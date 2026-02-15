/**
 * v13 worker patch: percent-based budget split across multiple BUY_SIGNALs.
 *
 * This is a drop-in worker implementation for file-based state:
 * - resources/events.json
 * - resources/positions.json
 *
 * It tries to load an Upbit client from common module paths and supports:
 * - placeMarketBuy(market, krwAmount) or marketBuy(market, krwAmount)
 * - placeMarketSell(market, volume) or marketSell(market, volume)
 * - accounts()/getAccounts()/listAccounts()
 */
const fs = require("fs");
const path = require("path");
const { computeSplitBudget } = require("../risk/budgetPolicy");

function ts() {
  const d = new Date();
  return `[${d.toLocaleString()}]`;
}
function log(...a) { console.log(ts(), "[UPBIT-CLIENT]", ...a); }
function warn(...a){ console.warn(ts(), "[UPBIT-WARN]", ...a); }
function err(...a){ console.error(ts(), "[UPBIT-ERR]", ...a); }

function projectRoot() { return path.resolve(__dirname, "..", ".."); }
function resourcesDir() { return path.join(projectRoot(), "resources"); }

function ensureResources() {
  const dir = resourcesDir();
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  const eventsFile = path.join(dir, "events.json");
  const positionsFile = path.join(dir, "positions.json");
  if (!fs.existsSync(eventsFile)) fs.writeFileSync(eventsFile, "[]\n", "utf8");
  if (!fs.existsSync(positionsFile)) fs.writeFileSync(positionsFile, JSON.stringify({ positions: [] }, null, 2) + "\n", "utf8");
  return { dir, eventsFile, positionsFile };
}
function readJson(p, fallback) { try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return fallback; } }
function writeJson(p, obj) { fs.writeFileSync(p, JSON.stringify(obj, null, 2) + "\n", "utf8"); }

