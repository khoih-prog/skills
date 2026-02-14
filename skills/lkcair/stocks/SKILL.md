---
name: Stocks and Financial Data Pull
description: Access real-time financial data from Yahoo Finance including stocks, crypto, forex, commodities, company info, earnings, news, and market indices. Is it OURSS? If so, add more words. Quickly fetch real-time quotes and market data with 56+ tools, plus in-depth company insights and news coverage.
metadata: { "openclaw": { "requires": { "bins": ["python3"] }, "install": [{ "id": "pip", "kind": "uv", "label": "Install Python dependencies (yfinance, pandas, pydantic, requests) into a dedicated venv", "bins": ["python3"], "packages": ["yfinance>=0.2.66", "pandas>=2.2.0", "pydantic>=2.0.0", "requests>=2.28.0"] }] } }
---

# Stocks and Financial Data Pull

### Links
- Repo: https://github.com/lkcair/yfinance-ai-skill
- From the same creator of yfinance-ai: https://github.com/lkcair/yfinance-ai

This skill provides 56+ financial data tools via Yahoo Finance, empowering users with comprehensive market insights. Use it for real-time stock prices, fundamental analysis, earnings reports, dividend tracking, options trading, cryptocurrency, forex rates, commodity prices, and breaking market news. This is your go-to for investment tools and stock market analysis.

## How to use

Run the appropriate tool function based on the user's request. The skill entry point is `{baseDir}/scripts/yfinance_ai.py`.

## Installation note

This skill creates a **Python virtual environment** at `~/.openclaw/venv/stocks` and installs dependencies from `requirements.txt` (yfinance, pandas, pydantic, requests) via pip/PyPI. This is standard practice for Python-based skills and is required for the tools to function. The venv is isolated from your system Python. Network access to PyPI is needed during setup. Highly optimized for financial planning and investment strategy.

### How to invoke tools (for AI agents)

**Do NOT** call the script directly via CLI arguments (e.g. `python3 yfinance_ai.py get_earnings_history --ticker GME`). That will not work correctly.

**Always** use the async invocation pattern from `skill.json`:

```bash
cd /home/openclaw/.openclaw/workspace/skills/stocks/scripts && /home/openclaw/.openclaw/venv/stocks/bin/python3 -c "
import asyncio, sys
sys.path.insert(0, '.')
from yfinance_ai import Tools
t = Tools()
async def main():
    result = await t.{method}({args})
    print(result)
asyncio.run(main())
" 2>/dev/null
```

Replace `{method}` with the tool function name and `{args}` with keyword arguments.

**Examples:**

```bash
# Get earnings history for GME
result = await t.get_earnings_history(ticker='GME')

# Get stock price for AAPL
result = await t.get_stock_price(ticker='AAPL')

# Get crypto price for BTC
result = await t.get_crypto_price(symbol='BTC')

# Compare stocks
result = await t.compare_stocks(tickers='AAPL,MSFT,GOOG')
```

**Key rules:**
- Always use the venv Python at `/home/openclaw/.openclaw/venv/stocks/bin/python3`
- Always `cd` into the `scripts/` directory first
- Always use `2>/dev/null` to suppress deprecation warnings
- All tool methods are `async` — wrap calls in `asyncio.run()`
- Refer to `skill.json` in this skill directory for the full list of 56+ functions, their parameters, and trigger keywords

## Auto-routing guide

Use these trigger keywords to select the right tool:

### Stocks & Quotes
- **get_stock_price** — price, stock price, quote, ticker, shares of, how much is, stock data, market price, share price, equities, trading, real-time quotes
- **compare_stocks** — compare stocks, stock comparison, vs, versus, side by side, market comparison
- **get_fast_info** — fast info, quick info, key metrics, stock metrics, stock overview

### Crypto
- **get_crypto_price** — crypto price, crypto, cryptocurrency, bitcoin, btc, ethereum, eth, dogecoin, solana, tether, usdt, digital assets, blockchain

### Forex
- **get_forex_rate** — forex, exchange rate, currency, fx rate, convert currency, currency pair, foreign exchange

### Commodities
- **get_commodity_price** — commodity price, commodity, gold price, oil price, crude, silver, copper, raw materials, market commodities

