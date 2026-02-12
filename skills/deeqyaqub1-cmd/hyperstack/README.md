# 🃏 HyperStack — Cloud Memory for AI Agents

**Your agent forgets everything. HyperStack fixes that.**

Instead of stuffing 6,000 tokens of conversation history into every prompt, your agent stores knowledge as small cards (~350 tokens) and retrieves only what matters. 94% less tokens. ~$254/mo saved. 30-second setup.

## The Problem

Every time your agent starts a new conversation, it has amnesia. The project stack? Gone. User preferences? Gone. That decision you made last Tuesday? Gone.

The current fix is ugly: dump everything into MEMORY.md or stuff the system prompt with thousands of tokens of "context." It's expensive, slow, and hits context limits fast.

**Nobody is giving agents real memory. HyperStack does.**

## How It Works

| Without HyperStack | With HyperStack |
|---------------------|-----------------|
| ~6,000 tokens/message (full history dump) | ~350 tokens/message (1-2 relevant cards) |
| $81/mo per agent (GPT-4 class) | $4.72/mo per agent |
| Context limit hit after 20 cards | Unlimited cards, retrieves only what's needed |
| Loses memory between sessions | Persistent across all sessions |
| One agent's memory | Shared across team (Pro) |

## Install (30 seconds)

### Option 1: ClawHub (recommended)

```bash
clawhub install hyperstack
```

### Option 2: MCP Server (Claude Desktop, Cursor, VS Code, Windsurf)

```bash
npx hyperstack-mcp
```

### Option 3: SDK

```bash
pip install hyperstack-py    # Python
npm install hyperstack-sdk   # JavaScript
```

### Option 4: Raw REST API

Works with any language. Just `curl` and go.

**One env var. No Docker. No LLM calls on your bill. Just set your API key.**

```bash
export HYPERSTACK_API_KEY=hs_your_key    # Get free at cascadeai.dev
```

## What Your Agent Does

Ask your OpenClaw: *"What do you know about the project?"*

HyperStack searches cards and returns relevant context in ~350 tokens instead of dumping everything.

```
Store a memory     → POST /api/cards       (upsert by slug)
Search memory      → GET  /api/search      (keyword-scored relevance)
List all cards     → GET  /api/cards       (lightweight index)
Delete stale info  → DELETE /api/cards     (keep memory clean)
Auto-extract       → POST /api/ingest     (pipe raw text, get cards back)
```

### Card Anatomy

```json
{
  "slug": "project-webapp",
  "title": "WebApp Project",
  "body": "Next.js 14 + Prisma + Neon PostgreSQL. Deployed on Vercel.",
  "stack": "projects",
  "keywords": ["nextjs", "prisma", "vercel"]
}
```

### Stacks (Categories)

| Stack | Use for |
|-------|---------|
| `projects` 📦 | Tech stacks, repos, architecture |
| `people` 👤 | Teammates, contacts, roles |
| `decisions` ⚖️ | Why X over Y, trade-offs |
| `preferences` ⚙️ | Editor, tools, coding style |
| `workflows` 🔄 | Deploy steps, CI/CD, runbooks |
| `general` 📄 | Everything else |

## How It Compares

|  | HyperStack | Mem0 | Zep | Letta |
|--|------------|------|-----|-------|
| Setup | 1 env var | 6+ env vars | SDK required | Own server |
| LLM cost per op | **$0 to you** | ~$0.002 | ~$0.002 | ~$0.002 |
| Docker required | **No** | Yes (self-hosted) | No | Yes |
| Setup time | **30 seconds** | 5-10 minutes | 5 minutes | 10-15 minutes |
| MCP server | ✅ | Partial | ❌ | Partial |
| Team sharing | ✅ (Pro) | ❌ | Enterprise | ❌ |
| Free tier | 50 cards | 10K memories | Trial | Open source |

## Token Savings Math

3 agents × 50 messages/day × 30 days = 4,500 messages/month

- **Without**: 4,500 × 6,000 tokens = 27M tokens → **~$81/agent/mo** at $3/MTok
- **With**: 4,500 × 350 tokens = 1.6M tokens → **~$4.72/agent/mo**
- **Savings**: ~$76/agent/mo → **~$254/mo for 3 agents**

## Honest Limitations

- Search is keyword-based, not semantic (vector search coming soon)
- Auto-extract uses pattern matching, not LLM (fast + free, but less precise)
- Free tier capped at 50 cards per workspace
- Requires internet — no offline mode
- Cards stored on CascadeAI cloud (Neon PostgreSQL on AWS)

For most workflows, keyword search and 50 cards handles everything. Power users upgrade to Pro.

## Pro ($15/mo)

Free tier includes all core features. 50 cards, 1 workspace, unlimited searches.

[HyperStack Pro](https://cascadeai.dev) unlocks:

- ♾️ Unlimited cards and workspaces
- 👥 Team sharing (up to 20 members)
- 📜 Version history on all cards
- 📊 Usage analytics dashboard

## Verify It Works

After installing, ask your OpenClaw:

> "Store a memory: I prefer dark mode and use VS Code"

Then start a new conversation and ask:

> "What editor do I use?"

If it answers correctly — your agent has memory. 🃏

---

**Built for agents that need to remember. Stop wasting tokens on amnesia.**

[Website](https://cascadeai.dev) · [MCP](https://www.npmjs.com/package/hyperstack-mcp) · [Python](https://pypi.org/project/hyperstack-py/) · [JavaScript](https://www.npmjs.com/package/hyperstack-sdk) · [Discord](https://discord.gg/tdnXaV6e)
