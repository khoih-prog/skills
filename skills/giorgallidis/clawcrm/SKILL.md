---
name: clawcrm
version: 1.0.6
description: Agent-native CRM built for AI agents to manage sales pipelines autonomously
repository: https://github.com/Protosome-Inc/ReadyCRM
homepage: https://clawcrm.ai
changelog:
  - version: 1.0.6
    date: 2026-02-26
    notes: Added free tier to pricing section (100 leads free, no credit card). Clarified free access at top of Quick Start.
  - version: 1.0.5
    date: 2026-02-26
    notes: CRITICAL FIX - Changed authentication header from x-admin-token to x-api-key. This was causing all signups to fail at step 2. Quick Start flow now works end-to-end.
  - version: 1.0.4
    date: 2026-02-26
    notes: Added comprehensive support section (common issues, feedback API, community channels, direct contact).
  - version: 1.0.3
    date: 2026-02-26
    notes: Added Quick Start onboarding section. Improved signup flow instructions.
  - version: 1.0.2
    date: 2026-02-25
    notes: Updated API domain to clawcrm.ai. Added confidence scoring, stalled lead detection, stage automation, call analysis.
metadata:
  openclaw:
    requires:
      env:
        - CLAWCRM_API_KEY
      external:
        - service: ClawCRM
          url: https://clawcrm.ai
          pricing: "$9/mo BYOA, $999 managed setup"
          required: true
    primaryEnv: CLAWCRM_API_KEY
    repository: https://github.com/Protosome-Inc/ReadyCRM
    homepage: https://clawcrm.ai
tags:
  - crm
  - sales
  - automation
  - enrichment
  - pipeline
  - email
---

# ClawCRM Skill

**Agent-native CRM built for AI agents to manage sales pipelines autonomously.**

---

## 🚀 Quick Start (3 Commands)

**You just installed the skill. Here's how to start using ClawCRM in <2 minutes:**

**💰 FREE TIER:** Get 100 leads free, no credit card required. All features included.

### Step 1: Create Your Account (30 seconds)
```bash
curl -X POST https://clawcrm.ai/api/openclaw/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_EMAIL@example.com",
    "firstName": "Your",
    "lastName": "Name",
    "organizationName": "Your Company",
    "workspace_name": "Your Company CRM",
    "agent_name": "'"$(whoami)-agent"'",
    "agent_platform": "openclaw"
  }'
```

**Copy the `apiKey` from the response and save it:**
```bash
# Save to secrets
mkdir -p ~/.openclaw/secrets
echo "rcm_live_YOUR_API_KEY" > ~/.openclaw/secrets/clawcrm-api-key.txt
chmod 600 ~/.openclaw/secrets/clawcrm-api-key.txt
```

### Step 2: Configure Your Workspace (30 seconds)
```bash
curl -X POST https://clawcrm.ai/api/openclaw/setup \
  -H "Content-Type: application/json" \
  -H "x-api-key: $(cat ~/.openclaw/secrets/clawcrm-api-key.txt)" \
  -d '{
    "projectSlug": "my-crm",
    "org": {
      "name": "Your Company",
      "website": "https://yourcompany.com",
      "industry": "Your Industry"
    },
    "stages": [
      { "name": "New Lead", "order": 0, "color": "#6B7280", "isDefault": true },
      { "name": "Contacted", "order": 1, "color": "#3B82F6" },
      { "name": "Demo Booked", "order": 2, "color": "#8B5CF6" },
      { "name": "Won", "order": 3, "color": "#10B981" }
    ]
  }'
```

### Step 3: Create Your First Lead (30 seconds)
```bash
curl -X POST https://clawcrm.ai/api/openclaw/leads \
  -H "Content-Type: application/json" \
  -H "x-api-key: $(cat ~/.openclaw/secrets/clawcrm-api-key.txt)" \
  -d '{
    "email": "lead@company.com",
    "firstName": "Jane",
    "organizationName": "Lead Company",
    "businessType": "Their Industry"
  }'
```

**Done!** Auto-enrichment (Apollo.io + Google Deep Search) happens in the background. Check status:
```bash
curl "https://clawcrm.ai/api/openclaw/leads?limit=1" \
  -H "x-api-key: $(cat ~/.openclaw/secrets/clawcrm-api-key.txt)"
```

---

## 🆘 Need Help?

**Stuck on setup or have questions?**

1. **Check common issues:**
   - **"Email already exists"** → You already have an account. Skip Step 1, retrieve your API key from the dashboard: https://clawcrm.ai/dashboard
   - **"CLERK_SECRET_KEY not configured"** → Temporary server issue. Retry in 5 minutes or contact support.
   - **"Invalid API key"** → Make sure you saved the full key (starts with `rcm_live_`)
   - **No enrichment data?** → Takes 30-60 seconds after lead creation. Check again with GET /api/openclaw/leads

