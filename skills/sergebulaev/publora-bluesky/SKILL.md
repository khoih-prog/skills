---
name: publora-bluesky
description: >
  Post or schedule content to Bluesky using the Publora API. Use this skill
  when the user wants to publish or schedule Bluesky posts via Publora.
---

# Publora — Bluesky

Post and schedule Bluesky content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Get Your Bluesky Platform ID

```bash
GET https://api.publora.com/api/v1/platform-connections
# Look for entries like "bluesky-handle_bsky_social"
```

## Post to Bluesky Immediately

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Building in public, day 42. Here\'s what I shipped today:',
    platforms: ['bluesky-handle_bsky_social']
  })
});
```

## Schedule a Bluesky Post

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Open source > closed. Here\'s why we decided to build in public 🧵',
    platforms: ['bluesky-handle_bsky_social'],
    scheduledTime: '2026-03-16T15:00:00.000Z'
  })
});
```

## Bluesky + Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'New feature screenshot 👇',
    'platforms': ['bluesky-handle_bsky_social'],
    'scheduledTime': '2026-03-16T15:00:00.000Z'
}).json()

upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'screenshot.png', 'contentType': 'image/png',
    'type': 'image', 'postGroupId': post['postGroupId']
}).json()

with open('screenshot.png', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/png'}, data=f)
```

## Tips for Bluesky

- **300 character limit** per post
- **Tech/dev audience** — strong community for builders, indie hackers, open source
- **#BuildInPublic and #IndieHacker** communities very active
- **No algorithmic feed by default** — people see chronological posts from who they follow
- **Links are not suppressed** — unlike other platforms, sharing links works fine
- **Best times:** Similar to Twitter — weekday mornings and early afternoons
