---
name: capital-market-report
description: Generate comprehensive capital market briefings covering global indices (A-shares, Hong Kong stocks, US stocks), commodities (gold, oil, Bitcoin), and categorized news from Chinese and international financial media. Use when user requests "capital market briefing", "market report", "资本市场简报", "资本市场报告", or any request for market summary with stock indices, commodity prices, and financial news classification into bullish/bearish/neutral categories.
---

# Capital Market Report Skill

Generate professional capital market briefings with real-time data and categorized news.

## Workflow

### Step 1: Get Market Data

**A-shares, HK stocks, US stocks:**
```bash
uv run ~/.openclaw/skills/tencent-finance-stock-price/scripts/query_stock.py 上证指数 科创50 创业板指 恒生指数 恒生科技 标普500 纳指100
```

**Cryptocurrency (Bitcoin):**
```bash
uv run ~/.openclaw/workspace-group/skills/cryptoprice/scripts/cryptoprice.py BTC
```

**Gold & Oil:**
- Use web_fetch to get from Kitco or CNBC
- Gold: https://www.kitco.com/gold-price-today-usa/
- Oil: https://www.cnbc.com/quotes/@CL.1

### Step 2: Collect News (24-hour window)

**Chinese Media:**
- 36Kr: https://www.36kr.com/feed
- Sina Finance: https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=10
- People's Daily Finance: http://finance.people.com.cn/

**International Media:**
- BBC Business: https://feeds.bbci.co.uk/news/business/rss.xml
- Bloomberg: https://www.bloomberg.com/feeds/markets/sitemap_news.xml
- Yahoo Finance: https://finance.yahoo.com/news/rss
- WSJ Markets: https://feeds.a.dj.com/rss/RSSMarketsMain.xml
- Financial Times: https://www.ft.com/?format=rss

### Step 3: News Classification

**🟢 Bullish (利好):**
- Policy support / stimulus
- Strong earnings / guidance
- Market rallies / inflows
- M&A deals
- Positive economic data

**🔴 Bearish (利空):**
- Geopolitical conflicts
- Weak earnings / guidance cuts
- Market selloffs / outflows
- Regulatory tightening
- Economic slowdown signals

**⚪ Neutral (中性):**
- Executive changes
- Corporate restructuring
- Industry analysis
- Neutral policy announcements

### Step 4: Report Format

```
📊 Capital Market Briefing | YYYY-MM-DD HH:MM

---

### 🟢 Trading (Real-time Data)

**Commodities**
- Gold: $X,XXX/oz (+/-$X / +/-X%)
- Crude Oil (WTI): $XX.XX/barrel (+/-$X / +/-X%)
- Bitcoin: $XX,XXX

---

### 🔴 Market Closed

**A-shares (Last Close)**
- Shanghai Composite: X,XXX.XX pts (+/-X / +/-X%)
- STAR 50: X,XXX.XX pts (+/-X / +/-X%)
- ChiNext: X,XXX.XX pts (+/-X / +/-X%)

**Hong Kong (Last Close)**
- Hang Seng Index: XX,XXX.XX pts (+/-X / +/-X%)
- Hang Seng Tech: X,XXX.XX pts (+/-X / +/-X%)

**US Stocks (Last Close)**
- S&P 500: X,XXX.XX pts (+/-X / +/-X%)
- Nasdaq 100: XX,XXX.XX pts (+/-X / +/-X%)

---

### 📰 24-Hour News Briefing

#### 🟢 Bullish

1. **Headline**
   - 📰 Source | Time
   - Summary

#### 🔴 Bearish

1. **Headline**
   - 📰 Source | Time
   - Summary

#### ⚪ Neutral

1. **Headline**
   - 📰 Source | Time
   - Summary

---

### 📡 News Sources

Chinese: 36Kr, Sina Finance, People's Daily, Cailianshe
International: BBC, Bloomberg, Yahoo Finance, WSJ, Financial Times

---

**Note**: Major stock markets are closed on weekends, data shows last trading day close. Commodities and crypto markets trade 24/7.
```

## Key Rules

1. **Language** - Use the user's preferred language (default to Chinese/中文 unless explicitly requested otherwise)
2. **Never fabricate data** - Always fetch real data before generating report
3. **24-hour news window** - Only include news from last 24 hours
4. **Label trading status** - Clearly mark which markets are open vs closed
5. **Source attribution** - Every news item must have source and timestamp
6. **Mobile-friendly** - Use list format, avoid tables for Telegram
7. **Comprehensive coverage** - Collect from all listed media sources

## Market Trading Hours

- **A-shares**: Mon-Fri 09:30-11:30, 13:00-15:00 (Beijing time)
- **Hong Kong**: Mon-Fri 09:30-12:00, 13:00-16:00 (Hong Kong time)
- **US Stocks**: Mon-Fri 21:30-04:00 next day (Beijing time, DST adjusted)
- **Commodities/Crypto**: 24/7

## Helper Script

Use the bundled script for data collection:
```bash
uv run ~/.openclaw/workspace-group/skills/capital-market-report/scripts/generate-report.py
```
