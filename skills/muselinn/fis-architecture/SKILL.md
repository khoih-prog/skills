# FIS Architecture Skill

> **Version**: 3.1.2  
> **Name**: Federal Intelligence System (联邦智能系统 / FIS 联邦智能系统)  
> **Description**: OpenClaw multi-agent collaboration framework with shared memory, deadlock detection, and skill registry  
> **Status**: P0 core stable, Phase 2/3 framework ready (user data isolated)

---

## Important Notice: Data Isolation

**This Skill provides framework tools only. Your data stays in your workspace.**

- ✅ P0 Core tools (memory_manager, deadlock_detector, etc.) are deployed to shared hub
- ✅ Phase 2/3 framework code (kg_manager, gating_controller) is available for activation
- ❌ **No user data is included** — knowledge graph nodes, memories, and agent data are created in YOUR local workspace

After installation, initialize FIS in your workspace:
```bash
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py
```

---

## Release Note

**v3.1.2** - Clean release with generalization:
- Removed personal configuration examples
- Removed unrelated utilities (tts_edge)
- All examples now use generic placeholders

---

## Architecture Overview

FIS 3.1 Lite is a lightweight, file-based multi-agent collaboration framework designed for OpenClaw environments. It enables:

- **Shared Memory**: Three-tier storage (working/short_term/long_term) for agent communication
- **Deadlock Detection**: DFS-based cycle detection for task dependency management
- **Skill Registry**: Dynamic capability discovery across agents
- **SubAgent Lifecycle**: Worker/Reviewer role management with badge system
- **Zero Core File Pollution**: All extensions isolated to `.fis3.1/` directories

---

## Current Status

### P0 Core (Deployed)
```
research-shared-hub/.fis3.1/           # (or your preferred shared directory)
├── lib/                               # Core Python libraries
│   ├── memory_manager.py              # Shared memory management
│   ├── deadlock_detector.py           # DFS deadlock detection
│   ├── skill_registry.py              # Skill discovery & registration
│   └── subagent_lifecycle.py          # SubAgent lifecycle + badge system
├── memories/                          # Three-tier memory storage
│   ├── working/                       # TTL: 1 hour
│   ├── short_term/                    # TTL: 24 hours
│   └── long_term/                     # Permanent
├── skills/                            # Skill registry
│   ├── registry.json                  # Skill index
│   └── manifests/                     # Agent skill manifests
└── heartbeat/                         # Heartbeat status

Status: ✅ Healthy, zero Core File pollution
```

### Phase 2/3 Features (Framework Ready)

**Framework code is available, user data is created locally:**

```
research-shared-hub/.fis3.1/experimental/  # Created in YOUR workspace
├── knowledge_graph/nodes/entities/        # YOUR nodes (created by you)
├── lib/
│   ├── kg_manager.py                      # Framework: node creation tools
│   ├── gating_controller.py               # Framework: access control logic
│   ├── retrieval_orchestrator.py          # Framework: search orchestration
│   └── emb_spawn_wrapper.py               # Framework: embedding pipeline
└── POLICY_GATING.md                       # Template: customize your policies
```

**How to activate:**
1. Framework code auto-deploys to shared hub
2. Run `init_fis31.py` to create your local `experimental/` structure
3. Create your own nodes using `kg_manager` APIs
4. Your data stays in YOUR workspace, never shared

Status: ✅ Framework ready, user data isolated

---

## Quick Start

```bash
# Initialize FIS 3.1 environment
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/init_fis31.py

# Check architecture health
~/.openclaw/system/scripts/fis_maintenance.sh check

# Cleanup redundancy (dry-run)
~/.openclaw/system/scripts/fis_cleanup_redundancy.sh

# Cleanup subagents
python3 ~/.openclaw/system/scripts/fis_subagent_cleanup.py

# Generate badge images
python3 ~/.openclaw/workspace/skills/fis-architecture/examples/generate_badges.py
```

---

## Python API Reference

### Shared Memory
```python
from memory_manager import write_memory, query_memory

# Agent writes analysis result
write_memory(
    agent="worker",                    # YOUR agent name
    content={"result": data, "score": 0.95},
    layer="short_term",
    tags=["project", "task-001"]       # YOUR tags
)

# Coordinator queries
results = query_memory(
    query="project task",              # YOUR query
    agent_filter=["worker"],           # YOUR agents
    limit=5
)
```

### Deadlock Detection
```python
from deadlock_detector import check_and_resolve

report = check_and_resolve()
if report["deadlock_found"]:
    print(f"Deadlocks: {report['deadlocks']}")
    print(f"Resolved: {report['resolved']}")
```

### Skill Registry
```python
from skill_registry import register_skills, discover_skills

# Register agent skills
register_skills("my_agent", manifest)  # YOUR agent name

# Discover available skills
skills = discover_skills(query="processing")  # YOUR query
```

### SubAgent Lifecycle (Badge System)
```python
from subagent_lifecycle import SubAgentLifecycleManager, SubAgentRole

manager = SubAgentLifecycleManager("coordinator")  # YOUR coordinator name

# Issue badge (spawn subagent)
worker = manager.spawn(
    name="Worker-001",
    role=SubAgentRole.WORKER,
    task_description="Your task description here"  # YOUR task
)

# Generate badge image
image_path = manager.generate_badge_image(worker['employee_id'])

# Batch generation (2x2 grid)
multi_image = manager.generate_multi_badge_image([id1, id2, id3, id4])

# Terminate (auto-cleanup workspace)
manager.terminate(worker['employee_id'], "completed")
```

