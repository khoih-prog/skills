---
name: skipup-meeting-scheduler
description: Schedule, check on, pause, resume, and cancel meetings through SkipUp's AI-powered coordination. Use when a user asks to schedule, check on, pause, resume, or cancel a meeting, look up workspace members, or verify someone is a workspace member. SkipUp coordinates via email — it does not instant-book.
metadata: { "openclaw": { "emoji": "📅", "primaryEnv": "SKIPUP_API_KEY", "requires": { "env": ["SKIPUP_API_KEY"] } } }
---

# SkipUp Meeting Scheduler

SkipUp is an AI-powered scheduling coordinator. When you create a meeting request, SkipUp emails all participants, collects availability across timezones, and books the optimal time automatically. This is an asynchronous process — creating a request does not instantly book a meeting.

## Authentication

Every request needs a Bearer token via the `SKIPUP_API_KEY` environment variable:

```
Authorization: Bearer $SKIPUP_API_KEY
```

The key must have `meeting_requests.read`, `meeting_requests.write`, and `members.read` scopes. Never hardcode it.

## Create a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests
```

Returns **202 Accepted**. SkipUp will coordinate asynchronously via email.

### Example request

```json
{
  "organizer_email": "sarah@acme.com",
  "participants": [
    { "email": "alex@example.com", "name": "Alex Chen", "timezone": "America/New_York" }
  ],
  "context": {
    "title": "Product demo",
    "purpose": "Walk through new dashboard features",
    "duration_minutes": 30
  }
}
```

Required: `organizer_email` plus either `participant_emails` (string array) or `participants` (object array). Provide one format, not both.

### Example response

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "sarah@acme.com",
    "participant_emails": ["alex@example.com"],
    "status": "active",
    "title": "Product demo",
    "created_at": "2026-02-15T10:30:00Z"
  }
}
```

### What to tell the user

The meeting request has been created. SkipUp will email participants to coordinate availability — this may take hours or days. They'll receive a calendar invite once a time is confirmed.

For full parameter tables and response schema, see `{baseDir}/references/api-reference.md`.

## Cancel a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests/:id/cancel
```

Only works on `active` or `paused` requests.

### Example request

```json
{
  "notify": true
}
```

Set `notify: true` to email cancellation notices to participants. Defaults to `false`.

### What to tell the user

The meeting request has been cancelled. If `notify` was true, participants will be notified by email. If false, no one is contacted.

For full details, see `{baseDir}/references/api-reference.md`.

## Pause a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests/:id/pause
```

Pauses an active meeting request. No request body required. Only works on `active` requests.

### Example request

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ.../pause \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

The meeting request has been paused. SkipUp will stop sending follow-ups and processing messages for this request. Participants are not notified. You can resume it at any time.

## Resume a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests/:id/resume
```

Resumes a paused meeting request. No request body required. Only works on `paused` requests.

### Example request

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ.../resume \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

The meeting request has been resumed. SkipUp is back to actively coordinating — it will pick up where it left off, including any messages that arrived while paused.

For full details, see `{baseDir}/references/api-reference.md`.

## List meeting requests

```
GET https://api.skipup.ai/api/v1/meeting_requests
```

Returns a paginated list of meeting requests, newest first. Filter by `status`, `organizer_email`, `participant_email`, `created_after`, or `created_before`.

### Example request

```bash
curl "https://api.skipup.ai/api/v1/meeting_requests?status=active&limit=10" \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

Here are the meeting requests matching your filters. If there are more results, tell the user and offer to fetch the next page.

## Get a meeting request

```
GET https://api.skipup.ai/api/v1/meeting_requests/:id
```

Retrieves a single meeting request by ID.

### Example request

```bash
curl https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ... \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

Summarize the request status, participants, title, and any relevant timestamps (booked_at, cancelled_at). If active, remind them that SkipUp is still coordinating.

## List workspace members

```
GET https://api.skipup.ai/api/v1/workspace_members
```

Returns a paginated list of active workspace members. Filter by `email` or `role`.

### Example request

```bash
curl "https://api.skipup.ai/api/v1/workspace_members?email=sarah@acme.com" \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

Show the matching members. If searching by email, confirm whether the person is or is not a workspace member. This is useful as a pre-check before creating meeting requests.

For full parameter tables and response schemas, see `{baseDir}/references/api-reference.md`.

## Key rules

1. **Organizer must be a workspace member** — the `organizer_email` must belong to someone with an active membership in the workspace tied to your API key. External emails are rejected.
2. **Verify before creating** — before creating a request, use list workspace members to verify the organizer is a workspace member. This prevents 422 errors.
3. **Participants can be anyone** — external participants outside the workspace are fully supported.
4. **Async, not instant** — creating a request starts email-based coordination. Tell the user it may take time.
5. **Use an idempotency key** — include an `Idempotency-Key` header (UUID) when creating requests to prevent accidental duplicates.
6. **Ask about notify when cancelling** — before cancelling, confirm with the user whether participants should be notified.
7. **Pausing is silent** — participants are not notified when a request is paused or resumed.
8. **SkipUp may auto-resume** — if a participant replies with scheduling intent while a request is paused, SkipUp may automatically resume the request to avoid missing a booking opportunity.

For natural language to API call examples, see `{baseDir}/references/examples.md`.

## Further reading

- Full API reference: https://support.skipup.ai/api/meeting-requests/
- OpenClaw integration guide: https://support.skipup.ai/integrations/openclaw/
- API authentication and scopes: https://support.skipup.ai/api/authentication/
- SkipUp llms.txt: https://skipup.ai/llms.txt
- Learn more about SkipUp: https://blog.skipup.ai/llm/index
