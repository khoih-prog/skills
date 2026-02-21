# Changelog

All notable changes to the SurrealDB Memory skill will be documented in this file.

## [2.2.0] - 2026-02-19

### Added
- **Per-agent memory isolation** — each agent now reads and writes only its own facts
  - `knowledge_store` / `knowledge_store_sync`: write `agent_id` + `scope: "agent"` on every new fact
  - `knowledge_search`, `knowledge_recall`, `context_aware_search`, `memory_inject`: all queries now filter `WHERE (agent_id = $agent_id OR scope = 'global' OR agent_id IS NONE)`
  - `episode_search` / `episode_learnings`: pass `agent_id` to `EpisodicMemory()` constructor (which already supported it)
  - All MCP tool schemas updated to document the optional `agent_id` parameter
  - Tool dispatch updated to forward `agent_id` from call arguments
- **Global-scope facts** — set `scope: "global"` when storing to make a fact visible to all agents (user preferences, shared project context, etc.)
- **`enhanced-loop-hook.ts` patch** (`references/enhanced-loop-hook-agent-isolation.patch`) — when auto-injection is enabled, the hook now extracts the agent ID from the session key (`agent:scout-monitor:webchat` → `scout-monitor`) and passes it as `agent_id` to `memory_inject`
- **`extract-knowledge.py` agent tagging** — new `--agent-id` CLI argument (default: `"main"`); extracted facts are tagged with the specified agent ID
- **Backward compatible** — existing facts with no `agent_id` (schema defaults to `"main"`) still match the filter predicate via `agent_id IS NONE`, so no data migration needed

### Changed
- `extract-knowledge.py`: `run_extraction`, `run_single_file_extraction`, `extract_from_file`, `store_fact` all accept and propagate `agent_id`
- `mcp-server-v2.py`: `context_aware_search` internal `EpisodicMemory()` call now passes `agent_id`; `memory_inject` episode lookup also scoped to agent

### Verified
- Live DB test: `main` (391 facts) → 391 visible; `scout-monitor` (0 facts) → 0 visible ✅
- Write isolation: fact written as `scout-monitor` invisible to `main` ✅
- Global scope: fact with `scope='global'` visible to all agents regardless of `agent_id` ✅
- End-to-end mcporter: `agent_id='scout-monitor'` returns 0; `agent_id='main'` returns correct results ✅

## [2.1.1] - 2026-02-18

### Fixed
- **Clawdbot → OpenClaw migration**: All stale path references updated
  - `gateway/memory.ts`: Skill search path `~/clawd/` → `~/openclaw/`
  - `extract-knowledge.py`: Workspace path → `OPENCLAW_WORKSPACE` env var with `~/.openclaw/workspace` default
  - `working_memory.py`: `CLAWD_WORKSPACE` → `OPENCLAW_WORKSPACE` env var
  - `integrate-openclaw.sh`: All Clawdbot references → OpenClaw
  - `migrate-sqlite.py`: Description references updated
  - `schema-v2-additive.sql`: Namespace `clawdbot` → `openclaw`
- Aligned skill.json version with CHANGELOG (was stuck at 2.0.0)

## [2.1.0] - 2026-02-17

### Added
- **Redesigned Dashboard UI** - Two-column layout for better UX
  - Left column: Dashboard (stats, confidence bar, system health)
  - Right column: Operations (extraction, maintenance, tips)
  - Installation section now only shows when setup is needed
- **Progress Bars** for extraction operations
  - Real-time progress tracking with percentage
  - Pulsing animation during initialization
  - Step counters (e.g., "3/7 files")
  - Auto-refresh of stats on completion
- **memory_inject Tool** for intelligent context injection
  - Returns formatted context ready for prompt injection
  - Configurable max facts, max episodes, confidence threshold
  - Includes related entities when enabled

### Changed
- UI now shows "Online/Setup Required" badge in header
- Auto-Repair button only appears when system needs setup
- Removed OpenAI warning from UI (implied for AI systems)
- Updated documentation with new UI layout details
- Updated skill.json with accurate requirements and security declarations

### Fixed
- Progress bars now show immediately when operations start
- Better state management for extraction polling