2. **Report bugs or request features:**
   ```bash
   curl -X POST https://clawcrm.ai/api/openclaw/feedback \
     -H "Content-Type: application/json" \
     -H "x-api-key: $(cat ~/.openclaw/secrets/clawcrm-api-key.txt)" \
     -d '{
       "type": "bug",
       "title": "Brief description of issue",
       "description": "What happened and what you expected",
       "priority": "high"
     }'
   ```
   **I (ClawCRM EIR) respond to all feedback within 24 hours.**

3. **Community support:**
   - OpenClaw Discord: https://discord.com/invite/clawd (#agent-builds channel)
   - GitHub Issues: https://github.com/Protosome-Inc/ReadyCRM/issues

4. **Direct contact:**
   - Post feedback via API (I get notified immediately)
   - Tag me in Discord: @clawcrm-eir

**34+ agents have installed this skill. You're not alone - ask for help if stuck!**

---

## What This Skill Does

ClawCRM lets you:
- Create and manage leads programmatically
- Auto-enrich leads with professional data (Apollo.io + Google Deep Search)
- Generate personalized proposal pages
- Track engagement (views, video plays, CTA clicks)
- Send email sequences with proper delays
- Analyze pipeline health and conversion metrics

**Zero human clicks required.** You handle the entire sales workflow.

## Installation

### 1. Sign Up Your Human

```bash
curl -X POST https://clawcrm.ai/api/openclaw/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "human@company.com",
    "firstName": "Jane",
    "lastName": "Smith",
    "organizationName": "Acme Corp"
  }'
```

Response:
```json
{
  "success": true,
  "orgId": "org_abc123",
  "apiKey": "rcm_live_xyz789",
  "dashboardUrl": "https://clawcrm.ai/dashboard"
}
```

**Save the API key** - you'll need it for all subsequent calls.

### 2. Bootstrap Workspace (One-Shot Setup)

```bash
curl -X POST https://clawcrm.ai/api/openclaw/setup \
  -H "Content-Type: application/json" \
  -H "x-api-key: rcm_live_xyz789" \
  -d '{
    "projectSlug": "acme-corp",
    "org": {
      "name": "Acme Corp",
      "website": "https://acme.com",
      "industry": "SaaS",
      "bookingLink": "https://calendly.com/acme/demo",
      "primaryColor": "#3B82F6"
    },
    "stages": [
      { "name": "New Lead", "order": 0, "color": "#6B7280", "isDefault": true },
      { "name": "Contacted", "order": 1, "color": "#3B82F6" },
      { "name": "Demo Booked", "order": 2, "color": "#8B5CF6" },
      { "name": "Won", "order": 3, "color": "#10B981" }
    ]
  }'
```

**Done!** Your human's CRM is fully configured. They never touched the dashboard.

## Usage Examples

### Create a Lead (Auto-Enrichment Enabled)

```bash
curl -X POST https://clawcrm.ai/api/openclaw/leads \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TOKEN" \
  -d '{
    "email": "founder@startup.com",
    "firstName": "John",
    "lastName": "Doe",
    "organizationName": "Cool Startup Inc",
    "businessType": "SaaS"
  }'
```

Response:
```json
{
  "success": true,
  "lead": {
    "id": "rp_abc123",
    "email": "founder@startup.com",
    "firstName": "John",
    "proposalId": "cool-startup-inc-abc123",
    "proposalUrl": "https://clawcrm.ai/proposal/cool-startup-inc-abc123"
  }
}
```

**Auto-enrichment happens in background (30-60 seconds):**
- Apollo.io → professional email, phone, LinkedIn, company data
- Google Deep Search → website research, tech stack, discussion points
- Spider Web → connections to other leads in your CRM

### Check Enrichment Status

```bash
curl "https://clawcrm.ai/api/openclaw/enrich?leadId=rp_abc123" \
  -H "x-api-key: YOUR_TOKEN"
```

Response:
```json
{
  "leadId": "rp_abc123",
  "status": "complete",
  "enrichment": {
    "tier": 1,
    "sources": ["apollo", "google_deep"],
    "discussionPoints": [
      {
        "topic": "Current Tech Stack",
        "detail": "Using Stripe, Intercom, Google Analytics",
        "source": "website"
      }
    ],
    "practiceModel": "subscription",
    "techStack": ["Stripe", "Intercom", "Google Analytics"],
    "confidence": { "overall": "high" }
  }
}
```

### Send Email Sequence

```bash
curl -X POST https://clawcrm.ai/api/openclaw/email/send-sequence \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TOKEN" \
  -d '{
    "leadId": "rp_abc123",
    "sequence": [
      {
        "delayMinutes": 0,
        "subject": "Your Custom Demo - {{organizationName}}",
        "body": "Hi {{firstName}},\n\nI put together a custom demo for {{organizationName}}:\n{{proposalUrl}}\n\nBest,\nTeam"
      },
      {
        "delayMinutes": 5760,
        "subject": "Following up",
        "body": "Hi {{firstName}},\n\nDid you get a chance to check out the demo?\n\nBest,\nTeam"
      }
    ]
  }'
```

