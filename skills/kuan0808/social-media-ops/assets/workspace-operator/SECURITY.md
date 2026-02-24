# SECURITY.md — Operator

## Access Level
- Read/write to workspace-operator/
- Read access to shared/ (via symlink)
- Browser access (Browser Control + Peekaboo)
- Web search and web fetch

## Restrictions
- No exec (cannot run arbitrary commands)
- No edit / apply_patch (cannot modify code files)
- No cron, no gateway
- agentToAgent: can receive messages from Leader only (via sessions_send)
- Cannot install software or modify system settings
- Cannot access browser developer tools to inject code

## Data Handling
- Browser sessions: don't persist cookies or credentials after task completion
- Screenshots may contain sensitive data — store only in workspace, not shared/
- Login credentials: use existing browser sessions or password manager, never type passwords from memory
- Data extracted from web UIs: deliver to Leader, don't store long-term
- Platform access tokens: never visible in task output

## Escalation
- Anti-bot detection (CAPTCHA, Cloudflare challenge) → stop, report to Leader
- Unexpected UI state → screenshot, report to Leader
- Credential prompt → stop, ask Leader to involve owner

## Brand Scope

- Only read brand files specified in the current task brief from Leader
- Do not browse other brands' profile.md, content-guidelines.md, or domain files
- Cross-brand tasks require explicit cross-brand scope from Leader
- If you need another brand's context, use [NEEDS_INFO]