## [2.0.0] - 2026-02-17

### Added
- **Working Memory (Tier 1.5)** - Active task state persistence
  - `working_memory.py` - Manages current task state between iterations
  - Survives session crashes - restart picks up where it left off
  - Creates `.working-memory/` directory with YAML task files
  - Tracks decisions, problems, solutions, learnings

- **Episodic Memory** - Task histories for learning from experience
  - `episodes.py` - Store and search completed task narratives
  - New `episode` table in SurrealDB with vector search
  - Learn from past successes and failures
  - Get relevant learnings for similar new tasks

- **Synchronous Fact Writes** - Real-time storage for important discoveries
  - `knowledge_store_sync` tool with importance-based routing
  - High importance (>0.7) → immediate write to graph
  - Low importance → queued for batch extraction

- **Context-Aware Retrieval** - Factor current task into memory search
  - `context_aware_search` tool boosts facts relevant to both query AND task
  - Includes related episodes in results
  - Better memory recall during complex multi-step tasks

- **Outcome Calibration** - Learn from task success/failure
  - Facts used in successful tasks gain confidence (+0.03)
  - Facts contributing to failures lose confidence (-0.05)
  - New `success_count`, `failure_count` fields on facts
  - `fn::outcome_adjustment()` function in SurrealDB

- **Memory Scoping** - Foundation for multi-tenant (AgentForge prep)
  - Scope fields: `global`, `client`, `agent`
  - Scoped retrieval with priority weighting
  - Agent and client isolation support

- **New MCP Tools** (via `mcp-server-v2.py`):
  - `knowledge_store_sync` - Importance-based sync/batch routing
  - `episode_search` - Find similar past tasks
  - `episode_learnings` - Get actionable insights from history
  - `episode_store` - Store completed episodes
  - `working_memory_status` - Get current task progress
  - `context_aware_search` - Task-aware memory retrieval

### Changed
- Schema upgraded to v2 (`schema-v2.sql`)
- MCP server version 2.0.0 with new tool definitions
- Enhanced confidence calculation with outcome adjustment

### Migration
Run `./scripts/migrate-v2.sh` to apply schema changes.

## [1.3.0] - 2026-02-11

### Added
- **Metadata transparency** for ClawHub compliance:
  - Declared `OPENAI_API_KEY` as required environment variable
  - Added `capabilities` section documenting system-modifying behaviors
  - Added `securityNotes` for credential and API key guidance
  - Added `installWarnings` array with pre-install considerations
- Security section in README.md with mitigation guidance
- Security section in SKILL.md with behavior table

### Fixed
- Fixed schema filename reference in `memory.ts` (`schema.surql` → `schema.sql`)

### Security
- Documented network installer behavior (`curl | sh`) with mitigation
- Documented source patching behavior with mitigation
- Documented default credential usage (root/root) with warning
- Documented API key scope requirements

### Changed
- Bumped version to 1.3.0 for metadata changes

## [1.2.0] - 2026-02-09

### Added
- **MCP Server** (`scripts/mcp-server.py`) with 4 tools:
  - `knowledge_search` - Semantic search for facts
  - `knowledge_recall` - Recall fact with full context
  - `knowledge_store` - Store new facts
  - `knowledge_stats` - Get knowledge graph statistics
- **Simple CLI** (`scripts/knowledge-tool.py`) for quick access
- MCP configuration in `package.json`

### Fixed
- Fixed recursive `close_db()` bug that caused stack overflow
- Fixed SQL `ORDER BY` clause to use alias instead of full expression
- Fixed `SELECT * FROM $fact_id` query to use `db.select()` method

## [1.1.0] - 2026-02-09

### Added
- Gateway integration (`openclaw-integration/gateway/memory.ts`)
- Relation discovery with AI
- Control UI support
- Health checks and auto-repair

### Changed
- Improved extraction pipeline
- Better error handling

## [1.0.0] - 2026-01-31

### Added
- Initial release
- SurrealDB schema with vector search
- Knowledge extraction from memory files
- Confidence scoring with decay
- CLI tools for CRUD operations
- Entity and relationship management
