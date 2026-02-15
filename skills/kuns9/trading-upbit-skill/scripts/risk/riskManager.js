/**
 * 리스크 관리 모듈 (riskManager.js)
 * - 잔고 확인 및 주문 가능 여부 판단
 * - 최소 주문 금액(min_total) 필터
 * - 사이징 정책
 */

const { Logger } = require('../execution/upbitClient');

class RiskManager {
    /**
     * 주문 실행 전 리스크 검증
     * @param {Object} upbitClient - UpbitClient 인스턴스
     * @param {Object} event - 처리하려는 이벤트
     */
    async evaluate(upbitClient, event) {
        try {
            // 1. 주문 가능 정보 조회 (orders/chance)
            const chance = await upbitClient.request('GET', '/orders/chance', {}, { market: event.market });

            const bidFee = parseFloat(chance.bid_fee);
            const askFee = parseFloat(chance.ask_fee);
            const krwBalance = parseFloat(chance.bid_account.balance);
            const minTotal = parseFloat(chance.market.bid.min_total); // 최소 주문 금액 (KRW)

            if (event.type === 'BUY_SIGNAL') {
                const budget = event.budgetKRW || 10000; // 기본 1만원 또는 설정값

                // 잔고 부족 확인
                if (krwBalance < budget) {
                    return { allow: false, reason: 'INSUFFICIENT_BALANCE', detail: `잔고부족: ${krwBalance.toLocaleString()} KRW` };
                }

                // 최소 주문 금액 미달 확인
                if (budget < minTotal) {
                    return { allow: false, reason: 'UNDER_MIN_TOTAL', detail: `최소주문금액 미달: ${budget} < ${minTotal}` };
                }

                return { allow: true, budgetKRW: budget, fee: bidFee };
            }

            if (event.type === 'TARGET_HIT' || event.type === 'STOPLOSS_HIT') {
                // 매도의 경우 보유 수량 확인 (accounts)
                const accounts = await upbitClient.request('GET', '/accounts');
                const currency = event.market.split('-')[1];
                const asset = accounts.find(a => a.currency === currency);

                if (!asset || parseFloat(asset.balance) <= 0) {
                    return { allow: false, reason: 'NO_ASSET_TO_SELL' };
                }

                return { allow: true, volume: asset.balance, fee: askFee };
            }

            return { allow: false, reason: 'UNKNOWN_EVENT_TYPE' };
        } catch (err) {
            Logger.error(`Risk Evaluation Failed: ${err.message}`);
            return { allow: false, reason: 'ERROR', detail: err.message };
        }
    }
}

module.exports = new RiskManager();
