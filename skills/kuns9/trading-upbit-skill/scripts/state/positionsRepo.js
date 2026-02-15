const fs = require('fs').promises;
const { getResourcePaths, ensureResources } = require('./resources');

/**
 * Positions repository
 * - Manages position state machine:
 *   FLAT -> ENTRY_PENDING -> OPEN -> EXIT_PENDING -> CLOSED
 */

const POSITIONS_FILE = getResourcePaths().positionsFile;

class PositionsRepo {
  async load() {
    await ensureResources().catch(() => {});
    try {
      const data = await fs.readFile(POSITIONS_FILE, 'utf8');
      const parsed = JSON.parse(data);
      if (!parsed || typeof parsed !== 'object') return { positions: [] };
      if (!Array.isArray(parsed.positions)) parsed.positions = [];
      return parsed;
    } catch {
      return { positions: [] };
    }
  }

  async save(data) {
    await ensureResources().catch(() => {});
    await fs.writeFile(POSITIONS_FILE, JSON.stringify(data, null, 2), 'utf8');
  }

  async createEntryPending(market, strategy, budget) {
    const data = await this.load();
    const newPos = {
      id: `pos_${Date.now()}`,
      market,
      state: 'ENTRY_PENDING',
      entry: { budgetKRW: budget, createdAt: new Date().toISOString() },
      meta: { strategy },
    };
    data.positions.push(newPos);
    await this.save(data);
    return newPos;
  }

  async updateToOpen(market, orderResult) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'ENTRY_PENDING');
    if (!pos) return;
    pos.state = 'OPEN';
    pos.entry.orderUuid = orderResult.uuid;
    pos.entry.avgFillPrice = Number(orderResult.price || 0);
    pos.entry.openedAt = new Date().toISOString();

    // trailing state
    pos.exit = pos.exit || {};
    const base = Number(pos.entry.avgFillPrice || 0);
    pos.exit.peakPrice = Number.isFinite(Number(pos.exit.peakPrice)) ? pos.exit.peakPrice : base;
    pos.exit.trailingActive = !!pos.exit.trailingActive;

    await this.save(data);
  }

  async updatePeak(market, currentPrice, opts = {}) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'OPEN');
    if (!pos) return;

    pos.exit = pos.exit || {};
    const peak = Number(pos.exit.peakPrice || pos.entry?.avgFillPrice || 0);
    if (!Number.isFinite(peak) || peak <= 0) {
      pos.exit.peakPrice = currentPrice;
    } else if (currentPrice > peak) {
      pos.exit.peakPrice = currentPrice;
    }
    if (opts.activate === true) pos.exit.trailingActive = true;

    await this.save(data);
  }

  async updateToExitPending(market, reason) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'OPEN');
    if (!pos) return;
    pos.state = 'EXIT_PENDING';
    pos.exit = { ...(pos.exit || {}), reason, triggeredAt: new Date().toISOString() };
    await this.save(data);
  }

  async updateToClosed(market, orderResult) {
    const data = await this.load();
    const pos = data.positions.find(p => p.market === market && p.state === 'EXIT_PENDING');
    if (!pos) return;
    pos.state = 'CLOSED';
    pos.exit = { ...(pos.exit || {}), orderUuid: orderResult.uuid, closedAt: new Date().toISOString() };
    await this.save(data);
  }
}

module.exports = new PositionsRepo();
