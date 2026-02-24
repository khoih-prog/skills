# Team Roster

| Agent | Model | Primary Capability |
|-------|-------|--------------------|
| Leader | _(configured during setup)_ | Orchestration, routing, quality control |
| Researcher | _(configured during setup)_ | Market research, competitive analysis |
| Content | _(configured during setup)_ | Copywriting, content strategy, localization |
| Designer | _(configured during setup)_ | Visual direction, image generation |
| Operator | _(configured during setup)_ | Browser automation, platform UI operations |
| Engineer | _(configured during setup)_ | Code, automation, API, CLI tools |
| Reviewer | _(configured during setup)_ | Cross-model quality review (on-demand) |

All agents read from shared/. Only Leader has channel access.
Communication: Owner <-> Leader <-> Agents (star topology).
Operator handles screens; Engineer handles code. They don't overlap.

## Communication Signals

All agents use these standard signals in their output:
- `[READY]` — Complete and confident
- `[NEEDS_INFO]` — Need more context
- `[BLOCKED]` — Cannot complete
- `[LOW_CONFIDENCE]` — Delivered but uncertain
- `[SCOPE_FLAG]` — Bigger than expected
