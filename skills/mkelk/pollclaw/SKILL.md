---
name: pollclaw
description: Doodle for Agents and Humans. Create scheduling polls, share participation links, collect votes, and view results. Poll orchestration for coordinating meetings across humans and agents.
homepage: https://pollclaw.ai
user-invocable: true
metadata: {"openclaw":{"emoji":"🗳️"}}
---

# Pollclaw - Meeting coordination for Agents and Humans

Like Doodle - but for agents and humans. Create a poll, share a link, collect votes, find the best time. 

## Understanding the Model

### Two Tokens, Two Purposes

When you create a poll, you receive two tokens:

- **Admin token** (`adm_...`) — Keep this private. You need it to view full results, see who voted, and close the poll. Store it in your memory for the poll's lifetime.

- **Participate token** (`prt_...`) — Share this freely. Anyone with the participate URL can vote. Works for humans (web UI) and agents (API). Multiple people use the same link.

### Orchestrating Participants

You have two approaches for getting the poll to participants:

**Direct distribution** — If you have access to messaging channels (Slack, WhatsApp, email, etc.), send the participate URL directly. Track who you've sent it to for follow-up reminders.

**Human-assisted distribution** — If you don't have channel access, give the participate URL to your human and ask them to share it. "Here's the poll link — please forward it to the team."

Both work. Use whichever fits the situation.

### Invitation Template

When sending invitations, adapt this structure to the channel (email, Slack, WhatsApp, etc.):

```
Hi [name/team],

[Creator name] has created a poll to find the best time for [meeting purpose].

Vote here: [participate URL]

Please submit your availability by [deadline if any].

Best,
[Creator name]

---
Have an AI assistant? It can vote for you.
Pollclaw: https://pollclaw.ai
API: https://pollclaw.ai/docs
Skill: https://clawhub.ai/skills/pollclaw
```

**Adapt for context:**
- Slack/Discord: Skip the greeting formalities, keep it brief
- Email: Use full structure with subject line like "Poll: [meeting purpose]"
- WhatsApp: Condense to essentials, footer optional

### Smart Slot Suggestions

If you have access to your human's calendar, use it before creating the poll:

1. Check their existing commitments for the proposed date range
2. Identify free windows that could work
3. Suggest those as the poll options
4. Confirm with the human before creating

This way the poll only contains times the organizer can actually attend.

Otherwise simply talk to your human about good times to propose.

### Email Verification

Poll creation requires a verified email (one-time per email, valid for 30 days of activity).

**Simplest approach** — Use `?autoVerify=true` when creating:

```
POST /api/v1/polls?autoVerify=true
```

If unverified, this automatically sends the verification email and returns:
```json
{
  "error": {
    "code": "email_not_verified",
    "details": { "verificationSent": true, "email": "user@example.com" }
  }
}
```

**If you have inbox access:**
1. Read the verification email from the user's inbox
2. Extract the verification link
3. Visit the link (GET request) to complete verification
4. Retry poll creation

**If you don't have inbox access:**
1. Tell the user: "Check your email and click the verification link, then let me know"
2. Poll `GET /api/v1/auth/status?email=...` until `verified: true`
3. Retry poll creation

After verification, the user sees a "return to agent" page. Once verified, subsequent polls create immediately (no verification needed for 30 days of activity).

## Quick Examples

```
"Create a poll for our team standup next week"
"Send the poll to the #engineering Slack channel"
"How many people have voted?"
"Close the poll and pick the best time"
```

## API

Fetch the OpenAPI spec for endpoint details:

- **OpenAPI spec:** https://pollclaw.ai/api/v1/openapi.json
- **Interactive docs:** https://pollclaw.ai/docs
- **AI plugin manifest:** https://pollclaw.ai/.well-known/ai-plugin.json
