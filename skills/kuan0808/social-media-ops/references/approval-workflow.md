# Approval Workflow — Detailed Reference

## Pipeline

```
[DRAFT] → [PENDING APPROVAL] → [APPROVED] → [SCHEDULED/POSTED]
                ↓                    ↓
            [REVISION]          [REJECTED]
```

## Stage Details

| Stage | Description | Who Acts |
|-------|-------------|----------|
| DRAFT | Agent creates content internally | Content / Designer |
| PENDING APPROVAL | Content presented to owner | Owner reviews |
| APPROVED | Owner confirmed, ready to publish | Engineer / Operator publishes |
| REVISION | Owner requested changes | Content / Designer re-drafts |
| REJECTED | Owner discarded the content | Logged, no further action |
| SCHEDULED/POSTED | Content published | Logged in daily notes |

## Owner Shortcuts

| Shortcut | Action |
|----------|--------|
| `approve` / `lgtm` / `ship it` | Approve most recent pending item |
| `approve all` | Approve all pending items |
| `revise: [feedback]` | Request changes with feedback |
| `reject` / `kill it` / `nah` | Reject most recent pending item |
| `show queue` | List all pending items |

## Rules

1. No content posted without explicit owner approval
2. All external-facing content tagged `[PENDING APPROVAL]`
3. Bulk approval via "approve all"
4. Stale approvals (>48h) flagged during heartbeat
5. Max 2 revision rounds per task
6. Multi-agent rework doesn't bypass approval
7. Route approvals to correct brand topic

## Reviewer Integration

- Leader decides when to invoke Reviewer (not automatic)
- Reviewer provides [APPROVE] or [REVISE]
- Leader evaluates Reviewer feedback as a peer
- Leader may override Reviewer (must document reason)
- Max 2 review rounds