function loadConfig() {
  const p = path.join(projectRoot(), "config.json");
  if (!fs.existsSync(p)) throw new Error("config.json not found in skill root");
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function loadUpbitClient(cfg) {
  const candidates = [
    "../data/upbitClient",
    "../data/api-client",
    "../data/apiClient",
    "../execution/upbitClient",
    "../execution/executor",
  ];
  for (const rel of candidates) {
    try {
      const mod = require(rel);
      if (typeof mod === "function") return mod(cfg);
      if (mod?.createClient) return mod.createClient(cfg);
      if (mod?.client) return mod.client;
      return mod;
    } catch {}
  }
  throw new Error("Upbit client module not found. Adapt loadUpbitClient() paths.");
}

async function getAccounts(client) {
  if (typeof client.accounts === "function") return await client.accounts();
  if (typeof client.getAccounts === "function") return await client.getAccounts();
  if (typeof client.listAccounts === "function") return await client.listAccounts();
  throw new Error("Upbit client does not expose accounts/getAccounts/listAccounts");
}

function krwBalanceFromAccounts(accts) {
  const krw = (accts || []).find(a => (a.currency || a.code) === "KRW");
  const balStr = krw?.balance ?? krw?.available ?? krw?.free ?? "0";
  const n = Number(balStr);
  return Number.isFinite(n) ? n : 0;
}

async function main() {
  const start = Date.now();
  const { eventsFile, positionsFile } = ensureResources();
  log("[paths] resourcesDir=" + resourcesDir());
  log("[paths] eventsFile=" + eventsFile);
  log("[paths] positionsFile=" + positionsFile);

  const cfg = loadConfig();
  const policy = cfg?.trading?.budgetPolicy || { mode: "fixed" };

  const events = readJson(eventsFile, []);
  const pending = events.filter(e => !e.processed);
  const buyEventsAll = pending.filter(e => e.type === "BUY_SIGNAL");
  const sellEvents = pending.filter(e => e.type === "SELL_SIGNAL");

  log(`[worker] pendingEvents=${pending.length} buy=${buyEventsAll.length} sell=${sellEvents.length}`);

  const client = loadUpbitClient(cfg);

  // positions
  const posDoc = readJson(positionsFile, { positions: [] });
  posDoc.positions = Array.isArray(posDoc.positions) ? posDoc.positions : [];

  // budget split selection
  let perOrderKRW = null;
  let buyProcessCount = buyEventsAll.length;
  let availableKRW = null;

  if (policy?.mode === "balance_pct_split" && buyEventsAll.length > 0) {
    const accts = await getAccounts(client);
    availableKRW = krwBalanceFromAccounts(accts);
    const split = computeSplitBudget(availableKRW, buyEventsAll.length, policy);
    perOrderKRW = split.perOrderKRW;
    buyProcessCount = split.processCount;
    log(`[budget] mode=balance_pct_split availableKRW=${Math.floor(availableKRW)} usableKRW=${split.usableKRW} totalBudgetKRW=${split.totalBudget} buyCount=${buyEventsAll.length} processCount=${buyProcessCount} perOrderKRW=${perOrderKRW}`);
    if (buyProcessCount === 0) warn(`[budget] insufficient budget for minOrderKRW=${policy.minOrderKRW}; skipping all BUY events this run`);
  }

  function upsertPosition(market, krwSpent, uuid) {
    let p = posDoc.positions.find(x => x.market === market);
    if (!p) { p = { market }; posDoc.positions.push(p); }
    p.lastOrderUuid = uuid;
    p.lastBuyAt = new Date().toISOString();
    p.krwSpent = (Number(p.krwSpent) || 0) + (Number(krwSpent) || 0);
  }

  let processed = 0, skipped = 0, errors = 0;

  // BUY
  for (let i = 0; i < buyEventsAll.length; i++) {
    const e = buyEventsAll[i];
    e.attempts = (e.attempts || 0) + 1;
    e.lastAttemptAt = new Date().toISOString();

    let krwAmount = e.budgetKRW || cfg?.trading?.budgetKRW || 10000;
    if (policy?.mode === "balance_pct_split") {
      if (i >= buyProcessCount || !perOrderKRW || perOrderKRW <= 0) {
        e.processed = true;
        e.processedAt = new Date().toISOString();
        e.result = { action: "SKIP", reason: "INSUFFICIENT_BUDGET_FOR_SPLIT" };
        skipped++;
        continue;
      }
      krwAmount = perOrderKRW;
    }

    log(`[worker] PROCESS id=${e.id} type=${e.type} market=${e.market} attempts=${e.attempts} krw=${krwAmount}`);

    try {
      const buyFn = client.placeMarketBuy || client.marketBuy;
      if (typeof buyFn !== "function") throw new Error("Upbit client missing placeMarketBuy/marketBuy");
      const res = await buyFn.call(client, e.market, krwAmount);
      const uuid = res?.uuid || res?.result?.uuid || res?.data?.uuid;
      log(`[EXECUTOR] buy placed uuid=${uuid}`);

      upsertPosition(e.market, krwAmount, uuid);
      e.processed = true;
      e.processedAt = new Date().toISOString();
      e.result = { action: "BUY", uuid, krw: krwAmount, policy: policy?.mode || "fixed" };
      processed++;
    } catch (ex) {
      err(`[worker] ERROR id=${e.id} market=${e.market} msg=${ex?.message || ex}`);
      e.lastError = String(ex?.message || ex);
      errors++;
    }
  }

  // SELL (sell full amount if position has 'amount')
  for (const e of sellEvents) {
    e.attempts = (e.attempts || 0) + 1;
    e.lastAttemptAt = new Date().toISOString();

    const p = posDoc.positions.find(x => x.market === e.market);
    if (!p || !p.amount) {
      e.processed = true;
      e.processedAt = new Date().toISOString();
      e.result = { action: "SKIP", reason: "NO_POSITION" };
      skipped++;
      continue;
    }

    log(`[worker] PROCESS id=${e.id} type=${e.type} market=${e.market} attempts=${e.attempts} amount=${p.amount}`);

    try {
      const sellFn = client.placeMarketSell || client.marketSell;
      if (typeof sellFn !== "function") throw new Error("Upbit client missing placeMarketSell/marketSell");
      const res = await sellFn.call(client, e.market, p.amount);
      const uuid = res?.uuid || res?.result?.uuid || res?.data?.uuid;
      log(`[EXECUTOR] sell placed uuid=${uuid}`);

      e.processed = true;
      e.processedAt = new Date().toISOString();
      e.result = { action: "SELL", uuid };
      posDoc.positions = posDoc.positions.filter(x => x.market !== e.market);
      processed++;
    } catch (ex) {
      err(`[worker] ERROR id=${e.id} market=${e.market} msg=${ex?.message || ex}`);
      e.lastError = String(ex?.message || ex);
      errors++;
    }
  }

  writeJson(eventsFile, events);
  writeJson(positionsFile, posDoc);

  const dur = Date.now() - start;
  log(`[worker] pending=${pending.length} processed=${processed} skipped=${skipped} errors=${errors} positions=${posDoc.positions.length} durationMs=${dur}`);
  console.log(`${ts()} [UPBIT-CLIENT] SUMMARY worker pending=${pending.length} processed=${processed} skipped=${skipped} errors=${errors} positions=${posDoc.positions.length} durationMs=${dur}`);
}

main().catch(e => {
  console.error(ts(), "[UPBIT-ERR] Worker Fatal:", e?.stack || e);
  process.exit(1);
});
