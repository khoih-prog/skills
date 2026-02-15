/**
 * 통합 매매 실행자 (tradeExecutor.js)
 * - 리스크 관리 확인
 * - 주문 실행 및 상태 전이 (PositionsRepo 활용)
 */

const { Logger } = require('./upbitClient');
const riskManager = require('../risk/riskManager');
const positionsRepo = require('../state/positionsRepo');

class TradeExecutor {
    constructor(orderService, opts = {}) {
        this.orderService = orderService;
        this.dryRun = !!opts.dryRun;
    }

    async execute(event) {
        Logger.info(`[EXECUTOR] start type=${event.type} market=${event.market}`);

        // 1) Risk evaluation (may call Upbit chance/accounts)
        const riskResult = await riskManager.evaluate(this.orderService.client, event);
        if (!riskResult.allow) {
            Logger.warn(`[EXECUTOR] skip reason=${riskResult.reason} detail=${riskResult.detail || ''}`);
            return { ok: false, disposition: 'SKIP', reason: riskResult.reason, detail: riskResult.detail || '' };
        }

        // 2) State transitions + order execution
        if (event.type === 'BUY_SIGNAL') {
            const data = await positionsRepo.load();
            if (data.positions.some(p => p.market === event.market && (p.state === 'OPEN' || p.state === 'ENTRY_PENDING'))) {
                Logger.warn(`[EXECUTOR] skip duplicate position market=${event.market}`);
                return { ok: false, disposition: 'SKIP', reason: 'DUPLICATE_POSITION' };
            }

            const pending = await positionsRepo.createEntryPending(event.market, event.meta?.strategy || 'unknown', riskResult.budgetKRW);

            const orderResult = this.dryRun
                ? { uuid: `dry_buy_${Date.now()}`, market: event.market, price: event?.payload?.price, volume: null }
                : await this.orderService.placeMarketBuy(event.market, riskResult.budgetKRW);

            Logger.info(this.dryRun
                ? `[EXECUTOR] DRYRUN buy uuid=${orderResult.uuid}`
                : `[EXECUTOR] buy placed uuid=${orderResult.uuid}`);

            await positionsRepo.updateToOpen(event.market, orderResult);
            return { ok: true, disposition: 'DONE', action: 'BUY', uuid: orderResult.uuid };
        }

        if (event.type === 'TARGET_HIT' || event.type === 'STOPLOSS_HIT' || event.type === 'TRAILING_STOP_HIT' || event.type === 'TAKEPROFIT_HARD') {
            await positionsRepo.updateToExitPending(event.market, event.type);

            const orderResult = this.dryRun
                ? { uuid: `dry_sell_${Date.now()}`, market: event.market, volume: riskResult.volume }
                : await this.orderService.placeMarketSell(event.market, riskResult.volume);

            Logger.info(this.dryRun
                ? `[EXECUTOR] DRYRUN sell uuid=${orderResult.uuid}`
                : `[EXECUTOR] sell placed uuid=${orderResult.uuid}`);

            await positionsRepo.updateToClosed(event.market, orderResult);
            return { ok: true, disposition: 'DONE', action: 'SELL', uuid: orderResult.uuid };
        }

        return { ok: false, disposition: 'SKIP', reason: 'UNKNOWN_EVENT_TYPE' };
    }
}

module.exports = TradeExecutor;
