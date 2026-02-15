---
name: skill-cleaner
description: Automatically verify "suspicious" skills via VirusTotal and add them to the safety allowlist.
metadata:
  {
    "openclaw":
      {
        "emoji": "🧹",
        "requires": { "env": ["VIRUSTOTAL_API_KEY"] },
        "user-invocable": true,
      },
  }
---

# Skill Cleaner

Scans your installed skills for suspicious patterns, verifies them against VirusTotal, and "fixes" false positives by adding them to the safety allowlist.

## Usage

Run the cleaner to automatically verify and allowlist suspicious skills:

```bash
# Dry run (safe, just shows what would happen)
npx tsx ./skills/skill-cleaner/scripts/clean.ts

# Commit clean results to safety allowlist
npx tsx ./skills/skill-cleaner/scripts/clean.ts --commit
```

## Security Disclosure

This skill requires high-privilege access to function as a security utility:

- **Persistence**: Writes to `~/.openclaw/security/safety-allowlist.json`. This is required to remember verified safe files so they aren't flagged in future scans.
- **Privilege**: Requires `VIRUSTOTAL_API_KEY` to perform reputation lookups.
- **Verification**: The script performs a **Live Scan** of your `skills/` directory using the internal OpenClaw security module.

**Audit Guidance**: If you see "Persistence & Privilege" warnings on the Hub, this is expected behavior for a security management tool. Always run in dry-run mode first to inspect planned changes.
