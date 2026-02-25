---
name: openclaw-guardian
description: >
  A security layer plugin for OpenClaw that intercepts high-risk AI operations
  (file deletion, config modification, external requests, etc.) through a
  multi-Guardian Agent voting mechanism. Supports tiered review — fast lane
  (auto-pass), light review (single Guardian), and full vote (3 Guardians with
  different perspectives: safety, privacy, permission, reversibility, cost).
  Keyword-based risk scoring with zero-cost rule matching; LLM-based Guardian
  evaluation only triggers for the ~5% of operations that actually need review.
---

# OpenClaw Guardian

> The missing safety layer for AI agents.

## What It Does

Guardian sits between the AI's decision and actual execution, automatically
assessing risk and routing dangerous operations through independent Guardian
Agents for voting-based approval.

**95% of operations pass instantly** (zero latency, zero cost). Only the ~5%
that are potentially dangerous trigger Guardian review.

## Architecture

```
Tool Call → Risk Assessor (keyword rules, 0ms)
              ↓
   Score 0-30  → Fast Lane (just execute)
   Score 31-70 → Light Review (1 Guardian, ~1-2s)
   Score 71-100 → Full Vote (3 Guardians, ~2-4s, majority rules)
```

### Guardian Perspectives (Full Vote)

| Guardian        | Focus                                              |
|-----------------|----------------------------------------------------|
| Safety          | Destructive potential, system recovery              |
| Privacy         | Credentials, API keys, personal data                |
| Permission      | Scope of user authorization                         |
| Reversibility   | Undo capability, blast radius                       |
| Comprehensive   | All angles (used in Light Review)                   |

## Installation

1. Clone into your OpenClaw workspace:

```bash
cd ~/.openclaw/workspace
git clone https://github.com/fatcatMaoFei/openclaw-guardian.git
```

2. Register the plugin in `openclaw.json`:

```json
{
  "plugins": {
    "load": {
      "openclaw-guardian": {
        "path": "workspace://openclaw-guardian",
        "enabled": true
      }
    }
  }
}
```

3. Restart OpenClaw gateway.

## Configuration

Edit `default-policies.json` to enable/disable:

```json
{ "enabled": true }
```

## File Structure

- `index.ts` — Entry point; registers `before_tool_call` hook
- `src/blacklist.ts` — Keyword rule engine for risk scoring
- `src/llm-voter.ts` — Tiered LLM voting with parallel execution
- `src/audit-log.ts` — SHA-256 hash-chain audit logger
- `openclaw.plugin.json` — Plugin manifest
- `default-policies.json` — Default risk policies (user-customizable)

## Token Cost

| Tier         | % of Ops | Extra Cost                |
|--------------|----------|---------------------------|
| Fast Lane    | 85-95%   | 0 (rule-based only)       |
| Light Review | 5-10%    | ~500 tokens per review    |
| Full Vote    | 1-3%     | ~1500 tokens per review   |

Average overhead: ~15-35% of total token usage.

## License

MIT
