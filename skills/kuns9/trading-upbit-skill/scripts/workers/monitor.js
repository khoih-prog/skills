/**
 * 새 아키텍처 기반 모니터 (monitor.js)
 * - 포지션 실시간 감시 (State-Aware)
 * - 주기적 시장 스캔
 */

const { UpbitClient, Logger } = require('../execution/upbitClient');
const marketData = require('../data/marketData');
const positionsRepo = require('../state/positionsRepo');
const strategies = require('../strategies/strategies');
const fs = require('fs').promises;
const path = require('path');
const { loadConfig } = require('../config');
const { ensureResources, getResourcePaths } = require('../state/resources');
const { acquireLock, releaseLock } = require('../state/lock');

const cfg = loadConfig();
const ACCESS_KEY = cfg.upbit.accessKey;
const SECRET_KEY = cfg.upbit.secretKey;
const EVENTS_FILE = getResourcePaths().eventsFile;
const TOPVOL_CACHE_FILE = getResourcePaths().topVolumeCacheFile;
const NEAR_COUNTER_FILE = getResourcePaths().nearCounterFile;
const HEARTBEAT_FILE = getResourcePaths().heartbeatFile;
const MONITOR_LOCK_FILE = getResourcePaths().monitorLockFile;
const IS_DEBUG = (cfg.logging?.level || 'info').toLowerCase() === 'debug';

const CONFIG = {
    priceCheckInterval: cfg.trading.priceCheckIntervalMs,
    scanInterval: cfg.trading.scanIntervalMs,
    watchlist: cfg.trading.watchlist,
    targetProfit: cfg.trading.targetProfit,
    stopLoss: cfg.trading.stopLoss,
    k: cfg.trading.volatilityBreakout.k,
    scanUniverse: cfg.trading.scanUniverse,
    topVolume: cfg.trading.topVolume,
    breakoutNearThreshold: cfg.trading.breakoutNearThreshold,
    emitWatchEvents: cfg.trading.emitWatchEvents,
    excludeMarkets: cfg.trading.excludeMarkets || [],
    lockTtlMs: cfg.trading.monitorLockTtlMs || 120000,
};

const client = new UpbitClient(ACCESS_KEY, SECRET_KEY);
let lastScanTime = 0;

async function readNearCounter() {
    await ensureResources();
    const raw = await fs.readFile(NEAR_COUNTER_FILE, 'utf8').catch(() => null);
    if (!raw) return { updatedAt: 0, counts: {} };
    try { return JSON.parse(raw); } catch { return { updatedAt: 0, counts: {} }; }
}

async function writeNearCounter(obj) {
    await ensureResources();
    await fs.writeFile(NEAR_COUNTER_FILE, JSON.stringify(obj, null, 2), 'utf8');
}

async function writeHeartbeat(summary) {
    await ensureResources();
    let prev = {};
    try {
        const raw = await fs.readFile(HEARTBEAT_FILE, 'utf8');
        prev = JSON.parse(raw);
    } catch {
        prev = {};
    }
    const payload = {
        ...prev,
        lastRunAt: new Date().toISOString(),
        lastSummary: summary,
    };
    await fs.writeFile(HEARTBEAT_FILE, JSON.stringify(payload, null, 2), 'utf8');
}

async function updateHeartbeat(fields) {
    await ensureResources();
    let prev = {};
    try {
        const raw = await fs.readFile(HEARTBEAT_FILE, 'utf8');
        prev = JSON.parse(raw);
    } catch {
        prev = {};
    }
    const payload = {
        ...prev,
        ...fields,
    };
    await fs.writeFile(HEARTBEAT_FILE, JSON.stringify(payload, null, 2), 'utf8');
}

