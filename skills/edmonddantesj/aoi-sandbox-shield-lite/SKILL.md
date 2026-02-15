# AOI Sandbox Shield (Lite)

S-DNA: `AOI-2026-0215-SDNA-SS02`

## What this is
A **public-safe** subset of “sandbox shield” focused on:
- creating **snapshots** of critical workspace/config files
- validating JSON config files (syntax + required keys)
- producing an **audit log artifact** you can attach to release notes

## What this is NOT (by design)
- Does **not** apply configs
- Does **not** restart gateways
- Does **not** modify cron
- Does **not** send messages externally

## Commands
### Create snapshot
```bash
node skill.js snapshot --reason="before publishing" 
```

### Validate config JSON (syntax + required keys)
```bash
node skill.js validate-config --path="$HOME/.openclaw/openclaw.json"
```

## Output
All commands print JSON to stdout for easy logging.

## License
MIT (AOI original).
