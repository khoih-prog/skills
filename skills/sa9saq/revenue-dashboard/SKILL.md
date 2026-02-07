---
name: revenue-dashboard
description: Revenue dashboard for real-time portfolio tracking. Built with Next.js + shadcn/ui + SQLite. Track crypto, freelance income, and service revenue in one place. Use when user says "revenue dashboard", "portfolio tracking", "income tracker", or "earnings report".
---

# Revenue Dashboard

Real-time revenue and portfolio tracking dashboard. Monitor crypto holdings, freelance income, and service revenue from a single interface.

## Features

- **Real-time portfolio tracking**: Crypto prices updated via CoinGecko API
- **Multi-source revenue**: Track crypto, freelance (Coconala, Lancers), and service income
- **Beautiful UI**: Built with Next.js 14 + shadcn/ui + Recharts
- **SQLite storage**: Lightweight, no external database needed
- **REST API**: Programmatic access to all data
- **Date range filtering**: Daily, weekly, monthly, yearly views

## Quick Start

```bash
cd {skill_dir}
npm install
npm run build

# Start dashboard
npm start -- --port 3020

# Or development mode
npm run dev
```

## API Endpoints

- `GET /api/portfolio` — Current portfolio summary
- `GET /api/revenue?from=YYYY-MM-DD&to=YYYY-MM-DD` — Revenue by date range
- `POST /api/transactions` — Add transaction
- `GET /api/holdings` — Current crypto holdings
- `POST /api/income` — Record freelance/service income

## Dashboard Sections

1. **Portfolio Overview** — Total value, 24h change, allocation chart
2. **Revenue Timeline** — Income over time (line/bar chart)
3. **Holdings Table** — Individual asset performance
4. **Income Sources** — Breakdown by source (crypto, freelance, services)

## Configuration

Environment variables:
- `PORT` — Server port (default: 3020)
- `DB_PATH` — SQLite path (default: ./data/revenue.db)
- `COINGECKO_API` — CoinGecko API base URL (default: free tier)

## Requirements

- Node.js 18+
- No API keys required (CoinGecko free tier)
