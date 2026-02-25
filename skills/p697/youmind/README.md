<div align="center">

# Youmind AI Agent Skill

**Let your AI agent chat directly with your Youmind boards**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![AI Agent Skill](https://img.shields.io/badge/AI%20Agent-Skill-purple.svg)](https://github.com/p697/youmind-skill)
[![GitHub](https://img.shields.io/github/stars/p697/youmind-skill?style=social)](https://github.com/p697/youmind-skill)

> Use this skill to query Youmind board chat directly from any AI agent with shell access — Claude Code, Codex, OpenClaw, and more. Browser automation, persistent auth, board library management, and NotebookLM-style Smart Add auto naming.

[Installation](#installation) • [Quick Start](#quick-start) • [Why Youmind](#why-youmind-not-manual-copy-paste) • [How It Works](#how-it-works)

</div>

---

## Important: Local CLI Only

This skill is designed for local AI agents with shell/exec access (Claude Code, Codex, OpenClaw, etc.), not sandboxed web chat environments.

It requires:
- Shell access to run Python scripts
- Local browser automation (Patchright/Chrome)
- Local auth persistence
- Local filesystem state under `data/`

---

## The Problem

When your product docs, research notes, and references live in Youmind boards, coding workflows get fragmented:

- You jump between terminal and browser repeatedly
- You lose context while copy-pasting questions and answers
- Board metadata is inconsistent, so retrieval quality drops
- Login/setup friction interrupts research flow

## The Solution

This skill lets your coding agent ask Youmind directly:

```text
Your task -> Agent asks Youmind board chat -> Youmind answers -> Agent continues implementation
```

No manual copy-paste loop.

---

## Why Youmind, Not Manual Copy-Paste?

| Approach | Context Switching | Setup | Reliability | Velocity |
|----------|-------------------|-------|-------------|----------|
| Browser copy-paste | High | Instant | Human-error prone | Slow |
| Ad-hoc local file search | Medium | Low | Misses board-level context | Medium |
| Youmind Skill | Low | Minutes | Consistent board routing + saved auth | High |

### What this skill adds on top of plain Youmind chat

1. Agent-native workflow in terminal
2. Persistent authentication across runs
3. Reusable board library with active-board selection
4. Smart Add auto metadata discovery and naming
5. Follow-up reminder flow to reduce incomplete answers

---

## Installation

### Claude Code / Codex

```bash
mkdir -p ~/.claude/skills
cd ~/.claude/skills
git clone https://github.com/p697/youmind-skill.git
cd youmind-skill
```

### OpenClaw

```bash
mkdir -p ~/.openclaw/workspace/skills
cd ~/.openclaw/workspace/skills
git clone https://github.com/p697/youmind-skill.git
cd youmind-skill
```

On first real use, the skill auto-creates `.venv`, installs dependencies, and installs Chrome runtime for Patchright.

---

## Quick Start

### 1. Check available skills

Say to your AI agent:

```text
What skills do I have?
```

### 2. Authenticate once

```text
Set up Youmind authentication
```

A browser opens, you complete login, and auth state is stored locally.

### 3. Create your knowledge base

Go to [youmind.com](https://youmind.com/) -> Create board -> Add your sources:

- 📄 PDFs, docs, and notes
- 🔗 Websites and GitHub links
- 🎥 YouTube/video links
- 📚 Multiple sources in one board

Share: `Board settings -> Share -> Anyone with link -> Copy`

### 4. Add your board

Option A: Smart Add (recommended)

```text
Smart add this board: https://youmind.com/boards/...
```

Option B: Manual add

```text
Add this Youmind board to my library: https://youmind.com/boards/...
```

### 5. Start querying

```text
Ask my Youmind board: summarize the key technical decisions
```

---

## Smart Add (NotebookLM-Style Auto Naming)

Smart Add is the Youmind mapping of NotebookLM skill's one-click auto onboarding.

What it does:
1. Queries the board automatically
2. Extracts structured metadata (`name`, `description`, `topics`)
3. Saves the board to local library
4. Activates it by default

Discovery modes:
- Single-pass (default): one structured extraction query
- Two-pass (`--two-pass`): summary then structured extraction

If extraction quality is poor, the workflow falls back to summary-based metadata generation.

---

## How It Works

This is a local skill folder with instructions + Python automation scripts.

```text
SKILL.md
scripts/
  run.py
  auth_manager.py
  board_manager.py
  ask_question.py
  browser_utils.py
  browser_session.py
  cleanup_manager.py
  setup_environment.py
references/
  api_reference.md
  usage_patterns.md
  troubleshooting.md
data/ (generated locally)
```

Runtime model:
1. Agent detects Youmind intent
2. Agent runs the matching script via `scripts/run.py`
3. Browser automation opens Youmind and submits query
4. Answer is returned to the agent
5. Agent decides whether follow-up questions are needed

---

## Core Features

### Source-constrained board querying
Queries are grounded in the selected Youmind board context.

### Board library management
Add/list/search/activate/remove boards with local metadata persistence.

### Persistent authentication
One-time login with reusable local browser state.

### Smart Add auto onboarding
Board metadata discovery with automatic naming and topic generation.

### Local isolation
Dependencies and state stay inside the skill folder.

---

## Common Prompts

| What you say | What happens |
|--------------|--------------|
| "Set up Youmind authentication" | Opens browser login and saves auth state |
| "Smart add this board: [link]" | Auto-discovers metadata and saves board |
| "Show my Youmind boards" | Lists saved board library |
| "Use this board: [name/id]" | Sets active board |
| "Ask my Youmind board about [topic]" | Queries board chat and returns answer |
| "Clean Youmind local state" | Clears generated local runtime data |

---

## Limitations

- Browser automation (not an official Youmind API)
- UI selector drift may occur when Youmind updates frontend
- Stateless ask model (each run is an independent query)
- Smart Add quality depends on board chat response quality

---

## Troubleshooting

Try these prompts first:

```text
Re-authenticate Youmind
Show browser and retry the same question
List my board library
```

Detailed references:
- `references/troubleshooting.md`
- `references/api_reference.md`
- `references/usage_patterns.md`

---

## Security Notes

- `data/` contains auth/browser state and must not be committed
- Use a dedicated automation account if your organization requires strict separation

---

## License

MIT (`LICENSE`)
