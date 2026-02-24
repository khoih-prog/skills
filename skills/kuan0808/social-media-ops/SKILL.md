---
name: social-media-ops
description: Set up a complete multi-brand social media management team on OpenClaw. Scaffolds 7 specialized AI agents (Leader, Researcher, Content Strategist, Visual Designer, Operator, Engineer, Reviewer) in a star topology with persistent A2A sessions, 3-layer memory system, shared knowledge base, approval workflows, and brand isolation. Use when setting up a new social media operations team, adding the multi-agent framework to an existing OpenClaw instance, or when the user mentions social media management, multi-brand operations, or content team setup.
metadata:
  {
    "openclaw": {
      "emoji": "📱",
      "requires": {
        "bins": ["node"]
      }
    }
  }
---

# Social Media Ops

## Overview

This skill sets up a complete AI-powered social media operations team on OpenClaw. It creates:

- **7 specialized agents** in a star topology (Leader + 6 specialists)
- **Persistent A2A sessions** for context-preserving multi-agent workflows
- **3-layer memory system** (MEMORY.md + daily notes + shared knowledge base)
- **Shared knowledge base** with brand profiles, operations guides, and domain knowledge
- **Approval workflow** ensuring nothing publishes without owner approval
- **Brand isolation** with per-brand channels, content guidelines, and asset directories
- **Cron automation** for daily memory consolidation and weekly KB review

## Prerequisites

Before installing, ensure:

1. OpenClaw is installed and `openclaw onboard` has been completed
2. At least one auth profile exists (e.g., Anthropic API key)
3. A Telegram bot is configured (or will be configured during setup)
4. The `~/.openclaw/` directory exists

## Quick Start

```
1. Install the skill (if not already in workspace/skills/)
2. Trigger setup: "Set up my social media operations team"
3. Follow the interactive onboarding (5 steps, ~10 minutes)
4. Add your first brand: "Add a new brand"
5. Start creating content!
```

## Onboarding Flow

When first triggered, this skill runs an interactive setup process.

### Step 1: Prerequisites Check

Verify the environment is ready:

- [ ] OpenClaw installed and `openclaw onboard` completed
- [ ] `~/.openclaw/` directory exists
- [ ] At least one auth profile configured
- [ ] Telegram bot token available (or will configure)

If any prerequisite is missing, guide the user to resolve it before continuing.

### Step 2: Team Configuration

**Agent selection** — Ask the user which team configuration they want:

| Configuration | Agents | Best For |
|---------------|--------|----------|
| **Full Team** (recommended) | All 7 | Multi-brand operations, high content volume |
| **Lean Team** | Leader + Content + Designer + Engineer | Single brand, lower volume |
| **Custom** | User selects | Specific needs |

**Model assignment** — For each agent, recommend:

| Agent | Recommended Model | Rationale |
|-------|-------------------|-----------|
| Leader | Opus (or best available) | Complex orchestration requires high reasoning |
| Researcher | Opus (or best available) | Deep analysis benefits from stronger models |
| Content | Sonnet (or mid-tier) | Fast, capable text generation |
| Designer | Sonnet (or mid-tier) | Fast visual brief writing + image gen |
| Operator | Sonnet (or mid-tier) | Browser automation needs speed |
| Engineer | Sonnet (or mid-tier) | Code generation is well-served by mid-tier |
| Reviewer | Different provider | Independent perspective (e.g., GLM-5, Gemini) |

The user can accept defaults or customize per agent.

### Step 3: Platform Setup

Collect platform configuration:

1. **Telegram bot token** — If not already configured in openclaw.json
2. **Channel mode** — Recommend Group+Topics for multi-brand:
   - **Group+Topics** (recommended) — Supergroup with per-brand forum topics
   - **DM+Topics** — Private chat with forum mode
   - **Group-simple** — Group without topics (context-based routing)
   - **DM-simple** — Private chat (context-based routing)
3. **Group/chat ID** — For Group modes, the Telegram supergroup ID
4. **Operations topic** — Thread ID for system notifications

### Step 4: Run Scaffold

Execute the setup scripts:

```bash
# 1. Create directories, copy templates, set up symlinks
bash scripts/scaffold.sh \
  --skill-dir "$(pwd)" \
  --agents "leader,researcher,content,designer,operator,engineer,reviewer"

# 2. Merge agent configuration into openclaw.json
node scripts/patch-config.js \
  --config ~/.openclaw/openclaw.json \
  --agents "leader,researcher,content,designer,operator,engineer,reviewer"
```

The scaffold creates:
- Agent workspace directories with SOUL.md, SECURITY.md, MEMORY.md
- Shared knowledge base with all template files
- Symlinks from each workspace to shared/
- Sub-skills (instance-setup, brand-manager) in Leader's skills/
- Cron job definitions

The config patcher merges into openclaw.json:
- Agent definitions with model assignments and tool restrictions
- A2A session configuration
- QMD memory paths
- Internal hooks