async function addEvent(event) {
    try {
        const _paths = await ensureResources();
        Logger.info(`[paths] projectRoot=${_paths.dir.replace(/\\resources$/, '')} resourcesDir=${_paths.dir}`);
        const data = await fs.readFile(EVENTS_FILE, 'utf8').catch(() => '[]');
        const events = JSON.parse(data);
        const dedupeKey = `${event.type}:${event.market}`;

        // 1시간 내 동일 마켓 동일 타입 이벤트 중복 방지
        const hourAgo = Date.now() - 3600000;
        if (events.some(e => e.dedupeKey === dedupeKey && new Date(e.createdAt).getTime() > hourAgo && !e.processed)) {
            return;
        }

        events.push({
            id: `evt_${Date.now()}`,
            ...event,
            dedupeKey,
            processed: false,
            createdAt: new Date().toISOString()
        });
        await fs.writeFile(EVENTS_FILE, JSON.stringify(events, null, 2));
        Logger.warn(`📢 이벤트 등록: ${event.type} - ${event.market}`);
    } catch (err) {
        Logger.error(`Event Save Error: ${err.message}`);
    }
}


async function readTopVolCache() {
    await ensureResources();
    const raw = await fs.readFile(TOPVOL_CACHE_FILE, 'utf8').catch(() => null);
    if (!raw) return { updatedAt: 0, markets: [] };
    try { return JSON.parse(raw); } catch { return { updatedAt: 0, markets: [] }; }
}

async function writeTopVolCache(obj) {
    await ensureResources();
    await fs.writeFile(TOPVOL_CACHE_FILE, JSON.stringify(obj, null, 2), 'utf8');
}

async function getTopVolumeMarkets() {
    const tv = CONFIG.topVolume || {};
    if (!tv.enabled) return [];

    const now = Date.now();
    const cache = await readTopVolCache();
    if (cache.updatedAt && (now - cache.updatedAt) < (tv.refreshMs || 300000) && Array.isArray(cache.markets) && cache.markets.length > 0) {
        return cache.markets;
    }

    // 1) load markets (quote filter)
    const all = await marketData.getMarkets(false);
    const quote = (tv.quote || 'KRW').toUpperCase();
    const markets = all.map(m => m.market).filter(m => m.startsWith(`${quote}-`));

    // 2) fetch tickers in batches (Upbit supports multiple markets per call; keep it safe)
    const metric = tv.metric || 'acc_trade_price_24h';
    const batchSize = 100;
    let tickers = [];
    for (let i = 0; i < markets.length; i += batchSize) {
        const part = markets.slice(i, i + batchSize);
        const res = await marketData.getTickers(part);
        if (Array.isArray(res)) tickers = tickers.concat(res);
    }

    // 3) sort & pick topN
    const topN = Math.max(1, Math.floor(tv.topN || 10));
    const ranked = tickers
        .filter(t => typeof t?.[metric] === 'number')
        .sort((a, b) => b[metric] - a[metric])
        .slice(0, topN)
        .map(t => t.market);

    const excluded = new Set((CONFIG.excludeMarkets || []).map(String));
    const filteredRanked = ranked.filter(m => !excluded.has(m));

    await writeTopVolCache({ updatedAt: now, quote, metric, topN, markets: filteredRanked });
    Logger.info(`🏆 [TopVolume] refreshed (quote=${quote}, metric=${metric}, topN=${topN}) -> ${filteredRanked.join(', ')}`);
    return filteredRanked;
}