---

## Directory Structure

```
~/.openclaw/
├── workspace/                         # YOUR coordinator workspace
│   ├── MEMORY.md                      # Core File (protected)
│   ├── HEARTBEAT.md                   # Core File (protected)
│   └── .fis3.1/                       # FIS 3.1 extension
│       └── local_cache/
│
├── workspace-agent1/                  # YOUR agent 1 workspace
│   ├── MEMORY.md
│   ├── HEARTBEAT.md
│   └── .fis3.1/
│       ├── skill_manifest.json        # YOUR skill manifest
│       └── local_cache/
│
├── workspace-agent2/                  # YOUR agent 2 workspace
│   └── ...
│
└── research-shared-hub/               # YOUR Shared Hub
    ├── .fis3.1/                       # FIS 3.1 shared infrastructure
    │   ├── lib/                       # Python libraries
    │   ├── memories/                  # Shared memory
    │   ├── skills/                    # Skill registry
    │   ├── heartbeat/                 # Heartbeat status
    │   └── experimental/              # Phase 2/3 framework
    └── tickets/                       # Task tickets
        ├── active/
        ├── completed/
        └── archive/
```

---

## Design Principles

### 1. Zero Core File Pollution (零污染 Core Files)
```
❌ Never modify:
   - Other agents' MEMORY.md, HEARTBEAT.md
   - openclaw.json (main config)

✅ Only add to:
   - research-shared-hub/.fis3.1/ (shared infrastructure)
   - workspace/.fis3.1/ (agent extension)
```

### 2. Layered Isolation (分层隔离)
| Layer | Scope | Access Rule |
|-------|-------|-------------|
| L1 Core Files | `*/MEMORY.md` | Agent-local only |
| L2 Agent Workspace | `workspace-*/` | Agent-local only |
| L3 Shared Hub | `research-*/` | Controlled shared access |
| L4 FIS Extension | `*/.fis3.1/` | Agent-independent |

### 3. File-First Architecture (纯文件机制)
- No new services/processes
- 100% file system operations
- Auditable and recoverable

---

## Comparison: FIS 3.0 vs 3.1 Lite

| Feature | FIS 3.0 | FIS 3.1 Lite |
|---------|---------|--------------|
| Task Tickets | ✅ Basic format | ✅ Enhanced (backward compatible) |
| Shared Memory | ❌ None | ✅ Tiered storage |
| Deadlock Detection | ❌ None | ✅ DFS detection |
| Skill Discovery | ❌ Hard-coded | ✅ Dynamic registry |
| SubAgent | ❌ None | ✅ Badge system |
| Core File Pollution | - | ✅ Zero pollution |
| New Services | - | None (file-based) |

---

## Security Note

This Skill contains system administration scripts for:
- Multi-agent workspace lifecycle management
- File system maintenance (cleanup expired memories)
- Task deadlock detection

Some antivirus software may flag automation scripts as suspicious. All code is open-source and auditable with no malicious behavior.

**Operational Notes:**
- SubAgent `terminate()` permanently deletes `workspace-subagent_{id}/` folders
- Backup important data before initialization
- Review `subagent_lifecycle.py` to confirm deletion scope

---

## Changelog

### 2026-02-18: v3.1.2 Generalization
- Removed personal configuration examples
- Removed unrelated utilities (tts_edge)
- All examples now use generic placeholders
- Added data isolation notice

### 2026-02-18: Phase 2/3 Framework
- Knowledge graph framework ready
- Gating controller with RBAC
- Retrieval orchestrator with access control

### 2026-02-17: FIS 3.1 Lite Initial Deploy
- Deployed memory_manager, deadlock_detector, skill_registry
- Deployed subagent_lifecycle + badge system
- Example skills registered

### 2026-02-17: Badge Image Generation
- Added `generate_badge_image()` PNG generation
- Batch support via `generate_multi_badge_image()`
- Compatible badge layouts

### 2026-02-17: SubAgent Auto-Cleanup
- `terminate()` auto-deletes workspace folders
- Added `cleanup_all_terminated()` batch method

---

## File Locations

```
~/.openclaw/workspace/skills/fis-architecture/
├── SKILL.md                    # This file
├── QUICK_REFERENCE.md          # Quick reference
├── package.json                # ClawHub metadata
├── lib/                        # Python libraries (deployed to shared hub)
│   ├── memory_manager.py
│   ├── deadlock_detector.py
│   ├── skill_registry.py
│   ├── subagent_lifecycle.py
│   ├── badge_image_pil.py
│   └── badge_generator.py
├── examples/                   # Usage examples
│   ├── init_fis31.py
│   ├── subagent_pipeline.py
│   └── generate_badges.py
└── system/                     # System scripts
    ├── fis_maintenance.sh
    ├── fis_cleanup_redundancy.sh
    └── fis_subagent_cleanup.py
```

---

*FIS 3.1 Lite — Quality over Quantity*  
*Designed by CyberMao 🐱⚡*