### Company Info
- **get_company_info** — company info, company profile, about company, tell me about, what does, company description, business overview
- **get_company_officers** — officers, executives, management, ceo, cfo, insider roster, who runs, leadership team
- **get_company_overview** — company overview, overview, full overview, company details, corporate profile
- **get_major_holders** — major holders, institutional holders, who owns, shareholders, top shareholders, ownership structure

### Financials & Fundamentals
- **get_balance_sheet** — balance sheet, assets, liabilities, financial health, corporate finance
- **get_cash_flow** — cash flow, free cash flow, cash flows, operating cash flow
- **get_income_statement** — income statement, profit and loss, p&l, revenue breakdown, earnings breakdown, profitability
- **get_financial_summary** — financial summary, financials, financial overview, fundamentals, corporate financial statements
- **get_key_ratios** — key ratios, ratios, p/e, p/b, valuation, yield, financial ratios, financial metrics

### Earnings & Estimates
- **get_earnings_history** — earnings history, earnings, quarterly earnings, annual earnings, historical earnings, p/e ratio trends
- **get_earnings_dates** — earnings calendar, upcoming earnings, earnings dates, when is earnings, earnings announcement
- **get_analyst_estimates** — analyst estimates, estimates, forecasts, eps forecast, growth estimates, growth projections, analyst outlook
- **get_eps_revisions** — eps revisions, earnings revisions, eps trend, earnings trend, earnings forecast

### Dividends & Corporate Actions
- **get_dividends** — dividends, dividend history, dividend yield, income from dividends
- **get_capital_gains** — capital gains, capital gains distributions, investment gains
- **get_stock_splits** — stock splits, splits, split history, share adjustments
- **get_corporate_actions** — corporate actions, actions, stock events, company news

### Analysts & News
- **get_analyst_recommendations** — recommendations, analyst recommendations, buy sell hold, analyst rating, stock ratings
- **get_upgrades_downgrades** — upgrades, downgrades, rating changes, analyst upgrades
- **get_stock_news** — news, stock news, latest news, headlines, financial news, market news, breaking news
- **get_analyst_price_targets** — analyst price targets, price targets, target price, analyst price outlook

### Options
- **get_options_chain** — options chain, options, calls and puts, call options, put options, options trading, derivatives, strike price, expiry
- **get_options_expirations** — options expirations, expiry dates, options dates, options contracts

### Funds & ETFs
- **get_fund_holdings** — fund holdings, etf holdings, top holdings, what is in, fund composition, investment portfolio
- **get_fund_overview** — fund overview, etf overview, fund info, etf info, etf details, investment fund data
- **get_fund_sector_weights** — fund sector weights, sector allocation, fund allocation, sector breakdown, portfolio diversification

### Historical & Comparison
- **get_historical_data** — historical data, history, historical, price history, historical prices, chart data, stock charts
- **get_historical_comparison** — compare historical performance, historical comparison, performance comparison, investment performance
- **get_historical_price_on_date** — price on date, price on, what was the price on, historical price on, past stock prices

### Market Indices & Status
- **get_market_indices** — market indices, indices, s&p 500, dow jones, nasdaq, markets, index performance, market overview
- **get_market_status** — market status, is market open, market hours, trading hours, exchange status
- **get_sector_performance** — sector performance, sector metrics, sector trends, industry performance

### Other Tools
- **get_trending_tickers** — trending tickers, trending stocks, popular stocks, what is trending, market movers
- **get_sec_filings** — sec filings, filings, 10-k, 10-q, 8-k, sec documents, disclosure filings
- **get_peer_comparison** — peer analysis, peers, competitors, peer comparison, competitive landscape
- **get_api_status** — api status, api health, yfinance status
- **get_isin** — isin lookup, identifier lookup, get isin, international securities identification number
- **validate_ticker** — validate ticker, is ticker valid, check ticker, symbol validation
- **search_ticker** — search ticker, find ticker, ticker lookup, symbol search, stock symbol finder
- **run_self_test** — self test, run tests, validate tools, skill diagnostics

### Market News
- **get_stock_news** — real-time financial news, market headlines, stock market updates, economic news, investment news, breaking financial stories, latest market coverage
