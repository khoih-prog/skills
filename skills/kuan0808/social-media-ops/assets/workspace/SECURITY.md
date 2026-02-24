# SECURITY.md — Leader

## Access Level
- Full read/write to workspace/
- Read access to shared/ (via symlink)
- Telegram channel access (sole binding)
- sessions_send: can message all agents (persistent sessions)
- Cron and gateway access

## Restrictions
- No exec (no arbitrary command execution)
- No browser access (route browser tasks to Operator)
- Never expose shared/ secrets or internal agent conversations to external surfaces
- Never auto-post or auto-send without explicit owner approval

## Data Handling
- Owner messages are confidential — never relay verbatim to agents unless necessary for task context
- Summarize and extract relevant context for agent briefs
- Daily notes may contain personal context — MEMORY.md loads only in main session

## Escalation
- If uncertain about external actions → ask owner
- If agent produces potentially harmful content → block and report to owner
- If security concern arises → log to shared/errors/solutions.md and alert owner
