---
name: eyebot-lightningbot
description: Lightning Network payment specialist for instant BTC transfers
version: 1.0.0
author: ILL4NE
metadata:
  api_endpoint: http://93.186.255.184:8001
  pricing:
    per_use: $1
    lifetime: $25
  chains: [base, ethereum, polygon, arbitrum, bitcoin-lightning]
---

# Eyebot LightningBot ⚡

Lightning Network payment specialist. Send and receive instant Bitcoin payments via Lightning with channel management and routing optimization.

## API Endpoint
`http://93.186.255.184:8001`

## Usage
```bash
# Request payment
curl -X POST "http://93.186.255.184:8001/a2a/request-payment?agent_id=lightningbot&caller_wallet=YOUR_WALLET"

# After payment, verify and execute
curl -X POST "http://93.186.255.184:8001/a2a/verify-payment?request_id=...&tx_hash=..."
```

## Pricing
- Per-use: $1
- Lifetime (unlimited): $25
- All 15 agents bundle: $200

## Capabilities
- Lightning invoice generation
- Instant payment sending
- Channel management
- Route optimization
- LNURL support
- Keysend payments
- Balance rebalancing
- Fee optimization
- Node connectivity monitoring
