# SECURITY.md — Designer

## Access Level
- Read/write to workspace-designer/
- Read access to shared/ (via symlink)
- Web search for visual references
- Image generation skills (if installed)

## Restrictions
- No exec, no edit (code), no apply_patch
- No browser, no cron, no gateway
- agentToAgent: can receive messages from Leader only (via sessions_send)
- Cannot post or publish visuals

## Data Handling
- Generated images stay in workspace until Leader collects
- Don't use real customer photos without explicit approval
- Reference images from the web are for inspiration, not reproduction

## Brand Scope

- Only read brand files specified in the current task brief from Leader
- Do not browse other brands' profile.md, content-guidelines.md, or domain files
- Cross-brand tasks require explicit cross-brand scope from Leader
- If you need another brand's context, use [NEEDS_INFO]
