# SECURITY.md — Researcher

## Access Level
- Read/write to workspace-researcher/
- Read access to shared/ (via symlink)
- Web search and web fetch for research

## Restrictions
- No exec, no browser, no cron, no gateway
- agentToAgent: can receive messages from Leader only (via sessions_send)
- shared/ updates: propose via `[KB_PROPOSE]` in task response. Leader handles all shared/ writes.

## Data Handling
- Research data from public sources only
- Never store API keys or credentials
- Log all significant sources for auditability

## Brand Scope

- Only read brand files specified in the current task brief from Leader
- Do not browse other brands' profile.md, content-guidelines.md, or domain files
- Cross-brand tasks require explicit cross-brand scope from Leader
- If you need another brand's context, use [NEEDS_INFO]
