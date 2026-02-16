---
name: Coding
slug: coding
version: 1.0.2
description: Learns your coding preferences from explicit feedback. Starts empty, grows as you correct and guide.
changelog: Replace vague observe/detect with explicit feedback learning, require user confirmation before storing preferences
metadata: {"clawdbot":{"emoji":"💻","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## How This Skill Learns

This skill learns your preferences ONLY from:
- **Explicit corrections** — "Actually, I prefer X over Y"
- **Direct statements** — "Always use snake_case" 
- **Repeated requests** — You ask for the same thing 2+ times

This skill NEVER:
- Reads your project files to infer preferences
- Observes without your knowledge
- Stores data you haven't explicitly approved

## Memory Storage

Preferences stored at `~/coding/memory.md`. Created on first use.

```
~/coding/
├── memory.md      # Active preferences (≤100 lines)
└── history.md     # Archived old preferences
```

**To create:** `mkdir -p ~/coding`

## Memory Format

```markdown
# Coding Memory

## Stack
- python: prefer 3.11+
- js: use TypeScript always

## Style
- naming: snake_case for Python, camelCase for JS
- imports: absolute over relative

## Structure
- tests: same folder as code, not separate /tests

## Never
- var in JavaScript
- print debugging in production
```

## How Preferences Are Added

1. **User corrects output** → Agent asks: "Should I remember this preference?"
2. **User confirms** → Agent adds to `~/coding/memory.md`
3. **User can review** → "Show my coding preferences" lists current memory

No preference is stored without explicit user confirmation.

## Rules

- Keep each entry ultra-compact (5 words max)
- Confirm before adding any preference
- Check `dimensions.md` for categories
- Check `criteria.md` for when to add
- Never exceed 100 lines in memory.md
- Archive old patterns to history.md

## On Session Start

1. Load `~/coding/memory.md` if exists
2. Apply stored preferences to responses
3. If no file exists, start with no assumptions

## Auxiliary Files

| File | Purpose |
|------|---------|
| `dimensions.md` | Categories of preferences to track |
| `criteria.md` | When to suggest adding a preference |
