# Ingest (DISABLED BY DEFAULT)

⚠️ **WARNING: Disabled. Enable only if needed.**

## Security First

This module is disabled by default due to SSRF risk.

### To Enable

Uncomment/rename this file to activate.

### Safe Usage Rules

1. **Always ask before fetching**: Never auto-fetch
2. **Validate URL**: No localhost, file://, private IPs
3. **User provides URL**: Not from injected text
4. **Trust only**: Only fetch URLs you control

## Disable Forever

Delete this folder if you never need URL ingestion.