### Step 5: Instance Setup + First Brand

After scaffolding, run the sub-skills:

1. **Instance Setup** (`instance-setup` skill)
   - Owner name and timezone
   - Communication language (owner-facing)
   - Default content language
   - Bot identity (name, emoji, personality)
   - Updates: `shared/INSTANCE.md`, `workspace/IDENTITY.md`

2. **First Brand** (`brand-manager add`)
   - Brand ID, display name, domain
   - Target market and content language
   - Channel/topic thread ID
   - Creates: brand profile, content guidelines, domain knowledge file, asset directories

3. **Restart Gateway**
   ```
   openclaw gateway restart
   ```

### Step 6: Verification

After setup, verify the installation:

- [ ] All agent workspaces created with SOUL.md and SECURITY.md
- [ ] shared/ directory populated with templates
- [ ] Symlinks from each workspace to shared/ are valid
- [ ] openclaw.json contains all agent definitions
- [ ] A2A configuration is set (tools.agentToAgent.enabled: true)
- [ ] Cron jobs are configured
- [ ] Gateway restarts successfully
- [ ] Leader responds to messages
- [ ] `sessions_send` to at least one agent succeeds

**Suggested first tasks after setup:**
1. Fill in your brand profile: `shared/brands/{brand_id}/profile.md`
2. Test content creation: "Write a Facebook post for {brand}"
3. Add more brands: "Add a new brand"
4. Set up posting schedule: fill in `shared/operations/posting-schedule.md`

## Post-Installation

### Adding More Brands

Use the `brand-manager` sub-skill:
- "Add a new brand" — interactive brand creation
- "List brands" — show all active brands
- "Archive {brand}" — deactivate a brand

### Customizing Agents

Each agent's behavior is defined in their SOUL.md:
- `workspace/SOUL.md` — Leader behavior, routing rules, quality gates
- `workspace-{agent}/SOUL.md` — Specialist behavior and constraints

Modify these files to tune agent behavior for your specific needs.

### Memory System

The 3-layer memory system works automatically:
- **MEMORY.md** — Long-term curated memory (auto-updated by cron)
- **memory/YYYY-MM-DD.md** — Daily activity logs
- **shared/** — Permanent knowledge base (grows over time)

See `references/memory-system.md` for detailed documentation.

### Communication Signals

Agents use standardized signals to communicate status. See `references/signals-protocol.md` for the complete signal dictionary.

## Reference Documentation

| Document | Purpose | When to Read |
|----------|---------|-------------|
| `references/architecture.md` | Star topology, session model, parallelism | Understanding system design |
| `references/agent-roles.md` | Detailed agent capabilities and restrictions | Customizing team composition |
| `references/signals-protocol.md` | Complete signal dictionary | Debugging agent communication |
| `references/memory-system.md` | 3-layer memory + knowledge capture | Understanding memory behavior |
| `references/approval-workflow.md` | Approval pipeline + owner shortcuts | Content publishing workflow |
| `references/troubleshooting.md` | Known issues (IPv6, etc.) + solutions | When something breaks |

## Directory Structure

After installation, the following structure is created:

```
~/.openclaw/
├── openclaw.json                    # Updated with agent configs
├── workspace/                       # Leader
│   ├── SOUL.md, AGENTS.md, HEARTBEAT.md, IDENTITY.md, SECURITY.md
│   ├── memory/, skills/, assets/
│   └── shared -> ../shared/
├── workspace-researcher/            # Researcher
│   ├── SOUL.md, SECURITY.md, MEMORY.md
│   ├── memory/, skills/
│   └── shared -> ../shared/
├── workspace-content/               # Content Strategist
│   └── (same structure)
├── workspace-designer/              # Visual Designer
│   └── (same structure)
├── workspace-operator/              # Operator
│   └── (same structure)
├── workspace-engineer/              # Engineer
│   └── (same structure)
├── workspace-reviewer/              # Reviewer (minimal, read-only)
│   ├── SOUL.md, SECURITY.md
│   └── shared -> ../shared/
├── shared/                          # Shared knowledge base
│   ├── INSTANCE.md                  # Instance configuration
│   ├── brand-registry.md            # Brand registry
│   ├── system-guide.md, brand-guide.md, compliance-guide.md
│   ├── team-roster.md
│   ├── brands/{id}/profile.md       # Per-brand profiles
│   ├── domain/{id}-industry.md      # Industry knowledge
│   ├── operations/                  # Ops guides
│   └── errors/solutions.md          # Error KB
└── cron/jobs.json                   # Scheduled tasks
```

## Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/scaffold.sh` | Create directories, copy templates, set up symlinks | During initial setup |
| `scripts/patch-config.js` | Merge agent config into openclaw.json | During initial setup |

## Sub-Skills

| Skill | Purpose |
|-------|---------|
| `instance-setup` | Configure owner info, language, bot identity |
| `brand-manager` | Add, edit, archive brands |
