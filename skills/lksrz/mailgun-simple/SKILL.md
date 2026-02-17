---
name: mailgun-simple
description: Send outbound emails via the Mailgun API. REQUIRED: MAILGUN_API_KEY. Built for AI Commander.
metadata: {
  "author": "Skippy & Lucas (AI Commander)",
  "homepage": "https://aicommander.dev",
  "env": {
    "MAILGUN_API_KEY": { "description": "Your private Mailgun API key. REQUIRED.", "required": true },
    "MAILGUN_DOMAIN": { "description": "Your verified sending domain (default: aicommander.dev).", "default": "aicommander.dev" },
    "MAILGUN_REGION": { "description": "The API region, either US or EU (default: EU).", "default": "EU" },
    "MAILGUN_FROM": { "description": "Default sender address (default: Postmaster <postmaster@domain>)." }
  },
  "openclaw": {
    "requires": { "bins": ["node"] },
    "install": [
      {
        "id": "npm-deps",
        "kind": "exec",
        "command": "npm install mailgun.js form-data",
        "label": "Install Mailgun SDK dependencies"
      }
    ]
  }
}
---

# Mailgun Simple

Send outbound emails using the official Mailgun JS SDK. 

## 🚨 Security & Setup

This skill is environment-driven and does **not** load external .env files. It relies strictly on the environment variables provided by the caller.

### Environment Variables
- `MAILGUN_API_KEY`: Your private Mailgun API key. **REQUIRED.**
- `MAILGUN_DOMAIN`: Your verified sending domain (default: `aicommander.dev`).
- `MAILGUN_REGION`: The API region, either `US` or `EU` (default: `EU`).

## Tools

### Send Email
Sends a plain text email to a recipient.
```bash
MAILGUN_API_KEY=xxx MAILGUN_DOMAIN=example.com MAILGUN_REGION=EU node scripts/send_email.js <to> <subject> <text> [from]
```

## Runtime Requirements
Requires: `mailgun.js`, `form-data`, and `node`.
