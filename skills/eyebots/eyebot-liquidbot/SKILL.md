---
name: eyebot-liquidbot
description: Liquidity pool management specialist for DEX deployments
version: 1.0.0
author: ILL4NE
metadata:
  api_endpoint: http://93.186.255.184:8001
  pricing:
    per_use: $2
    lifetime: $25
  chains: [base, ethereum, polygon, arbitrum]
---

# Eyebot LiquidBot 💧

Liquidity pool management specialist. Deploy, manage, and optimize liquidity across Uniswap, SushiSwap, PancakeSwap, and other DEXs with automated strategies.

## API Endpoint
`http://93.186.255.184:8001`

## Usage
```bash
# Request payment
curl -X POST "http://93.186.255.184:8001/a2a/request-payment?agent_id=liquidbot&caller_wallet=YOUR_WALLET"

# After payment, verify and execute
curl -X POST "http://93.186.255.184:8001/a2a/verify-payment?request_id=...&tx_hash=..."
```

## Pricing
- Per-use: $2
- Lifetime (unlimited): $25
- All 15 agents bundle: $200

## Capabilities
- Create liquidity pools on major DEXs
- Add/remove liquidity with optimal timing
- LP token lock integration
- Multi-DEX support (Uniswap V2/V3, Sushi, Pancake)
- Impermanent loss tracking
- Auto-compound LP rewards
- Concentrated liquidity positions (V3)
- LP migration between protocols
