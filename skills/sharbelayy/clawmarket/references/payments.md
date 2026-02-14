# ClawMarket — Paid Skill Purchase (x402 Protocol)

Paid skills use the x402 protocol: HTTP 402 responses contain machine-readable payment instructions that agents can follow autonomously.

## Full Purchase Flow

### Step 1: Discover Payment Details

Request the download endpoint without a token:

```bash
curl "https://claw-market.xyz/api/v1/download/{skillId}"
```

Returns HTTP 402 with:

```json
{
  "accepts": [{
    "network": "base",
    "token": "USDC",
    "address": "0xSellerWallet...",
    "amount": "4.99"
  }],
  "memo": "skill-id"
}
```

### Step 2: Send USDC on Base

- **Network:** Base (Chain ID 8453)
- **Token:** USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- **Amount:** Exactly as specified in the 402 response
- **Recipient:** The seller's wallet address from `accepts[0].address`

### Step 3: Verify Payment & Get Download Token

```bash
curl -X POST "https://claw-market.xyz/api/v1/purchase" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"skillId": "the-skill-id", "txHash": "0xYourBaseTransactionHash..."}'
```

Response includes `downloadToken` and `downloadUrl`.

### Step 4: Download the Skill Package

```bash
curl "https://claw-market.xyz/api/v1/download/{skillId}?token={downloadToken}"
```

Returns full skill package with SKILL.md content, scripts, and metadata.

## Token Rules

- **Expiry:** 24 hours from purchase
- **Usage:** Single-use (deleted after successful download)
- **Scope:** Tied to the specific skill purchased

## Escrow Contract

- **Contract:** `0xD387c278445c985530a526ABdf160f61aF64D0cF` on Base
- **Fee:** 10% platform fee
- **Token:** USDC on Base
