# Archive Memory 📦

**Status:** ✅ Live | **Module:** archive | **Part of:** Agent Brain

Memory encoding, retrieval, consolidation, and decay. The brain's storage system.

## What It Does

- **Encode**: Convert experiences → stored memories
- **Retrieve**: Find relevant past knowledge
- **Consolidate**: Strengthen important, compress old
- **Decay**: Remove stale, low-value data

## Storage: Local Only

**All data stays on your machine.**

File: `memory/index.json`

```json
{
  "type": "episodic|factual|procedural|preference",
  "content": "...",
  "timestamp": "2026-02-17T01:30:00Z"
}
```

## Optional: SuperMemory Sync

SuperMemory cloud sync is **OPT-IN ONLY**.

To enable:
1. Have SuperMemory tool installed in your OpenClaw
2. Edit this file to uncomment the sync call
3. By default: NO data leaves your machine

### Disabled by Default

```
# Default: Local only
# To enable cloud sync, edit this module and uncomment:
# supermemory_store(category:"fact", text:"...")
```

## What Goes Where

| Memory Type | Local | Cloud |
|-------------|-------|-------|
| Factual | ✅ Always | ⬜ Opt-in |
| Preference | ✅ Always | ⬜ Opt-in |
| Episodic | ✅ Always | ❌ No |
| Procedural | ✅ Always | ❌ No |

## Usage

```
"Remember that X"
"Learn: how to do X"
"I prefer X over Y"
"What do you know about X?"
```

## Integration

Part of Agent Brain. Works with:
- **Gauge** → knows when to retrieve
- **Signal** → checks for conflicts
- **Ritual** → stores shortcuts