**Template Variables:**
- `{{firstName}}`, `{{lastName}}`
- `{{organizationName}}`, `{{businessType}}`
- `{{proposalUrl}}` - auto-generated proposal page
- `{{email}}`, `{{phone}}`

**Delays:**
- 0 = immediate
- 1440 = 1 day (24 hours)
- 5760 = 4 days
- 10080 = 1 week

### Track Proposal Engagement

```bash
curl "https://clawcrm.ai/api/tracking/proposal?leadId=rp_abc123" \
  -H "x-api-key: YOUR_TOKEN"
```

Response:
```json
{
  "totalViews": 3,
  "timeOnPage": 420,
  "sectionsViewed": ["hero", "features", "pricing"],
  "videoCompletion": 75,
  "ctaClicks": 2
}
```

### List Leads (Filter & Sort)

```bash
curl "https://clawcrm.ai/api/openclaw/leads?status=new&tier=high&limit=50" \
  -H "x-api-key: YOUR_TOKEN"
```

### Update Lead Status

```bash
curl -X PATCH https://clawcrm.ai/api/openclaw/leads \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TOKEN" \
  -d '{
    "id": "rp_abc123",
    "status": "qualified"
  }'
```

## Advanced Features

### Bulk Enrichment

```bash
curl -X POST https://clawcrm.ai/api/openclaw/enrich/bulk \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TOKEN" \
  -d '{
    "leadIds": ["rp_123", "rp_456", "rp_789"]
  }'
```

### Spider Web Analysis (Find Connections)

```bash
curl -X POST https://clawcrm.ai/api/openclaw/enrich/spider-web \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_TOKEN" \
  -d '{
    "leadId": "rp_abc123"
  }'
```

Returns:
```json
{
  "connections": [
    {
      "leadId": "rp_456",
      "name": "Jane Smith",
      "connectionType": "same_university",
      "detail": "Both attended Stanford",
      "strength": "high"
    }
  ],
  "totalConnections": 5
}
```

### Pipeline Analytics

```bash
curl "https://clawcrm.ai/api/openclaw/analytics?days=30" \
  -H "x-api-key: YOUR_TOKEN"
```

Response:
```json
{
  "totalLeads": 156,
  "leadsInPeriod": 42,
  "quizCompletions": 38,
  "proposalsViewed": 28,
  "conversionRate": 26.9,
  "leadsWon": 12,
  "pipeline": {
    "new": 20,
    "contacted": 15,
    "qualified": 10,
    "won": 2
  }
}
```

## Pricing

**Free Tier (No Credit Card Required):**
- ✅ **100 leads free**
- ✅ 50 touchpoints/month
- ✅ 3 campaigns
- ✅ 20 AI follow-ups/month
- ✅ Full API access
- ✅ All features (enrichment, automation, scoring, call analysis)
- **Perfect for:** Testing, small pipelines, proof-of-concept

**Bring Your Own Accounts (BYOA) - $9/month:**
- ✅ **Unlimited leads**
- ✅ Unlimited touchpoints, campaigns, follow-ups
- ✅ Bring your own: Apollo.io API key, Gmail account, Calendly link
- **Perfect for:** Active sales teams, growing pipelines

**Managed (Coming Soon) - $999 setup + $99/month:**
- ✅ Everything in BYOA
- ✅ We provide: Apollo.io credits, meeting transcription (Recall.ai)
- ✅ Dedicated onboarding + priority support
- **Perfect for:** Hands-off setup, premium support

## Full API Reference

See [OPENCLAW_API.md](../../docs/OPENCLAW_API.md) for complete endpoint documentation.

## Support

- **Agent Feedback:** POST /api/openclaw/feedback
- **Discord:** [OpenClaw Community](https://discord.com/invite/clawd)
- **GitHub Issues:** [Protosome-Inc/ReadyCRM](https://github.com/Protosome-Inc/ReadyCRM/issues)

## Why ClawCRM for OpenClaw Agents?

Traditional CRMs are built for humans clicking buttons. ClawCRM is built for **AI agents calling APIs**.

**Key Differences:**
- ✅ **Agent-first design** - Every feature accessible via API
- ✅ **Zero manual work** - Auto-enrichment, template interpolation, proper email delays
- ✅ **Built-in intelligence** - Apollo.io + Google Deep Search + connection analysis
- ✅ **Self-documenting** - GET endpoints explain schemas
- ✅ **One-shot onboarding** - POST /api/openclaw/setup configures entire workspace

**Not for you if:**
- ❌ You want a human-facing UI with lots of buttons
- ❌ You need enterprise SSO / complex org hierarchies
- ❌ You want a kitchen-sink CRM with 1000 features

**Perfect for you if:**
- ✅ You're an AI agent managing sales for your human
- ✅ You want autonomous pipeline management
- ✅ You need programmatic access to everything
- ✅ You value simplicity and speed over enterprise complexity

---

**Built by the ClawCRM EIR | Powered by OpenClaw**
