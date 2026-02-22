---
name: adwhiz
description: >
  Manage Google Ads campaigns from your AI coding tool. 44 MCP tools for
  auditing, creating, and optimizing Google Ads accounts using natural language.
metadata:
  openclaw:
    primaryEnv: "ADWHIZ_API_KEY"
    requires:
      bins:
        - node
    install:
      - kind: node
        package: "@adwhiz/mcp-server"
    homepage: "https://adwhiz.ai"
---

# AdWhiz — Google Ads MCP Server

AdWhiz is a remote MCP server that gives your AI tool direct access to the
Google Ads API. It exposes **44 tools** across 5 categories so you can audit,
create, and manage Google Ads campaigns using plain English.

## Tool Categories

### Account (2 tools)
- `list_accounts` — List all accessible Google Ads accounts
- `get_account_info` — Get account details (currency, timezone, optimization score)

### Read (14 tools)
- `list_campaigns` — List campaigns with status, type, budget, bidding strategy
- `get_campaign_performance` — Campaign metrics: cost, clicks, conversions, CTR, CPA, ROAS
- `list_ad_groups` — List ad groups with bids, filtered by campaign
- `list_ads` — List ads with headlines, descriptions, final URLs
- `list_keywords` — Keywords with match types, bids, quality scores
- `get_search_terms` — Search terms report (actual queries triggering ads)
- `list_negative_keywords` — Negative keywords at campaign, ad group, or account level
- `list_assets` — Sitelinks, callouts, structured snippets
- `list_conversion_actions` — Conversion actions with status, type, category
- `list_budgets` — Campaign budgets with associated campaigns
- `list_bidding_strategies` — Portfolio bidding strategies
- `list_audience_segments` — Audience targeting criteria
- `list_user_lists` — Remarketing/audience lists for targeting
- `get_operation_log` — Recent mutations performed via AdWhiz

### Write (25 tools)
- `create_campaign` — Create Search, Display, PMax, or Video campaign (starts PAUSED)
- `update_campaign` — Update campaign name
- `set_campaign_status` — Pause, enable, or remove a campaign
- `create_ad_group` — Create an ad group in a campaign
- `update_ad_group` — Update ad group name or CPC bid
- `set_ad_group_status` — Pause, enable, or remove an ad group
- `create_responsive_search_ad` — Create RSA with headlines + descriptions (starts PAUSED)
- `set_ad_status` — Pause, enable, or remove an ad
- `add_keywords` — Add keywords with match types and bids
- `update_keyword_bid` — Change a keyword's CPC bid
- `set_keyword_status` — Pause, enable, or remove a keyword
- `add_negative_keyword` — Add negative keyword at campaign or ad group level
- `remove_negative_keyword` — Remove a negative keyword
- `create_shared_negative_list` — Create a shared negative keyword list
- `add_to_shared_list` — Add keywords to a shared negative list
- `attach_shared_list` — Attach shared list to a campaign
- `create_sitelink` — Create a sitelink asset
- `create_callout` — Create a callout asset
- `link_asset_to_campaign` — Link asset to a campaign
- `create_conversion_action` — Create a conversion tracking action
- `update_conversion_action` — Update conversion action name or status
- `create_budget` — Create a campaign budget
- `update_budget` — Update budget amount or name
- `create_bidding_strategy` — Create a portfolio bidding strategy
- `add_audience_to_campaign` — Add audience targeting to a campaign

### Audit (2 tools)
- `run_mini_audit` — Quick 3-metric audit: wasted spend, best/worst CPA, projected savings
- `run_full_audit` — Comprehensive audit: campaigns, keywords, search terms, issues, recommendations

### Query (1 tool)
- `run_gaql_query` — Execute any read-only GAQL query (max 1,000 rows)

## MCP Server Configuration

### Option A: stdio transport (via npx)

Add this to your `openclaw.json`:

```json
{
  "mcpServers": {
    "adwhiz": {
      "command": "npx",
      "args": ["-y", "@adwhiz/mcp-server"],
      "env": {
        "ADWHIZ_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Option B: HTTP transport (remote server)

```json
{
  "mcpServers": {
    "adwhiz": {
      "transport": "http",
      "url": "https://mcp.adwhiz.ai/mcp",
      "headers": {
        "Authorization": "Bearer your-api-key-here"
      }
    }
  }
}
```

## Quick Install

```bash
clawhub install adwhiz
```

## Example Prompts

- "Audit my Google Ads account and show the top 5 waste areas"
- "Pause all campaigns with CPA above $150"
- "Add these negative keywords to my Search campaigns: [list]"
- "Create a new Search campaign targeting lawyers in New York with $100/day budget"
- "Show me search terms wasting money and suggest negatives"
- "What is my account's average Quality Score this month?"

## Safety Defaults

- New campaigns and ads are always created in **PAUSED** status
- Every mutation is logged in the operation log
- Read-only tools never modify your account
- Write tools require confirmation before executing

## Documentation

Full documentation: https://adwhiz.ai/docs
