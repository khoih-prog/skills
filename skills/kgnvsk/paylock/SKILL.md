---
name: paylock
description: Create, fund, deliver, verify, and track SOL escrow contracts through the PayLock API from OpenClaw chat.
---

# PayLock Skill

Use this skill to manage PayLock escrow contracts directly from chat through a local/public REST API.

- **Local API:** `http://localhost:8767`
- **Public API:** `https://engaging-fill-smoking-accepting.trycloudflare.com`
- **PayLock SOL wallet:** `HxEFMJYCmCngcHK6CbadhYWSZCbpXUJ2t7Ze8sk9CP4z`
- **Fees:** **3% standard**, **1.5% founding** (first 10 clients)

## What this skill supports

1. Create contract → `POST /contract`
2. Fund contract → `POST /fund`
3. Deliver work → `POST /{id}/deliver`
4. Verify delivery → `POST /{id}/verify`
5. Check status → `GET /contract/{id}`
6. List contracts → `GET /contracts`

## Scripts

All wrappers are in `scripts/`:

- `paylock.py` (unified CLI with subcommands)
- `create_contract.py`
- `fund_contract.py`
- `deliver_contract.py`
- `verify_contract.py`
- `get_contract.py`
- `list_contracts.py`
- `paylock_api.py` (shared API client)

No third-party Python packages are required (uses stdlib only).

---

## Quick start

### Unified CLI

```bash
python3 skills/paylock/scripts/paylock.py list
```

Use public API explicitly:

```bash
python3 skills/paylock/scripts/paylock.py --api https://engaging-fill-smoking-accepting.trycloudflare.com list
```

Or set env once:

```bash
export PAYLOCK_API_BASE=http://localhost:8767
```

### Create contract

```bash
python3 skills/paylock/scripts/paylock.py create \
  --payer "agent-alpha" \
  --payee "agent-beta" \
  --amount 1.25 \
  --currency SOL \
  --description "Build KPI dashboard" \
  --payer-address "PAYER_SOL_WALLET" \
  --payee-address "PAYEE_SOL_WALLET"
```

### Fund contract

```bash
python3 skills/paylock/scripts/paylock.py fund \
  --contract-id "ctr_123" \
  --tx-hash "5j3...solana_tx_hash"
```

### Deliver work

```bash
python3 skills/paylock/scripts/paylock.py deliver \
  --id "ctr_123" \
  --delivery-payload "https://example.com/deliverable.zip" \
  --delivery-hash "sha256:abc123..." \
  --payee-token "PAYEE_SECRET_TOKEN"
```

### Verify delivery

```bash
python3 skills/paylock/scripts/paylock.py verify \
  --id "ctr_123" \
  --payer-token "PAYER_SECRET_TOKEN"
```

### Check one contract

```bash
python3 skills/paylock/scripts/paylock.py status --id "ctr_123"
```

### List all contracts

```bash
python3 skills/paylock/scripts/paylock.py list
```

---

## Direct script equivalents

```bash
python3 skills/paylock/scripts/create_contract.py --help
python3 skills/paylock/scripts/fund_contract.py --help
python3 skills/paylock/scripts/deliver_contract.py --help
python3 skills/paylock/scripts/verify_contract.py --help
python3 skills/paylock/scripts/get_contract.py --help
python3 skills/paylock/scripts/list_contracts.py --help
```

---

## Agent usage pattern (chat workflow)

When an agent is asked to run escrow:

1. **Create** contract with payer/payee/amount/description.
2. Ask payer to transfer SOL and provide tx hash.
3. **Fund** contract with `contract_id + tx_hash`.
4. After work completion, **Deliver** with payload/hash/token.
5. Payer checks delivery and **Verify** with payer token.
6. Use **Status** and **List** for monitoring/reporting.

This gives any OpenClaw agent a complete chat-native escrow lifecycle.

---

## ClawHub packaging notes

This skill is ready for ClawHub-style packaging:

- Top-level `SKILL.md` with metadata frontmatter
- Self-contained executable scripts under `scripts/`
- No external Python dependency lock-in
- Configurable endpoint via `--api` or `PAYLOCK_API_BASE`

If publishing requires platform metadata, include/update `_meta.json` in this folder.
