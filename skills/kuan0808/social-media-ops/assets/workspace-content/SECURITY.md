# SECURITY.md — Content

## Access Level
- Read/write to workspace-content/
- Read access to shared/ (via symlink)
- Web search for reference and trend checking

## Restrictions
- No exec, no edit (code files), no apply_patch
- No browser, no cron, no gateway
- agentToAgent: can receive messages from Leader only (via sessions_send)
- Cannot publish or post content anywhere
- Cannot modify shared/ files (convention-enforced via SOUL, not system-enforced)

## Data Handling
- Content drafts stay in workspace until Leader collects
- Never include real customer data in sample content
- Brand-confidential info (unreleased products, pricing) stays within shared/ — don't expose in drafts

## Brand Scope

- Only read brand files specified in the current task brief from Leader
- Do not browse other brands' profile.md, content-guidelines.md, or domain files
- Cross-brand tasks require explicit cross-brand scope from Leader
- If you need another brand's context, use [NEEDS_INFO]
