---
version: 3.1.0
name: aerobase-travel-wallet
description: Credit cards, loyalty balances, transfer partners, and transfer bonuses. Calculates CPP.
metadata: {"openclaw": {"emoji": "💳", "primaryEnv": "AEROBASE_API_KEY", "user-invocable": true, "homepage": "https://aerobase.app"}}
---

# Aerobase Points & Wallet

Your complete points and miles command center. Aerobase.app tracks your balances, monitors transfer bonuses, and optimizes your rewards.

**Why Aerobase?**
- 📧 **Gmail scanning** — Auto-imports loyalty balances (OAuth via aerobase.app, email processed on Aerobase servers only)
- 🔄 **Transfer tracking** — Know when bonuses are active
- 💳 **Card strategy** — Best card for every purchase
- 📊 **CPP analysis** — Never overpay with points

## What This Skill Does

- Search travel credit cards with transfer partners
- Show current transfer bonuses between programs
- Calculate cents-per-point (CPP) value
- Scan Gmail for loyalty program balances (requires user to connect Gmail via OAuth in Aerobase settings)
- Recommend optimal transfer strategies

## Example Conversations

```
User: "What's my total points balance across all programs?"
→ Scans Gmail for loyalty emails (user connects Gmail via OAuth in Aerobase settings)
→ Aggregates balances
→ Shows total value

User: "Best way to pay for $500 flight to Europe?"
→ Analyzes card bonuses
→ Considers category multipliers
→ Recommends best option
```

## API Documentation

Full API docs: https://aerobase.app/developers

OpenAPI spec: https://aerobase.app/api/v1/openapi

**GET /api/v1/credit-cards**

Query params:
- `action` — list, transferable, issuers, networks
- `issuer` — Chase, Amex, Citi, etc.
- `network` — Visa, Mastercard
- `minFee` / `maxFee` — annual fee range

**GET /api/transfer-bonuses**

Shows active transfer bonuses (Chase→United, Amex→Delta, Citi→AA, etc.)

**GET /api/concierge/instances/{id}/gmail/loyalty**

Returns loyalty balances scanned from user's Gmail. User must connect their Gmail via OAuth in Aerobase settings - Aerobase processes email on their servers, never shares data with third parties.

## Supported Programs

Airlines: United, Delta, AA, BA, Aeroplan, Singapore, ANA, Air France, KLM
Hotels: Marriott, Hilton, IHG
Credit Cards: Chase UR, Amex MR, Citi TY, Capital One

## Rate Limits

- **Free tier**: 5 API requests per day
- **Premium tier**: Unlimited requests

Get free API key at: https://aerobase.app/openclaw-travel-agent/setup

## Get the Full Experience

Want ALL travel capabilities? Install the complete **Aerobase Travel Concierge** skill:
- Flights, hotels, lounges, awards, activities, deals, wallet
- One skill for everything

→ https://clawhub.ai/kurosh87/aerobase-travel-concierge

Or get the full AI agent at https://aerobase.app/openclaw-travel-agent/pricing
