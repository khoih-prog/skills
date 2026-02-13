---
name: Dashboard
slug: dashboard
description: Build custom dashboards from any data source with local hosting, visual QA loops, and scriptable automation.
---

## When to Use

User wants to visualize data from any source: APIs, databases, IoT sensors, business metrics. Creates local web dashboards with validation before delivery.

## Core Principle: Scriptable > Heartbeat

Everything that CAN be automated without the agent SHOULD be. Agent involvement only for:
- Initial setup and connection
- Error debugging
- Design/layout changes
- New data sources

**Data fetching = cron scripts, NOT agent heartbeats.** Agent is expensive. Scripts are free.

## Architecture

```
~/dashboards/
├── registry.json           # Port assignments, project metadata, health status
├── scripts/                # Cron-able fetch scripts (agent generates, system runs)
│   └── fetch-{project}.sh  # curl + jq → data.json
├── {project}/
│   ├── config.json         # Layout, widgets, refresh intervals
│   ├── data.json           # Current data (updated by script, read by dashboard)
│   ├── index.html          # Static dashboard, reads data.json
│   └── .cache/             # Historical data, gitignored
```

## Visual QA Loop (MANDATORY)

**NEVER deliver a dashboard without validation.** Follow this loop:

```
1. Generate HTML
2. Open in browser → take screenshot
3. Check against criteria:
   □ No text overlapping
   □ Readable font sizes (≥14px for body, ≥24px for KPIs)
   □ Consistent spacing (8px grid)
   □ Good contrast (WCAG AA minimum)
   □ Charts have labels/legends
   □ Loading/error states visible
   □ Dark mode working (if enabled)
4. If ANY issue → fix → repeat from 2
5. Only after 3 passes with no issues → deliver
```

## Aesthetic Principles (Never Fail)

| Element | Safe Default |
|---------|--------------|
| Colors | Tailwind slate palette + 1 accent color |
| Background | Dark: `#0f172a`, Light: `#f8fafc` |
| Text | Dark: `#e2e8f0`, Light: `#1e293b` |
| Spacing | Multiple of 4px (prefer 16px, 24px, 32px) |
| Corners | 8px border-radius consistently |
| Charts | ECharts or Chart.js, never mix |
| Font | System font stack, no custom fonts |
| KPI cards | Big number (48-72px), label below (14px), delta badge |

## Data Source Strategies

For specific APIs by use case (SaaS, DevOps, IoT, Finance, Creator), see `sources.md`.

| Scenario | Strategy | Token Cost |
|----------|----------|------------|
| API with SDK/REST | Script: `curl` + `jq` → `data.json` | Zero (cron) |
| Webhook available | Endpoint receives push → updates `data.json` | Zero |
| No API, has embed | iframe in dashboard (Stripe, GA widgets) | Zero |
| No API, no embed | Screenshot capture → image in dashboard | Agent (occasional) |
| Export only | User drops CSV → dashboard watches file | Zero |
| Email reports | Parse incoming email → extract data | Agent (parse) |

**Rule:** Always try scriptable first. Screenshots/scraping = last resort.

## Screenshot Strategy (When No API)

For services without APIs (some analytics, internal tools):

```bash
# Cron runs daily at 6am
# 1. Open headless browser
# 2. Login (credentials from Keychain)
# 3. Navigate to chart
# 4. Screenshot specific element (not full page)
# 5. Save to ~/dashboards/{project}/screenshots/{date}.png
# 6. Dashboard shows latest screenshot with timestamp
```

**Constraints:**
- Max 1-2 screenshots per service per day (respect ToS)
- Never for services with APIs
- Always show "Last updated: X" timestamp

## API Integration Rules

**Rate Limits:**
- Calculate: `daily_limit / widgets / hours_active`
- If polling would exceed → reduce frequency or error
- Track remaining quota per API

**Error Handling:**
- 3 failures → circuit breaker open
- Show stale data + age badge: "Data from 2h ago ⚠️"
- Never blank widget, always fallback

**Auth:**
- Credentials in Keychain, never in config
- Refresh tokens proactively (before expiry)
- Support multiple accounts: `stripe_personal`, `stripe_work`

## Security Checklist

Before delivering any dashboard:
- [ ] Credentials in Keychain, not files
- [ ] Listening on `127.0.0.1` by default
- [ ] No PII (emails, names) in dashboard
- [ ] Logs don't contain tokens or revenue values
- [ ] Cache encrypted if contains sensitive data
- [ ] If LAN access needed: basic auth with generated password

## Scalability Structure

For users with many dashboards:

```json
// registry.json
{
  "projects": {
    "stripe-revenue": {
      "port": 3001,
      "sources": ["stripe"],
      "lastUpdate": "2026-02-13T10:00:00Z",
      "status": "healthy"
    },
    "home-assistant": {
      "port": 3002,
      "sources": ["hass"],
      "lastUpdate": "2026-02-13T10:05:00Z", 
      "status": "healthy"
    }
  },
  "nextPort": 3003,
  "globalPalette": "slate-blue"  // Shared colors across dashboards
}
```

**Meta-dashboard:** Generate `~/dashboards/index.html` that shows all dashboards with their health status.

## Legal Boundaries

| Method | Status | Notes |
|--------|--------|-------|
| Official REST API | ✅ Safe | Use documented endpoints only |
| Official embeds/widgets | ✅ Safe | Stripe, GA, etc. provide these |
| Public data scraping | ⚠️ Careful | Respect robots.txt, rate limit |
| Screenshots of own accounts | ⚠️ Careful | Personal use OK, check ToS |
| Undocumented APIs | ❌ Avoid | Can break, may violate ToS |
| Scraping behind login | ❌ Avoid | Usually prohibited |

**Rule:** If you need to reverse-engineer it, the user should know the risk.
