---
name: publora-twitter
description: >
  Post or schedule content to X (Twitter) using the Publora API. Use this skill
  when the user wants to tweet, schedule a tweet, or post a thread to X/Twitter via Publora.
---

# Publora — X / Twitter

Post and schedule X/Twitter content via the Publora API.

> **Prerequisite:** Install the `publora` core skill for auth setup and getting platform IDs.

## Get Your Twitter Platform ID

```bash
GET https://api.publora.com/api/v1/platform-connections
# Look for entries like "twitter-123456"
```

## Tweet Immediately

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Just shipped something exciting. More soon. 👀',
    platforms: ['twitter-123456']
  })
});
```

## Schedule a Tweet

```javascript
await fetch('https://api.publora.com/api/v1/create-post', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' },
  body: JSON.stringify({
    content: 'Hot take: most productivity advice is just procrastination in disguise.',
    platforms: ['twitter-123456'],
    scheduledTime: '2026-03-16T14:00:00.000Z'
  })
});
```

## Tweet with Image

```python
import requests

HEADERS = { 'Content-Type': 'application/json', 'x-publora-key': 'sk_YOUR_KEY' }

post = requests.post('https://api.publora.com/api/v1/create-post', headers=HEADERS, json={
    'content': 'New dashboard dropped 🎉',
    'platforms': ['twitter-123456'],
    'scheduledTime': '2026-03-16T14:00:00.000Z'
}).json()

upload = requests.post('https://api.publora.com/api/v1/get-upload-url', headers=HEADERS, json={
    'fileName': 'dashboard.png', 'contentType': 'image/png',
    'type': 'image', 'postGroupId': post['postGroupId']
}).json()

with open('dashboard.png', 'rb') as f:
    requests.put(upload['uploadUrl'], headers={'Content-Type': 'image/png'}, data=f)
```

## Cross-post to X + LinkedIn

```javascript
body: JSON.stringify({
  content: 'Your content here',
  platforms: ['twitter-123456', 'linkedin-ABC123'],
  scheduledTime: '2026-03-16T10:00:00.000Z'
})
```

## Tips for X/Twitter

- **Character limit:** 280 characters (longer with X Premium subscription)
- **Best times:** Weekdays 8 AM–4 PM, peak at 12 PM
- **Hooks:** First sentence must grab — most users don't click "show more"
- **Images:** 2 or 4 images perform better than 1 or 3 (grid layout)
- **Hashtags:** 1–2 max on X; more looks spammy
