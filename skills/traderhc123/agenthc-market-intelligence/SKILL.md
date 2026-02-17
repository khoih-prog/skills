---
name: agenthc-market-intelligence
description: Real-time stock market data and trading intelligence API. 47 modules — equities, bonds, crypto, bitcoin, macro economics, Fed policy, treasury yields, VIX, options flow, sector rotation, and technical analysis. Finance data for AI agents with Bitcoin Lightning micropayments.
homepage: https://api.traderhc.com/docs
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env: ["AGENTHC_API_KEY"]
      bins: ["curl", "jq", "python3"]
    primaryEnv: "AGENTHC_API_KEY"
---

# Stock Market Intelligence

Institutional-grade market intelligence API for AI agents. 47 modules covering equities, bonds, crypto, macro, Fed, liquidity, regime detection, alpha signals, options flow, and more. Bitcoin Lightning micropayments. Built by @traderhc.

## Setup

### For AI Agents (copy-paste, zero friction)

```bash
export AGENTHC_API_KEY=$(curl -s -X POST "https://api.traderhc.com/api/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d '{"name": "MyAgent"}' | jq -r '.api_key')
```

That's it. One command. Free, no KYC, no credit card. Now query any free module:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### For Humans (interactive setup)

```bash
bash scripts/setup.sh
```

Walks you through registration and prints your API key.

### Non-Interactive (CI/scripts)

```bash
export AGENTHC_API_KEY=$(bash scripts/setup.sh --auto)
```

## Free Modules (no payment required)

### Market Intelligence
Real-time market snapshot: S&P 500, VIX, treasury yields, DXY, commodities, sector performance, Fear & Greed, and market regime.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Educational Content
Trading concepts, historical lessons, and market psychology frameworks.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/educational_content" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Polymarket Intelligence
Fed/FOMC prediction markets, recession odds, crypto price predictions, political/regulatory odds.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/polymarket_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Premium Modules (100 sats/query)

These require Premium tier. Upgrade with Lightning payment or use L402 per-request payment.

### Technical Analysis
RSI, MACD, Bollinger Bands, support/resistance, volume analysis for any ticker.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/technical_analysis?ticker=AAPL" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Bond Intelligence
Treasury yields, yield curve dynamics, credit spreads, duration risk.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/bond_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Fed Intelligence
Fed balance sheet, FOMC calendar, ISM PMI, yield curve analysis, RRP/repo, liquidity trends.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/fed_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Macro Intelligence
CPI, PCE, NFP, unemployment, M2, credit spreads, ISM Services, consumer sentiment, housing.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/macro_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Correlation Tracker
18+ cross-market correlation pairs with anomaly detection and regime classification.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/correlation_tracker" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Volatility Analyzer
VIX regime classification, term structure, VVIX, implied vs realized vol.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/volatility_analyzer" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Volatility Surface
VIX ecosystem (VIX, VIX9D, VIX3M, VIX6M, VVIX), term structure, skew analysis, vol regime detection.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/volatility_surface" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Crypto Intelligence
Bitcoin, Ethereum, BTC dominance, halving cycle, alt season detection, crypto Fear & Greed.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/crypto_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Options Intelligence
Options open interest, volume, gamma exposure from OCC public data (T+1).

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/options_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### CME FedWatch
Fed rate probability expectations from CME FedWatch proxy.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/cme_fedwatch" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Institutional Modules (500 sats/query)

### Alpha Signals
Systematic multi-factor signal composite: momentum, mean reversion, carry, value, volatility, flow, macro.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/alpha_signals" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Regime Engine
12 market regimes with transition probabilities, leading indicators, historical analogues.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/regime_engine" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Tail Risk Engine
Crisis detection with 12 crisis types, early warning indicators, historical playbooks, composite tail risk score.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/tail_risk_engine" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Liquidity Intelligence
Fed net liquidity (Balance Sheet - TGA - RRP), liquidity regime, bank stress signals.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/liquidity_intelligence" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Credit Cycle
HY/IG/BBB/CCC spreads, lending standards, default indicators, credit cycle phase, financial conditions.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/credit_cycle" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

### Institutional Positioning
CFTC COT data, AAII sentiment, NAAIM exposure, put/call ratios, crowded trade detection.

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/institutional_positioning" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.data'
```

## Agent-Optimized Format

For AI agents, use `format=agent` to get actionable signals with direction, confidence, urgency, and delta tracking:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence?format=agent" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.signals'
```

Response includes:
- `signals.direction` — bullish/bearish/neutral/mixed
- `signals.confidence` — 0.0 to 1.0
- `signals.urgency` — low/medium/high/critical
- `signals.actionable` — true if action recommended
- `suggested_actions` — related modules to query next
- `delta` — what changed since your last query

## Compact Format (Token-Efficient)

Use `format=compact` for 60% fewer tokens in your context window:

```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/market_intelligence?format=compact" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
```

## Batch Queries (Premium+)

Query multiple modules in one request:

```bash
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["market_intelligence", "bond_intelligence", "fed_intelligence"]}' | jq '.'
```

## Real-Time Events (Webhooks)

Subscribe to 20+ market event types via webhooks with HMAC-SHA256 signatures:

