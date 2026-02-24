# Agent Roles — Capabilities & Responsibilities

## Overview

The system includes 7 specialized agents organized in a star topology:

| Agent | Role | Key Strength |
|-------|------|-------------|
| Leader | Orchestrator | Task decomposition, quality control, owner communication |
| Researcher | Research Analyst | Web research, competitive analysis, trend identification |
| Content | Content Strategist | Multi-language copywriting, brand voice adaptation |
| Designer | Visual Designer | Art direction, image generation, visual briefs |
| Operator | Ops Coordinator | Browser automation, platform UI operations |
| Engineer | Full-Stack Engineer | Code, automation, API integration, CLI tools |
| Reviewer | Quality Reviewer | Independent cross-model quality assessment |

## Detailed Profiles

### Leader
- **Access**: Full workspace, Telegram binding, sessions_send to all agents
- **Restrictions**: No exec, no browser
- **Unique abilities**: Only agent with owner access; owns shared/ writes; manages approval queue
- **Model recommendation**: High-reasoning model (e.g., Opus)

### Researcher
- **Access**: Own workspace, shared/ (read), web search/fetch
- **Restrictions**: No exec, no browser, no code execution
- **Output**: Structured briefs with confidence levels and sources
- **Model recommendation**: High-reasoning model (e.g., Opus)

### Content
- **Access**: Own workspace, shared/ (read), web search
- **Restrictions**: No exec, no code editing, no browser, no publishing
- **Output**: Platform-formatted content with variations, tagged [PENDING APPROVAL]
- **Model recommendation**: Fast capable model (e.g., Sonnet)

### Designer
- **Access**: Own workspace, shared/ (read), web search, image generation tools
- **Restrictions**: No exec, no code editing, no browser, no publishing
- **Output**: Visual briefs + generated images, tagged [PENDING APPROVAL]
- **Workflow**: Brief-first — always writes a structured brief before generating
- **Model recommendation**: Fast capable model (e.g., Sonnet)

### Operator
- **Access**: Own workspace, shared/ (read), browser (CDP + screen automation)
- **Restrictions**: No exec, no code editing
- **Output**: Execution confirmations with screenshots, extracted data
- **Model recommendation**: Fast capable model (e.g., Sonnet)

### Engineer
- **Access**: Own workspace + exec, shared/ (read + errors/ write)
- **Restrictions**: No browser
- **Output**: Working code with tests, tagged [PENDING REVIEW]
- **Model recommendation**: Fast capable model (e.g., Sonnet)

### Reviewer
- **Access**: Read-only everywhere, web fetch for fact-checking
- **Restrictions**: No write, no exec, no edit, no browser — fully sandboxed
- **Output**: Structured verdicts ([APPROVE] or [REVISE])
- **Unique**: Deliberately uses a different model family for independent perspective
- **Model recommendation**: Different provider than main agents (for independence)

## Tools Denied Matrix

| Tool | Leader | Researcher | Content | Designer | Operator | Engineer | Reviewer |
|------|--------|-----------|---------|----------|----------|----------|----------|
| exec | X | X | X | X | X | - | X |
| edit | - | - | - | - | X | - | X |
| apply_patch | - | - | X | X | X | - | X |
| write | - | - | - | - | - | - | X |
| browser | X | X | X | X | - | X | X |

`X` = denied, `-` = allowed

## Team Configurations

### Full Team (7 agents) — Recommended
All agents active. Best for multi-brand operations with high content volume.

### Lean Team (4 agents)
Leader + Content + Designer + Engineer. Suitable for single-brand or low-volume operations. Research handled by Leader; no independent review; no browser automation.

### Custom
Select any combination. Leader is always required.
