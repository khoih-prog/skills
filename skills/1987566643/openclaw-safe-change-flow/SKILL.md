---
name: openclaw-safe-change-flow
description: Safe OpenClaw config change workflow with backup, validation, health checks, and rollback for main + secondary instances.
---

# OpenClaw Safe Change Flow

Use this skill before any OpenClaw config edit that might affect availability.

## Scope

- Main instance config: `~/.openclaw/openclaw.json`
- Secondary instance config (optional): `~/.openclaw-wife/.openclaw/openclaw.json`

## Workflow (required)

1. **Backup first**
   - Save timestamped backups: `*.bak.safe-YYYYmmdd-HHMMSS`
2. **Apply minimal change**
   - Edit only required keys.
3. **Validate & health-check**
   - Main: `openclaw status --deep`
   - Secondary: `OPENCLAW_HOME=~/.openclaw-wife openclaw gateway health --url ws://127.0.0.1:18889 --token <token>`
4. **Rollback on failure**
   - Restore latest safe backup and restart gateway.
5. **Confirm channel health**
   - Verify Telegram/API channel is responding in both instances.

## Fast command template

```bash
TS=$(date +%Y%m%d-%H%M%S)
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak.safe-$TS
[ -f ~/.openclaw-wife/.openclaw/openclaw.json ] && cp ~/.openclaw-wife/.openclaw/openclaw.json ~/.openclaw-wife/.openclaw/openclaw.json.bak.safe-$TS

# ...apply config edits...

openclaw status --deep
OPENCLAW_HOME=~/.openclaw-wife openclaw gateway health --url ws://127.0.0.1:18889 --token wife-instance-token-18889
```

## Notes

- Never deploy unvalidated config edits directly to production instance.
- If schema rejects keys, remove unsupported fields and re-validate.
- Prefer testing risky changes on secondary instance first.