- Regime changes, VIX spikes, flash crashes
- Correlation breaks, credit stress spikes
- Alpha signal flips, tail risk alerts
- Breaking news, unusual options activity
- Fed rate probability shifts

## Lightning Payment (L402)

For per-request payment without registration:

1. Request a premium endpoint without auth
2. Receive 402 response with BOLT11 Lightning invoice + macaroon
3. Pay the invoice (any Lightning wallet)
4. Re-request with `Authorization: L402 <macaroon>:<preimage>`
5. Token valid for 24 hours — reuse across requests

## MCP Integration

Connect via Model Context Protocol (streamable-http transport):

```
Endpoint: https://api.traderhc.com/mcp
Protocol: 2025-03-26
Tools: 28
```

## All 47 Modules

| Module | Tier | Description |
|--------|------|-------------|
| market_intelligence | Free | Market snapshot, regime, Fear & Greed |
| educational_content | Free | Trading concepts, historical lessons |
| polymarket_intelligence | Free | Prediction market odds |
| technical_analysis | Premium | TA for any ticker (RSI, MACD, etc.) |
| economic_calendar | Premium | Economic events, beat/miss |
| fed_intelligence | Premium | Fed balance sheet, FOMC, ISM |
| macro_intelligence | Premium | Inflation, employment, M2, credit |
| bond_intelligence | Premium | Yields, curve, credit spreads |
| correlation_tracker | Premium | Cross-market correlation anomalies |
| volatility_analyzer | Premium | VIX regime, term structure, VVIX |
| volatility_surface | Premium | VIX ecosystem, skew, IV vs RV |
| crypto_intelligence | Premium | BTC, ETH, dominance, halving cycle |
| credit_cycle | Premium | Credit cycle phase, spreads, financial conditions |
| sector_rotation | Premium | Business cycle sector rotation |
| intermarket_analysis | Premium | Stock/bond/dollar/commodity signals |
| earnings_calendar | Premium | Upcoming earnings, reactions |
| news_sentiment | Premium | Breaking news with sentiment scoring |
| smart_money_tracker | Premium | Smart vs dumb money divergence |
| divergence_detection | Premium | Price/breadth/volume divergences |
| market_structure | Premium | Breadth, A/D, McClellan |
| exchange_stats | Premium | Market breadth, advance/decline |
| cme_fedwatch | Premium | Fed rate probability expectations |
| options_intelligence | Premium | OCC options OI, volume, gamma |
| alpha_signals | Institutional | Multi-factor signal composite |
| regime_engine | Institutional | 12 market regimes, transitions |
| tail_risk_engine | Institutional | Crisis detection, early warnings |
| liquidity_intelligence | Institutional | Fed net liquidity, regime |
| hedge_fund_playbooks | Institutional | 20+ institutional setups |
| institutional_positioning | Institutional | COT, sentiment, smart money |
| currency_intelligence | Institutional | DXY, carry trades, FX |
| factor_analysis | Institutional | Factor rotation, crowding |
| trend_exhaustion_scanner | Institutional | Trend exhaustion signals |
| advanced_risk | Institutional | Kelly, VaR, drawdown protocols |
| valuation_intelligence | Institutional | CAPE, Buffett indicator, ERP |
| global_flows | Institutional | Dollar cycle, capital rotation |
| geopolitical_risk | Institutional | Risk scoring, hedging |
| central_bank_dashboard | Institutional | All major central banks |
| market_microstructure | Institutional | Gamma, vanna, dealer positioning |
| narrative_tracker | Institutional | Market narrative lifecycle |
| wealth_knowledge | Institutional | Legendary investor wisdom |
| institutional_content | Institutional | Viral FinTwit content |
| market_knowledge | Institutional | Deep market knowledge base |
| sentiment_engine | Institutional | Multi-source sentiment |
| sec_edgar | Institutional | SEC insider filings |
| intelligence_service | Institutional | AI synthesis /ask endpoint |
| historical_parallels | Institutional | Historical analogue engine |
| agent_consensus | Institutional | Agent attention signal |

## Pricing

- **Free**: 3 modules, 10/min, 100/day
- **Premium**: 23 modules, 60/min, 5,000/day, 100 sats/query (~$0.10)
- **Institutional**: All 47 modules, 120/min, 50,000/day, 500 sats/query (~$0.50)

Payment via Bitcoin Lightning Network. Instant settlement, no KYC.

## Example Workflows

### Morning Market Brief
```bash
# Get market overview + bonds + macro + crypto in one batch
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["market_intelligence", "bond_intelligence", "macro_intelligence", "crypto_intelligence"]}' | jq '.results'
```

### Risk Check
```bash
# Check tail risk + volatility + correlations
curl -s -X POST "https://api.traderhc.com/api/v1/intelligence/batch" \
  -H "X-API-Key: $AGENTHC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"modules": ["tail_risk_engine", "volatility_analyzer", "correlation_tracker"]}' | jq '.results'
```

### Ticker Deep Dive
```bash
curl -s "https://api.traderhc.com/api/v1/intelligence/technical_analysis?ticker=NVDA&format=agent" \
  -H "X-API-Key: $AGENTHC_API_KEY" | jq '.'
```

## Disclaimer

All data and analysis is for educational and informational purposes only. Not financial advice. Not a registered investment advisor. Always do your own research.
