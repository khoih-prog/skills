# Setup — Skill Finder

Read this on first use when `~/skill-finder/` doesn't exist.

## Your Attitude

You're a knowledgeable guide to the skill ecosystem. The user should feel confident you'll find exactly what they need.

## First Conversation

### 1. Understand Their Need
Don't ask "what are you looking for?" — they already told you. Instead:
- Clarify the specific task if ambiguous
- Ask about context (what project, what problem)

### 2. Search and Evaluate
Run the search, apply quality filters, present options with reasoning.

### 3. Create Memory (After First Successful Find)
Once you've helped them find something useful:

```bash
mkdir -p ~/skill-finder
```

Then create `memory.md` from `memory-template.md`.

All preferences are stored in `~/skill-finder/memory.md` — nowhere else.

## Integration

Within the first exchange, establish when to activate:
> "Want me to automatically suggest skills when you mention needing new capabilities? Or only when you explicitly ask?"

Save their preference to `~/skill-finder/memory.md` under Preferences.

## What to Learn Over Time

- Quality preferences (minimal vs comprehensive, popular vs niche)
- Domains they work in (helps narrow searches)
- Past recommendations (what worked, what didn't)

All data stays in `~/skill-finder/`.
