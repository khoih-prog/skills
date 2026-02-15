const fs = require('fs');
const path = require('path');

function readJson(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8');
  return JSON.parse(raw);
}

function assertString(name, v) {
  if (typeof v !== 'string' || v.trim().length === 0) {
    throw new Error(`Invalid config: ${name} must be a non-empty string`);
  }
}

function assertNumber(name, v) {
  if (typeof v !== 'number' || Number.isNaN(v)) {
    throw new Error(`Invalid config: ${name} must be a number`);
  }
}

function assertArray(name, v) {
  if (!Array.isArray(v)) {
    throw new Error(`Invalid config: ${name} must be an array`);
  }
}

function assertBoolean(name, v) {
  if (typeof v !== 'boolean') {
    throw new Error(`Invalid config: ${name} must be a boolean`);
  }
}

function loadConfig() {
    const projectRoot = path.resolve(__dirname, '..', '..');
  const cfgPath = path.join(projectRoot, 'config.json');
    const examplePath = path.join(projectRoot, 'config.example.json');

  if (!fs.existsSync(cfgPath)) {
    const hint = fs.existsSync(examplePath)
      ? 'Create config.json based on config.example.json'
      : 'Create config.json in the skill root directory';
    throw new Error(`Missing config.json. ${hint}.`);
  }

  const cfg = readJson(cfgPath);

  // required
  assertString('upbit.accessKey', cfg?.upbit?.accessKey);
  assertString('upbit.secretKey', cfg?.upbit?.secretKey);

  // sections
  cfg.trading = cfg.trading || {};
  cfg.execution = cfg.execution || {};
  cfg.logging = cfg.logging || {};

  // defaults
  cfg.trading.watchlist = cfg.trading.watchlist || ['KRW-BTC', 'KRW-ETH', 'KRW-SOL'];
  assertArray('trading.watchlist', cfg.trading.watchlist);

  cfg.trading.scanIntervalMs = cfg.trading.scanIntervalMs ?? 300000;
  cfg.trading.priceCheckIntervalMs = cfg.trading.priceCheckIntervalMs ?? 10000;
  assertNumber('trading.scanIntervalMs', cfg.trading.scanIntervalMs);
  assertNumber('trading.priceCheckIntervalMs', cfg.trading.priceCheckIntervalMs);

  cfg.trading.targetProfit = cfg.trading.targetProfit ?? 0.05;
  cfg.trading.stopLoss = cfg.trading.stopLoss ?? -0.05;
  assertNumber('trading.targetProfit', cfg.trading.targetProfit);
  assertNumber('trading.stopLoss', cfg.trading.stopLoss);

  // optional: fixed buy budget in KRW (default: 10000)
  cfg.trading.budgetKRW = cfg.trading.budgetKRW ?? 10000;
  assertNumber('trading.budgetKRW', cfg.trading.budgetKRW);

  cfg.trading.volatilityBreakout = cfg.trading.volatilityBreakout || {};
  cfg.trading.volatilityBreakout.k = cfg.trading.volatilityBreakout.k ?? 0.5;
  assertNumber('trading.volatilityBreakout.k', cfg.trading.volatilityBreakout.k);

// breakout "near" threshold (candidate watch)
// If last/target >= breakoutNearThreshold, treat as a near-breakout candidate for logging (default: 0.98).
cfg.trading.breakoutNearThreshold = cfg.trading.breakoutNearThreshold ?? 0.98;
assertNumber('trading.breakoutNearThreshold', cfg.trading.breakoutNearThreshold);
if (cfg.trading.breakoutNearThreshold <= 0 || cfg.trading.breakoutNearThreshold > 1.5) {
  throw new Error('Invalid config: trading.breakoutNearThreshold must be > 0 and reasonably small (e.g., 0.98)');
}

// optional: emit WATCH_CANDIDATE events when near-breakout (default: false)
cfg.trading.emitWatchEvents = cfg.trading.emitWatchEvents ?? false;
assertBoolean('trading.emitWatchEvents', cfg.trading.emitWatchEvents);


  
// aggressive mode (more frequent entries/exits)
cfg.trading.aggressive = cfg.trading.aggressive || {};
cfg.trading.aggressive.enabled = cfg.trading.aggressive.enabled ?? false;
assertBoolean('trading.aggressive.enabled', cfg.trading.aggressive.enabled);

// entry: allow near-entry before full breakout (default 0.99)
cfg.trading.aggressive.entryNearThreshold = cfg.trading.aggressive.entryNearThreshold ?? 0.99;
assertNumber('trading.aggressive.entryNearThreshold', cfg.trading.aggressive.entryNearThreshold);

// momentum filter on 5-minute candles (default: last 3 candles, >=2 bullish)
cfg.trading.aggressive.momentumCandles = cfg.trading.aggressive.momentumCandles ?? 3;
cfg.trading.aggressive.momentumBullMin = cfg.trading.aggressive.momentumBullMin ?? 2;
assertNumber('trading.aggressive.momentumCandles', cfg.trading.aggressive.momentumCandles);
assertNumber('trading.aggressive.momentumBullMin', cfg.trading.aggressive.momentumBullMin);

// exits: tighter TP/SL + trailing stop
cfg.trading.aggressive.targetProfit = cfg.trading.aggressive.targetProfit ?? 0.02; // +2%
cfg.trading.aggressive.stopLoss = cfg.trading.aggressive.stopLoss ?? -0.02;       // -2%
cfg.trading.aggressive.takeProfitHard = cfg.trading.aggressive.takeProfitHard ?? 0.03; // +3% hard take
cfg.trading.aggressive.trailingActivateAt = cfg.trading.aggressive.trailingActivateAt ?? 0.01; // activate at +1%
cfg.trading.aggressive.trailingStop = cfg.trading.aggressive.trailingStop ?? 0.01; // 1% drawdown from peak
assertNumber('trading.aggressive.targetProfit', cfg.trading.aggressive.targetProfit);
assertNumber('trading.aggressive.stopLoss', cfg.trading.aggressive.stopLoss);
assertNumber('trading.aggressive.takeProfitHard', cfg.trading.aggressive.takeProfitHard);
assertNumber('trading.aggressive.trailingActivateAt', cfg.trading.aggressive.trailingActivateAt);
assertNumber('trading.aggressive.trailingStop', cfg.trading.aggressive.trailingStop);

// portfolio controls
cfg.trading.maxPositions = cfg.trading.maxPositions ?? 5;
assertNumber('trading.maxPositions', cfg.trading.maxPositions);

// scan universe
  // - 'watchlist' (default): scan only configured watchlist markets (fast, cron-friendly)
  // - 'allKrw': scan all KRW markets (slow; may hit rate limits)
  cfg.trading.scanUniverse = cfg.trading.scanUniverse || 'watchlist';
  if (!['watchlist', 'allKrw'].includes(cfg.trading.scanUniverse)) {
    throw new Error("Invalid config: trading.scanUniverse must be 'watchlist' or 'allKrw'");
  }


  // top volume markets (dynamic watchlist)
  // Adds top-N markets by 24h trade value or volume to the monitoring universe.
  cfg.trading.topVolume = cfg.trading.topVolume || {};
  cfg.trading.topVolume.enabled = cfg.trading.topVolume.enabled ?? false;
  assertBoolean('trading.topVolume.enabled', cfg.trading.topVolume.enabled);

  cfg.trading.topVolume.quote = cfg.trading.topVolume.quote || 'KRW';
  assertString('trading.topVolume.quote', cfg.trading.topVolume.quote);

  cfg.trading.topVolume.topN = cfg.trading.topVolume.topN ?? 10;
  assertNumber('trading.topVolume.topN', cfg.trading.topVolume.topN);

  cfg.trading.topVolume.metric = cfg.trading.topVolume.metric || 'acc_trade_price_24h';
  if (!['acc_trade_price_24h', 'acc_trade_volume_24h'].includes(cfg.trading.topVolume.metric)) {
    throw new Error("Invalid config: trading.topVolume.metric must be 'acc_trade_price_24h' or 'acc_trade_volume_24h'");
  }

  cfg.trading.topVolume.refreshMs = cfg.trading.topVolume.refreshMs ?? 300000;
  assertNumber('trading.topVolume.refreshMs', cfg.trading.topVolume.refreshMs);

  cfg.execution.eventPollIntervalMs = cfg.execution.eventPollIntervalMs ?? 5000;
  cfg.execution.dryRun = cfg.execution.dryRun ?? false;
  assertNumber('execution.eventPollIntervalMs', cfg.execution.eventPollIntervalMs);

  cfg.logging.level = cfg.logging.level || 'info';

  return cfg;
}

module.exports = { loadConfig };
