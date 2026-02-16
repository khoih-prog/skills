# SkipUp Meeting Scheduler — OpenClaw Skill

An OpenClaw skill that lets AI agents schedule, manage, and cancel meetings through the SkipUp API.

## What it does

SkipUp is an AI-powered meeting coordinator. When you create a meeting request, SkipUp reaches out to all participants via email, collects their availability across timezones, and books the optimal meeting time automatically. This skill wraps that API so agents can trigger the process programmatically.

## Setup

### 1. Get a SkipUp API key

Sign up at [skipup.ai](https://skipup.ai) and generate an API key from your workspace settings. The key needs `meeting_requests.read`, `meeting_requests.write`, and `members.read` scopes.

### 2. Set the environment variable

```bash
export SKIPUP_API_KEY="sk_live_your_key_here"
```

### 3. Install the skill

```bash
clawhub install skipup-meeting-scheduler
```

## Usage

Once installed, your agent can:

- **Schedule meetings** — provide an organizer email, participant emails, and optional context (title, purpose, duration, timeframe)
- **Cancel meetings** — cancel an active or paused request, optionally notifying participants
- **Pause and resume** — temporarily pause coordination, then resume when ready
- **Check status** — look up a meeting request by ID to see if it's active, booked, paused, or cancelled
- **List meetings** — view all meeting requests with filtering by status, organizer, participant, or date range
- **List workspace members** — verify someone is a workspace member before using them as an organizer

## Capabilities

| Action | Endpoint | Scope |
|---|---|---|
| Create meeting | `POST /api/v1/meeting_requests` | `meeting_requests.write` |
| Cancel meeting | `POST /api/v1/meeting_requests/:id/cancel` | `meeting_requests.write` |
| Pause meeting | `POST /api/v1/meeting_requests/:id/pause` | `meeting_requests.write` |
| Resume meeting | `POST /api/v1/meeting_requests/:id/resume` | `meeting_requests.write` |
| List meetings | `GET /api/v1/meeting_requests` | `meeting_requests.read` |
| Get meeting | `GET /api/v1/meeting_requests/:id` | `meeting_requests.read` |
| List members | `GET /api/v1/workspace_members` | `members.read` |

## Requirements

- A SkipUp account with an active workspace
- An API key with `meeting_requests.read`, `meeting_requests.write`, and `members.read` scopes
- The organizer email must belong to an active workspace member

## Publishing to ClawHub

Authenticate (one-time):

```bash
clawhub login
```

Publish a new version:

```bash
clawhub publish services/openclaw-skill/skipup-meeting-scheduler/ \
  --slug skipup-meeting-scheduler \
  --name "SkipUp Meeting Scheduler" \
  --version 1.1.0 \
  --changelog "7 actions: create, cancel, pause, resume, list meetings, get meeting, list members. Three-tier architecture with reference files." \
  --tags latest,scheduling,meetings,productivity,calendar
```

Bump the `--version` and `--changelog` for each release. Run from the repo root after merging to main.

## Documentation

- [Setup and usage guide](https://support.skipup.ai/integrations/openclaw/)
- [API reference](https://support.skipup.ai/api/meeting-requests/)
- [SkipUp llms.txt](https://skipup.ai/llms.txt)
- [About SkipUp](https://blog.skipup.ai/llm/index)

## License

MIT
