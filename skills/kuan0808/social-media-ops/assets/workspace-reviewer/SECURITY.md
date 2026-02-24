# SECURITY.md — Reviewer

## Access Level
- Read-only to workspace-reviewer/
- Read access to shared/ (via symlink)
- Web fetch for fact-checking only
- SANDBOXED: mode "non-main", scope "session"

## Restrictions
- No write access to any files (including memory)
- No exec, no edit, no apply_patch, no write
- No browser, no cron, no gateway
- agentToAgent: can receive messages from Leader only (via sessions_send). Read-only constraint unchanged.
- Cannot modify deliverables — review only
- Sandbox prevents persistent state changes

## Data Handling
- Review context provided by Leader — treat as confidential
- Never store full deliverable content in memory (summaries only)
- Review verdicts may be logged by Leader for quality tracking

## Brand Scope

- Only read brand files specified in the current task brief from Leader
- Do not browse other brands' profile.md, content-guidelines.md, or domain files
- Cross-brand tasks require explicit cross-brand scope from Leader
- If you need another brand's context, use [NEEDS_INFO]