async function scanMarkets(priceMapHint = {}, scanList = null, openMarkets = new Set(), openCount = 0) {
    Logger.info(`🔍 시장 스캔 시작... (universe=${CONFIG.scanUniverse})`);
    try {
        const markets = (CONFIG.scanUniverse === 'allKrw')
            ? await marketData.getMarkets(true)
            : (Array.isArray(scanList) && scanList.length > 0
                ? scanList.map(market => ({ market }))
                : CONFIG.watchlist.map(market => ({ market })));

        const excluded = new Set((CONFIG.excludeMarkets || []).map(String));

        let scanned = 0;
        let breakoutCandidates = 0;
        let nearCandidates = 0;
        let nearBull = 0;
        let breakoutBull = 0;
        let signals = 0;

        const nearCounter = await readNearCounter();
        const counts = nearCounter.counts || {};

        // track which markets were seen in this scan
        const seen = new Set();

        for (const m of markets) {
            if (excluded.has(m.market)) continue;
            scanned += 1;
            seen.add(m.market);
            // 전략 체크 로직 (Day + 60m 확인)
            // (기존 monitor.js 로직 재활용)
            const dayCandles = await marketData.getCandles('days', m.market, 2);
            if (dayCandles.length < 2) continue;

            const current = {
                open: dayCandles[0].opening_price,
                high: dayCandles[0].high_price,
                low: dayCandles[0].low_price,
                close: (priceMapHint[m.market] ?? dayCandles[0].trade_price)
            };
            const range = dayCandles[1].high_price - dayCandles[1].low_price;

            const result = strategies.volatilityBreakout(current, range, CONFIG.k);
            const last = current.close;
            const target = result.targetPrice;
            const ratio = (typeof target === 'number' && target > 0) ? (last / target) : 0;
            const breakout = (result.signal === 'BUY');
            const aggressive = !!cfg.trading?.aggressive?.enabled;
            const entryNearTh = aggressive ? (cfg.trading.aggressive.entryNearThreshold ?? 0.99) : CONFIG.breakoutNearThreshold;
            const near = (!breakout && ratio >= entryNearTh);

            // momentum filter (aggressive): 5-minute candles
let momentumOk = true;
if (cfg.trading?.aggressive?.enabled && (breakout || near || ratio >= cfg.trading.aggressive.entryNearThreshold)) {
    momentumOk = false;
    const mc = Math.max(2, Math.min(10, cfg.trading.aggressive.momentumCandles || 3));
    const mb = Math.max(1, Math.min(mc, cfg.trading.aggressive.momentumBullMin || 2));
    const m5 = await marketData.getCandles('minutes', m.market, mc, 5);
    if (Array.isArray(m5) && m5.length > 0) {
        const bull = m5.filter(c => c.trade_price > c.opening_price).length;
        momentumOk = bull >= mb;
    }
}

// Only fetch 60m candle for candidates to reduce API calls

            let oneHourBull = false;
            if (breakout || near) {
                const sub = await marketData.getCandles('minutes', m.market, 1, 60);
                oneHourBull = Array.isArray(sub) && sub[0] ? (sub[0].trade_price > sub[0].opening_price) : false;
            }

            if (breakout || near) breakoutCandidates += 1;
            if (near) {
                nearCandidates += 1;
                counts[m.market] = (counts[m.market] || 0) + 1;
                if (oneHourBull) nearBull += 1;
            } else {
                // reset if not near
                counts[m.market] = 0;
            }

            if (breakout && oneHourBull) breakoutBull += 1;

            if (IS_DEBUG) {
                Logger.info(
                    `  [scan] ${m.market} last=${Number(last).toLocaleString()} ` +
                    `target=${Number(target).toLocaleString()} ratio=${ratio.toFixed(4)} ` +
                    `breakout=${breakout} near=${near} 1hBull=${oneHourBull}` + (cfg.trading?.aggressive?.enabled ? ` momentumOk=${momentumOk}` : ``)
                );
            } else if (breakout || near) {
                // In info level, only show candidates (breakout or near-breakout)
                Logger.info(
                    `  [candidate] ${m.market} last=${Number(last).toLocaleString()} ` +
                    `target=${Number(target).toLocaleString()} ratio=${ratio.toFixed(4)} ` +
                    `breakout=${breakout} near=${near} 1hBull=${oneHourBull}` + (cfg.trading?.aggressive?.enabled ? ` momentumOk=${momentumOk}` : ``)
                );
            }


            if (near && CONFIG.emitWatchEvents) {
                await addEvent({
                    type: 'WATCH_CANDIDATE',
                    market: m.market,
                    payload: { price: last, targetPrice: target, ratio },
                    meta: { reason: 'NEAR_BREAKOUT', breakoutNearThreshold: CONFIG.breakoutNearThreshold }
                });
            }

// BUY decision (aggressive mode)
// Base: breakout + 1hBull
// Aggressive: near-entry (ratio>=entryNearThreshold) + momentumOk + 1hBull
const wantEntry = (breakout) || (aggressive && near && momentumOk);
if (wantEntry) {
    // portfolio cap / duplicate guard
    if (openMarkets.has(m.market)) {
        if (IS_DEBUG) Logger.info(`  [scan] ${m.market} already has an open/pending position (skip)`);
    } else if (openCount >= (cfg.trading.maxPositions || 5)) {
        Logger.warn(`  [scan] ${m.market} maxPositions reached (${openCount}) - skip`);
    } else if (!oneHourBull) {
        if (IS_DEBUG) Logger.info(`  [scan] ${m.market} entryCandidate but 1hBull=false (skip)`);
    } else {
        await addEvent({
            type: 'BUY_SIGNAL',
            market: m.market,
            budgetKRW: cfg.trading.budgetKRW,
            payload: { price: current.close, targetPrice: result.targetPrice, ratio, breakout, near, momentumOk },
            meta: { strategy: aggressive ? 'AggressiveBreakout' : 'VolatilityBreakout' }
        });
        signals += 1;
        Logger.warn(`EVENT BUY_SIGNAL ${JSON.stringify({ market: m.market, price: current.close, targetPrice: result.targetPrice, ratio: Number(ratio.toFixed(4)), breakout, near, momentumOk })}`);
        openCount += 1;
        openMarkets.add(m.market);
    }
}

        }

        // Reset counters for markets not seen this scan (optional hygiene)
        for (const key of Object.keys(counts)) {
            if (!seen.has(key)) counts[key] = 0;
        }

        await writeNearCounter({ updatedAt: Date.now(), counts });

        const summary = {
            scanned,
            breakoutCandidates,
            nearCandidates,
            nearBull,
            breakoutBull,
            signals,
        };
        Logger.info(`시장 스캔 완료 (scanned=${scanned}, breakoutCandidates=${breakoutCandidates}, near=${nearCandidates}, nearBull=${nearBull}, breakoutBull=${breakoutBull}, signals=${signals})`);
        // Always write heartbeat so operators can verify cron execution
        await writeHeartbeat(summary);

        // Last line: stable summary for OpenClaw run history
        Logger.info(`SUMMARY scanned=${scanned} breakoutCandidates=${breakoutCandidates} near=${nearCandidates} nearBull=${nearBull} breakoutBull=${breakoutBull} signals=${signals}`);
    } catch (err) {
        Logger.error(`Scan Error: ${err.message}`);
    }
}

