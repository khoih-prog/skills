---
name: agent-brain
description: "Memory system for AI agents - never repeat yourself"
homepage: https://github.com/alexdobri/clawd/tree/main/skills/agent-brain
metadata:
  openclaw:
    emoji: 🧠
    disable-model-invocation: true
    user-invocable: true
---

# Agent Brain 🧠

*Your AI's personal memory that never forgets*

## The Problem

Every conversation starts from zero. You repeat yourself. The AI forgets what you taught it yesterday.

## The Solution

Agent Brain gives your AI a memory that actually works.

```
┌─────────────────────────────────────────────────────────┐
│                    👤 YOU                               
│  "Remember: I prefer prose over bullets"              
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    🧠 AGENT BRAIN                      
│  ┌─────────┐  ┌─────────┐  ┌─────────┐              
│  │ Archive │  │ Signal  │  │  Gauge  │              
│  │   📦    │  │   ⚡    │  │   📊    │              
│  │ Stores  │  │ Catches │  │ Confidence              
│  │ facts   │  │ conflicts│  │  level  │              
│  └────┬────┘  └────┬─────┘  └────┬────┘              
│       │           │            │                     
│  ┌─────────┐  ┌─────────┐                           
│  │ Ritual  │  │  Vibe   │                           
│  │   🔄    │  │   🎭    │                           
│  │ Habits  │  │  Tone   │                           
│  └─────────┘  └─────────┘                           
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              💾 MEMORY (Local Only)                    
│  ┌─────────────────────────────────────────────────┐   
│  │           memory/index.json                     │   
│  │           All data stays on your machine       │   
│  └─────────────────────────────────────────────────┘   
└─────────────────────────────────────────────────────────┘
```

## What You Get

| Feature | Benefit |
|---------|---------|
| **Never repeat yourself** | Teach once, remember forever |
| **Catch contradictions** | AI warns when you contradict yourself |
| **Confidence tracking** | Knows when it's sure vs. unsure |
| **Habit learning** | Remembers your workflows |
| **Tone detection** | Adjusts to your mood |

## What Each Module Does

| Module | What It Does | Example |
|--------|--------------|---------|
| **Archive** | Stores facts & knowledge | "Remember: Alex prefers prose" |
| **Signal** | Detects contradictions | Warns if you contradict yourself |
| **Gauge** | Tracks confidence level | Says "I'm not sure" when appropriate |
| **Ritual** | Learns your habits | Remembers "Alex always starts with research" |
| **Vibe** | Detects emotional tone | Adjusts response to match your mood |
| **Ingest** | Fetches URLs (⚠️ disabled) | "Ingest: https://..." |

## Storage (Local Only)

**All data stays on your machine:**

- File: `memory/index.json`
- No cloud sync by default
- You control where data goes

### Optional: SuperMemory Sync

If you want cloud backup, you can enable SuperMemory:

1. Install SuperMemory integration separately
2. Edit Archive module to enable sync
3. Data stays local unless YOU enable cloud

## Commands

```
"Remember: <fact>"        → Store a fact
"Check conflicts"          → Look for contradictions
"How confident are you?"   → Gauge module
```

## Security

- Ingest module disabled by default
- Runs only on explicit commands
- All data stored locally
- No automatic cloud sync

---

*Install once. Works forever. Your data stays yours.*
