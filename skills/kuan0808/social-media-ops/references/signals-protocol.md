# Signals Protocol — Complete Reference

## Overview

Agents communicate with the Leader using standardized signal tags placed at the top of their responses. Signals drive routing, escalation, and workflow decisions.

## Status Signals

| Signal | Meaning | Leader Action |
|--------|---------|---------------|
| `[READY]` | Complete and confident | Normal quality review |
| `[NEEDS_INFO]` | Needs more context | Gather info, re-brief |
| `[BLOCKED]` | Cannot complete | Assess, try alternative, or escalate |
| `[LOW_CONFIDENCE]` | Delivered but uncertain | Extra scrutiny, consider verification |
| `[SCOPE_FLAG]` | Bigger than expected | Reassess scope with owner |

## Approval Signals

| Signal | Meaning | Used By |
|--------|---------|---------|
| `[APPROVE]` | Meets requirements | Reviewer |
| `[REVISE]` | Material issues, fixes listed | Reviewer |
| `[PENDING APPROVAL]` | Awaiting owner approval | All agents (external content) |
| `[PENDING REVIEW]` | Code awaiting review | Engineer |

## Session Management Signals

| Signal | Meaning | Who Sends |
|--------|---------|-----------|
| `[KB_PROPOSE]` | Proposes shared/ knowledge update | All agents |
| `[MEMORY_DONE]` | Finished writing own memory | All except Reviewer |
| `[CONTEXT_LOST]` | Session compacted, needs context | All agents |

## KB_PROPOSE Format

```
[KB_PROPOSE]
- file: shared/brands/{brand_id}/content-guidelines.md
  action: append
  content: "Audience prefers gentle tone"
  source: revision-feedback
[/KB_PROPOSE]
```

## Rules

1. One primary signal per response
2. `[READY]` is default — may be omitted for clean deliveries
3. Session management signals can accompany a primary signal
4. Signals go at the **top** of the response
5. Signals are for Leader consumption only