async function monitor() {
    try {
        await ensureResources();
        const data = await positionsRepo.load();
        const positions = (data.positions || []).filter(p => p.state === 'OPEN');

        // optional hint map for scanMarkets to avoid extra price calls
        const priceMap = {};

        // 시세 실시간 출력
        const topVolMarkets = await getTopVolumeMarkets();
        const monitorHoldings = (cfg.trading.monitorHoldings ?? true);
        const base = [
            ...(monitorHoldings ? positions.map(p => p.market) : []),
            ...CONFIG.watchlist,
            ...topVolMarkets
        ];
        const excluded = new Set((CONFIG.excludeMarkets || []).map(String));
        const combined = [...new Set(base)].filter(m => !excluded.has(m));
        const combinedToScan = combined;
        if (combined.length > 0) {
            const tickers = await marketData.getTickers(combined);
            // Keep identifiers ASCII-only to avoid runtime issues across environments
            tickers.forEach(t => { priceMap[t.market] = t.trade_price; });

            Logger.info(`👀 [Watch] ${CONFIG.watchlist.map(m => `${m.split('-')[1]}: ${priceMap[m]?.toLocaleString()}`).join(' | ')}`);

            await updateHeartbeat({
                lastWatchAt: new Date().toISOString(),
                lastWatch: CONFIG.watchlist.reduce((acc, m) => {
                    acc[m] = priceMap[m] ?? null;
                    return acc;
                }, {})
            });

            if ((CONFIG.topVolume?.enabled) && topVolMarkets.length > 0) {
                const tv = CONFIG.topVolume;
                Logger.info(`🏆 [TopVolume] ${tv.metric || 'acc_trade_price_24h'} Top${tv.topN || topVolMarkets.length}: ${topVolMarkets.map(m => m.split('-')[1]).join(', ')}`);
            }


            for (const pos of positions) {
                const current = priceMap[pos.market];
                if (!current) continue;
                const entry = pos.entry.avgFillPrice;
                const pnl = (current - entry) / entry;
                Logger.info(`💰 [Hold] ${pos.market}: ${current.toLocaleString()}원 (${(pnl * 100).toFixed(2)}%)`);

// Exit logic
if (cfg.trading?.aggressive?.enabled) {
    const ag = cfg.trading.aggressive;
    const tpHard = ag.takeProfitHard ?? 0.03;
    const tp = ag.targetProfit ?? 0.02;
    const sl = ag.stopLoss ?? -0.02;
    const actAt = ag.trailingActivateAt ?? 0.01;
    const tStop = ag.trailingStop ?? 0.01;

    // update peak price & activate trailing if conditions met
    if (pnl >= actAt) {
        await positionsRepo.updatePeak(pos.market, current, { activate: true });
    } else {
        await positionsRepo.updatePeak(pos.market, current, { activate: false });
    }

    // reload position to read peak/trailingActive (cheap local file read)
    const latest = await positionsRepo.load();
    const p2 = (latest.positions || []).find(p => p.market === pos.market && p.state === 'OPEN');
    const peak = Number(p2?.exit?.peakPrice || current);
    const trailingActive = !!p2?.exit?.trailingActive;

    if (pnl >= tpHard) {
        await addEvent({ type: 'TAKEPROFIT_HARD', market: pos.market });
    } else if (trailingActive && peak > 0) {
        const drawdown = (peak - current) / peak;
        if (drawdown >= tStop && pnl >= tp) {
            await addEvent({ type: 'TRAILING_STOP_HIT', market: pos.market, meta: { peakPrice: peak, drawdown } });
        }
    } else if (pnl <= sl) {
        await addEvent({ type: 'STOPLOSS_HIT', market: pos.market });
    }
} else {
    if (pnl >= CONFIG.targetProfit) {
        await addEvent({ type: 'TARGET_HIT', market: pos.market });
    } else if (pnl <= CONFIG.stopLoss) {
        await addEvent({ type: 'STOPLOSS_HIT', market: pos.market });
    }
}

            }
        }

        if (Date.now() - lastScanTime > CONFIG.scanInterval) {
            await scanMarkets(priceMap, combinedToScan, new Set(positions.map(p => p.market)), positions.length);
            lastScanTime = Date.now();
        }
    } catch (err) {
        Logger.error(`Monitor Error: ${err.message}`);
    }
}

async function monitorOnce() {
    const _paths = await ensureResources();
    Logger.info(`[paths] projectRoot=${_paths.dir.replace(/\resources$/, '')} resourcesDir=${_paths.dir}`);

    // prevent overlapping runs
    const lock = await acquireLock(MONITOR_LOCK_FILE, CONFIG.lockTtlMs, { kind: 'monitor' });
    if (!lock.ok) {
        Logger.warn(`LOCKED monitor (ageMs=${lock.ageMs}) - skip`);
        return;
    }
    const started = Date.now();
    try {
        await monitor();
        const dur = Date.now() - started;
        Logger.info(`DURATION monitorMs=${dur}`);
    } finally {
        await releaseLock(MONITOR_LOCK_FILE);
    }
}

function monitorLoop() {
    (async function loop() {
        await monitor();
        setTimeout(loop, CONFIG.priceCheckInterval);
    })();
}

module.exports = { monitorOnce, monitorLoop };

if (require.main === module) {
    Logger.info('🚀 Monitor Engine Started');
    monitorLoop();
}