---
name: xpoz-social-search
description: "Search Twitter, Instagram, and Reddit posts in real time. Find social media mentions, track hashtags, discover influencers, and analyze engagement — 1.5B+ posts indexed. Social listening, brand monitoring, and competitor research made easy for AI agents."
homepage: https://xpoz.ai
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["mcporter"], "skills": ["xpoz-setup"], "network": ["mcp.xpoz.ai"], "credentials": "Xpoz account (free tier) — auth via xpoz-setup skill (OAuth 2.1)" },
      },
  }
tags:
  - social-media
  - search
  - twitter
  - instagram
  - reddit
  - mcp
  - xpoz
  - research
  - intelligence
  - discovery
  - social-search
  - twitter-search
  - social-listening
  - brand-monitoring
  - hashtag
  - mentions
  - influencer
  - engagement
  - viral
  - trending
---

# Xpoz Social Search

**Multi-platform social media search powered by 1.5 billion+ indexed posts.**

Search posts, find people, and discover conversations across Twitter, Instagram, and Reddit using natural language queries. Built on Xpoz MCP — the social intelligence server that makes cross-platform research as easy as a function call.

---

## ⚡ Setup (READ THIS FIRST)

**Before using this skill, ensure the Xpoz MCP server is configured and authenticated.**

👉 **Read and follow [`xpoz-setup/SKILL.md`](https://clawhub.ai/skills/xpoz-setup)** — it handles everything automatically. The user won't need to run any commands; at most they click "Authorize" in a browser.

Once `mcporter call xpoz.checkAccessKeyStatus` returns `hasAccessKey: true`, come back here and continue with **Usage Patterns** below.

---

## What This Skill Does

This skill teaches OpenClaw agents to:

✅ **Search posts** by keywords across Twitter, Instagram, and Reddit  
✅ **Find people** who talk about specific topics  
✅ **Look up profiles** by username or ID  
✅ **Search by name** to discover accounts  
✅ **Filter by date range** for time-sensitive research  
✅ **Find relevant subreddits** about any topic  
✅ **Export results to CSV** for analysis  

### Why Multi-Platform Matters

Unlike single-platform tools, Xpoz lets you search across Twitter, Instagram, and Reddit simultaneously. Find where conversations are actually happening — not just where you think they are.

**Indexed Data:**
- 🐦 Twitter: 1B+ posts
- 📸 Instagram: 400M+ posts (captions + video subtitles)
- 🗨️ Reddit: 100M+ posts & comments

---

## Setup

See the **[xpoz-setup](https://clawhub.ai/skills/xpoz-setup)** skill for full setup and authentication instructions.

**TL;DR:** The agent handles everything. You just click "Authorize" when the browser opens (or tap a link your agent sends you).

---

## Usage Patterns

### Pattern 1: Search Posts by Topic (Cross-Platform)

**Use Case:** Find recent discussions about a product, trend, or event.

**Example: Find posts about "Model Context Protocol" on Twitter**

```bash
mcporter call xpoz.getTwitterPostsByKeywords \
  query="model context protocol OR MCP" \
  startDate=2026-01-01 \
  limit=50
```

The response includes an `operationId`. **Always poll for results:**

```bash
mcporter call xpoz.checkOperationStatus operationId=op_abc123
```

**Cross-Platform Search:**

```bash
# Twitter
mcporter call xpoz.getTwitterPostsByKeywords query="AI agents"

# Instagram
mcporter call xpoz.getInstagramPostsByKeywords query="AI agents"

# Reddit
mcporter call xpoz.getRedditPostsByKeywords query="AI agents"
```

---

### Pattern 2: Find People Who Talk About Something

**Use Case:** Identify potential leads, influencers, or community members.

**Example: Find Twitter users posting about "open source LLMs"**

```bash
mcporter call xpoz.getTwitterUsersByKeywords \
  query="\"open source\" AND LLM" \
  limit=100
```

Then poll:

```bash
mcporter call xpoz.checkOperationStatus operationId=op_xyz789
```

**Result:** List of users with post counts, follower stats, and relevance scores.

**Cross-Platform:**

```bash
# Find Instagram users posting about fitness
mcporter call xpoz.getInstagramUsersByKeywords query="fitness routine"

# Find Reddit users discussing Python
mcporter call xpoz.getRedditUsersByKeywords query="python programming"
```

---

### Pattern 3: Look Up a Specific Profile

**Use Case:** Get detailed profile data for a known account.

**Example: Look up a Twitter user by username**

```bash
mcporter call xpoz.getTwitterUser \
  identifier=elonmusk \
  identifierType=username
```

**Example: Look up by Twitter user ID**

```bash
mcporter call xpoz.getTwitterUser \
  identifier=44196397 \
  identifierType=id
```

**Other Platforms:**

```bash
# Instagram profile
mcporter call xpoz.getInstagramUser identifier=instagram identifierType=username

# Reddit profile
mcporter call xpoz.getRedditUser identifier=spez identifierType=username
```

---

### Pattern 4: Search for Accounts by Name

**Use Case:** Find accounts when you don't know the exact username.

**Example: Find Twitter accounts named "OpenAI"**

```bash
mcporter call xpoz.searchTwitterUsers query="OpenAI" limit=20
```

**Cross-Platform:**

```bash
# Search Instagram users
mcporter call xpoz.searchInstagramUsers query="National Geographic"

# Search Reddit users
mcporter call xpoz.searchRedditUsers query="AutoModerator"
```

---

### Pattern 5: Search Within a Date Range

**Use Case:** Analyze sentiment during a specific event or time period.

**Example: Find tweets about "Super Bowl" during game day**

```bash
mcporter call xpoz.getTwitterPostsByKeywords \
  query="Super Bowl" \
  startDate=2026-02-09 \
  endDate=2026-02-10 \
  limit=200
```

**Note:** Current year is **2026**. Use `YYYY-MM-DD` format.

---

### Pattern 6: Find Relevant Subreddits

**Use Case:** Discover communities discussing a topic.

**Example: Find subreddits about "machine learning"**

```bash
mcporter call xpoz.getRedditSubredditsByKeywords \
  query="machine learning" \
  limit=30
```

Then poll:

```bash
mcporter call xpoz.checkOperationStatus operationId=op_reddit123
```

**Result:** List of subreddits with subscriber counts, descriptions, and activity metrics.

---

### Pattern 7: Advanced Boolean Queries

**Use Case:** Precise filtering with boolean operators.

**Operators:**
- `AND` — Both terms must appear
- `OR` — Either term must appear
- `NOT` — Exclude a term
- `"exact phrase"` — Match exact phrase
- `()` — Group expressions

**Example: Find tweets about Tesla but not stock discussion**

```bash
mcporter call xpoz.getTwitterPostsByKeywords \
  query="Tesla AND (cars OR vehicles) NOT stock NOT TSLA"
```

**Example: Find Instagram posts about travel OR adventure**

```bash
mcporter call xpoz.getInstagramPostsByKeywords \
  query="travel OR adventure OR wanderlust"
```

---

### Pattern 8: Export to CSV

**Use Case:** Export large result sets for external analysis.

Every search operation returns a `dataDumpExportOperationId`. Use it to export results:

```bash
# Step 1: Get search results
mcporter call xpoz.getTwitterPostsByKeywords query="climate change" limit=1000

# Step 2: Poll for results
mcporter call xpoz.checkOperationStatus operationId=op_search123

# Step 3: Export using dataDumpExportOperationId from response
mcporter call xpoz.checkOperationStatus operationId=export_op_abc
```

The export URL will be in the `result.url` field when complete.

---

## Tool Reference

### Search Posts

| Tool | Platform | What It Searches |
|------|----------|------------------|
| `getTwitterPostsByKeywords` | Twitter | Tweets and retweets |
| `getInstagramPostsByKeywords` | Instagram | Posts, reels (captions + subtitles) |
| `getRedditPostsByKeywords` | Reddit | Posts only |
| `getRedditCommentsByKeywords` | Reddit | Comments only |

**Key Parameters:**
- `query` (required) — Search terms (supports boolean operators)
- `startDate` / `endDate` (optional) — Date range (YYYY-MM-DD)
- `limit` (optional) — Max results (default: 100)
- `language` (optional) — Language code (e.g., `en`, `es`)
- `fields` (optional) — Specify fields to return (improves performance)

### Find People

| Tool | Platform | What It Returns |
|------|----------|-----------------|
| `getTwitterUsersByKeywords` | Twitter | Users who posted matching content |
| `getInstagramUsersByKeywords` | Instagram | Users who posted matching content |
| `getRedditUsersByKeywords` | Reddit | Users who posted matching content |

**Key Parameters:**
- `query` (required) — Search terms
- `limit` (optional) — Max users (default: 100)

### Profile Lookup

| Tool | Platform | Identifier Types |
|------|----------|------------------|
| `getTwitterUser` | Twitter | `username` or `id` |
| `getInstagramUser` | Instagram | `username` or `id` |
| `getRedditUser` | Reddit | `username` |

**Parameters:**
- `identifier` (required) — Username or ID
- `identifierType` (required) — Type of identifier

### Search by Name

| Tool | Platform | Purpose |
|------|----------|---------|
| `searchTwitterUsers` | Twitter | Find accounts by display name |
| `searchInstagramUsers` | Instagram | Find accounts by display name |
| `searchRedditUsers` | Reddit | Find accounts by username |

**Parameters:**
- `query` (required) — Search query
- `limit` (optional) — Max results

### Utility

| Tool | Purpose |
|------|---------|
| `checkOperationStatus` | Poll for async operation results (REQUIRED) |
| `checkAccessKeyStatus` | Verify your API key is configured |
| `getRedditSubredditsByKeywords` | Find subreddits about a topic |

---

## Important Notes

### ⚠️ Always Poll for Results

**All search tools return an `operationId` — you MUST call `checkOperationStatus` to get the actual data.**

```bash
# ❌ WRONG: This doesn't return results immediately
mcporter call xpoz.getTwitterPostsByKeywords query="AI"

# ✅ CORRECT: Poll for results
mcporter call xpoz.getTwitterPostsByKeywords query="AI"
# Returns: { operationId: "op_123" }

mcporter call xpoz.checkOperationStatus operationId=op_123
# Returns: { status: "completed", result: { posts: [...] } }
```

### 🚀 Use `fields` Parameter for Performance

If you only need specific fields (e.g., username and followers), specify them:

```bash
mcporter call xpoz.getTwitterUsersByKeywords \
  query="AI startups" \
  fields="username,displayName,followerCount"
```

This reduces response size and speeds up queries.

### 📅 Date Format

Always use `YYYY-MM-DD` format:

```bash
# ✅ Correct
startDate=2026-01-15

# ❌ Wrong
startDate="Jan 15, 2026"
```

**Current year is 2026** — important for calculating relative dates.

### 📊 CSV Exports

Large datasets (>1000 results) can be exported to CSV:

1. Every search returns a `dataDumpExportOperationId`
2. Poll that operation ID with `checkOperationStatus`
3. Download the CSV from the `result.url` when ready

### 🔍 Boolean Query Syntax

- `AND`, `OR`, `NOT` must be uppercase
- Use quotes for exact phrases: `"artificial intelligence"`
- Group with parentheses: `(AI OR ML) AND startups`
- Example: `"climate change" AND (policy OR regulation) NOT conspiracy`

### 🌍 Language Filtering

Specify language codes for better results:

```bash
mcporter call xpoz.getTwitterPostsByKeywords \
  query="football" \
  language=en
```

Common codes: `en`, `es`, `fr`, `de`, `pt`, `ja`, `ko`

---

## Example Workflows

### Workflow 1: Competitive Intelligence

**Goal:** Track competitor mentions over the last 30 days.

```bash
# Search Twitter
mcporter call xpoz.getTwitterPostsByKeywords \
  query="CompetitorName" \
  startDate=2026-01-12 \
  endDate=2026-02-11 \
  limit=500

# Poll results
mcporter call xpoz.checkOperationStatus operationId=op_comp123

# Find who's talking about them
mcporter call xpoz.getTwitterUsersByKeywords \
  query="CompetitorName" \
  limit=100

# Check operation
mcporter call xpoz.checkOperationStatus operationId=op_comp_users456
```

### Workflow 2: Influencer Discovery

**Goal:** Find micro-influencers in the fitness niche.

```bash
# Find Instagram users posting about fitness
mcporter call xpoz.getInstagramUsersByKeywords \
  query="fitness transformation OR workout routine" \
  limit=200

# Poll results
mcporter call xpoz.checkOperationStatus operationId=op_fitness123

# Look up promising profiles for detailed stats
mcporter call xpoz.getInstagramUser \
  identifier=fitnessguru123 \
  identifierType=username
```

### Workflow 3: Community Research

**Goal:** Understand where your audience hangs out on Reddit.

```bash
# Find relevant subreddits
mcporter call xpoz.getRedditSubredditsByKeywords \
  query="startup OR entrepreneur OR indie hacker" \
  limit=50

# Poll results
mcporter call xpoz.checkOperationStatus operationId=op_subs789

# Search posts in those communities
mcporter call xpoz.getRedditPostsByKeywords \
  query="launch AND feedback" \
  startDate=2026-02-01 \
  limit=100

# Check operation
mcporter call xpoz.checkOperationStatus operationId=op_posts456
```

### Workflow 4: Trend Analysis

**Goal:** See how sentiment changed during a product launch.

```bash
# Week before launch
mcporter call xpoz.getTwitterPostsByKeywords \
  query="ProductName" \
  startDate=2026-01-27 \
  endDate=2026-02-03

# Launch week
mcporter call xpoz.getTwitterPostsByKeywords \
  query="ProductName" \
  startDate=2026-02-03 \
  endDate=2026-02-10

# Compare volume, engagement, sentiment
```

---

## Troubleshooting

### "Operation not found"

You're polling an invalid `operationId`. Make sure you're using the exact ID returned from the search call.

### "Access key invalid"

Your API key isn't configured or is expired:

```bash
mcporter call xpoz.checkAccessKeyStatus
```

Fix by setting `XPOZ_ACCESS_KEY` environment variable (see Setup section).

### Empty results

- **Check your query syntax** — boolean operators must be uppercase
- **Verify date range** — dates must be in `YYYY-MM-DD` format
- **Try broader terms** — exact phrases may be too specific

### Slow queries

- **Use the `fields` parameter** to request only what you need
- **Reduce `limit`** for faster initial results
- **Add date filters** to narrow the search scope

---

## Related Skills

- **[xpoz-marketing](../xpoz-marketing)** — Content creation workflows for Xpoz
- **[find-influencers](../find-influencers)** — Influencer outreach automation
- **[xpoz-social](../xpoz-social)** — Social media management for Xpoz channels

---

## Resources

- **Website:** [xpoz.ai](https://xpoz.ai)
- **MCP Package:** [@xpozinc/xpoz-mcp](https://www.npmjs.com/package/@xpozinc/xpoz-mcp)
- **Dashboard:** [xpoz.ai/dashboard](https://xpoz.ai/dashboard)
- **Support:** support@xpoz.ai

---

## License & Usage

This skill is open source. The Xpoz MCP server requires a free or paid account at [xpoz.ai](https://xpoz.ai).

**Free Tier Limits:**
- 100 searches/month
- 1,000 results per search
- All platforms included

**Upgrade for:**
- Unlimited searches
- Bulk exports (up to 500K results per query)
- Historical data (back to 2019)
- Custom retention
- Priority support

---

## Responsible Use

This skill searches publicly available social media data. When using it:

- **Comply with platform terms of service** for Twitter, Instagram, and Reddit
- **Respect privacy laws** applicable to your jurisdiction (GDPR, CCPA, etc.)
- **Do not use for harassment, stalking, or unauthorized surveillance**
- **Consider data minimization** — only collect what you need for your use case
- **Disclose data collection** where required by law or ethical guidelines

Xpoz indexes only publicly available posts and profiles. No private messages, protected accounts, or non-public data is accessible.

---

**Built for ClawHub • Published 2026-02-11**
