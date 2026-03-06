---
name: agent-swarm-orchestrator
description: Orchestrate OpenClaw Agent Swarm workflows for multi-project coding automation with Obsidian task intake, Claude coding, Codex review, GitLab MR flow, merge+sync, and done-status closure.
---

# Agent Swarm Orchestrator

Multi-project coding automation: Obsidian task intake → Claude Code → Codex review → GitLab MR → merge + sync.

## Architecture

```
Obsidian note (status: ready)
  → scan-obsidian.sh (cron 15min)
    → spawn-agent.sh
      ├── git worktree + branch
      ├── prompt file (task + context.md)
      └── tmux session → run-agent.sh
                            ├── claude -p "$PROMPT" | tee log
                            └── review-and-push.sh
                                  ├── codex review (graded)
                                  ├── push + glab mr create --yes
                                  └── notification → Telegram

check-agents.sh (cron 5min)
  ├── dead tmux + commits → trigger review
  ├── >60min → timeout notification
  └── MR merged → done + sync main
```

## Core Paths

| Path | Purpose |
|------|---------|
| `~/agent-swarm/` | Control plane (scripts, registry, tasks) |
| `~/agent-swarm/registry.json` | Project configs (repo, paths, branch) |
| `~/agent-swarm/tasks.json` | Task state machine |
| `~/GitLab/repos/` | Local repos |
| `~/GitLab/worktrees/` | Per-task worktrees |
| `~/Documents/Obsidian Vault/agent-swarm/` | Task intake notes |

## Scripts

| Script | Purpose |
|--------|---------|
| `spawn-agent.sh` | Create worktree + prompt + tmux → run-agent |
| `run-agent.sh` | `claude -p` → check commits → trigger review |
| `review-and-push.sh` | Codex review → graded fix → push → MR |
| `check-agents.sh` | Cron fallback: detect done/stuck, auto-close merged |
| `scan-obsidian.sh` | Parse Obsidian notes, spawn `status: ready` tasks |
| `send-notifications.sh` | Send `.notification` files via OpenClaw CLI |
| `merge-and-sync.sh` | Merge MR + sync local main |
| `sync-project-main.sh` | Fast-forward local repo to origin/main |
| `new-project.sh` | Initialize project (GitLab + registry + context + Obsidian) |
| `cleanup.sh` | Daily archive old tasks, clean worktrees/logs |

## Usage

### Spawn task
```bash
~/agent-swarm/scripts/spawn-agent.sh <project> "<task description>"
```

### Monitor
```bash
tmux attach -t agent-<task-id>        # live output
tail -f ~/agent-swarm/logs/<task-id>.log  # log file
```

### Merge and sync
```bash
~/agent-swarm/scripts/merge-and-sync.sh <project> <mr-iid>
```

### New project
```bash
~/agent-swarm/scripts/new-project.sh <project-name>
```

## Task Lifecycle

```
starting → running → [no-output | reviewing]
reviewing → [ready_to_merge | review-error | needs-manual-fix | fixing]
fixing → reviewing (retry, max 2)
ready_to_merge → done (auto on MR merged)
```

## Prerequisites

### Claude Code CLI
- Authenticated via OAuth (`~/.claude.json` oauthAccount)
- `~/.claude/settings.json`: `skipDangerousModePermissionPrompt: true`
- `~/.claude.json` projects: trust `~/GitLab/worktrees` and `~/GitLab/repos` (`hasTrustDialogAccepted: true`)
- No `ANTHROPIC_*` env vars leaking into tmux (causes proxy conflicts)

### Tools
- `claude` CLI (Claude Code)
- `codex` CLI (OpenAI Codex, for review)
- `glab` CLI (GitLab)
- `jq`, `python3`, `tmux`

### Cron
```
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
*/5 * * * * ~/agent-swarm/scripts/check-agents.sh
*/15 * * * * ~/agent-swarm/scripts/scan-obsidian.sh
0 3 * * * ~/agent-swarm/scripts/cleanup.sh
```

### Notifications
```bash
openclaw message send --channel telegram --target <chat_id> --message "..."
```
Configure target in `send-notifications.sh` via `SWARM_NOTIFY_TARGET` env var.

## Prompt Template

Each task gets a prompt file with:
1. Project name, task description, priority
2. Working directory and branch
3. Project context (from `context.md`)
4. Standard instructions (commit, push, MR, update context.md if architectural changes)

## Obsidian Integration

- Frontmatter `status: active | stop` controls project scanning
- Task block: `### Task Name` + `status: ready` + `> description`
- `### INIT_PROJECT` + `status: ready` triggers `new-project.sh`
- Dedup: sha1(project+name+desc)[:12], flagged in logs
- Debounce: skip files modified within last 1 minute

## Review Policy

- **Coding**: Claude Code (`-p` mode, auto-exit)
- **Review**: Codex (`codex exec review`)
- **CRITICAL/HIGH**: auto-fix retry (max 2), then `needs-manual-fix`
- **MEDIUM**: auto-fix (non-blocking), skip for docs-only
- **LOW**: notes in MR description only
- **Docs-only**: downgrade CRITICAL/HIGH to MEDIUM

## Portable Install

```bash
mkdir -p ~/agent-swarm/{scripts,logs,projects}
cp -f <skill_dir>/scripts/*.sh ~/agent-swarm/scripts/
chmod +x ~/agent-swarm/scripts/*.sh
echo '{"projects":{}}' > ~/agent-swarm/registry.json
echo '{"tasks":[]}' > ~/agent-swarm/tasks.json
```

Then: register projects in `registry.json`, set cron, configure notifications.

## Guardrails

### You are the dispatcher, not the analyst

When a user reports an issue or requests a change to project code:

- ❌ Do NOT read project source code to analyze
- ❌ Do NOT diagnose root causes yourself
- ❌ Do NOT design technical solutions
- ✅ Understand the user's intent and translate it into a clear task description
- ✅ Pass user feedback verbatim to the agent (e.g. "tiles didn't get bigger")
- ✅ Spawn the task, monitor progress, merge MRs, maintain the swarm system

The coding agent runs in a full worktree with complete project context — it is better positioned to read code, diagnose issues, and implement fixes than you are from a chat session.

### Other rules

- Do not edit project code directly — always go through spawn-agent
- Push-first + cron-fallback notification design
- State names: `done`, `ready_to_merge`, `review-error`, `needs-manual-fix`
- Context.md auto-update only for architectural changes (not minor fixes)
