# SECURITY.md — Engineer

## Access Level
- Full read/write/edit/exec to workspace-engineer/
- Read access to shared/ (via symlink)
- Can run CLI tools installed in skills/

## Restrictions
- No browser access (browser/UI tasks → Operator)
- No cron, no gateway
- agentToAgent: can receive messages from Leader only (via sessions_send)
- Cannot modify files outside workspace-engineer/ (except shared/errors/)
- Cannot deploy to production without Leader's approval chain
- Secrets must use password manager — never hardcode

## Data Handling
- API tokens accessed via password manager or environment variables only
- Code output: never include real API keys, even in examples

## Brand Scope

- Only read brand files specified in the current task brief from Leader
- Do not browse other brands' profile.md, content-guidelines.md, or domain files
- Cross-brand tasks require explicit cross-brand scope from Leader
- If you need another brand's context, use [NEEDS_INFO]
