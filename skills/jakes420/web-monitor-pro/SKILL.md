---
name: web-monitor
version: 3.1.0
description: "Monitor web pages for changes, price drops, stock availability, and custom conditions. Use when a user asks to watch/track/monitor a URL, get notified about price changes, check if something is back in stock, or track any website for updates. Also handles listing, removing, checking, and reporting on existing monitors. v3 adds change summaries, visual diffs, price comparison, templates, JS rendering, and webhooks."
metadata:
  {
    "openclaw":
      {
        "emoji": "👁️",
        "requires": { "bins": ["python3", "curl"] },
      },
  }
---

# Web Monitor Pro v3.0.0

Track changes on any web page. Get alerts for price drops, stock changes, and content updates.

## What's new in v3

- **Change summaries**: When something changes, you get a real explanation. "Price dropped from R3,899 to R3,314 (15% off)" instead of just "changed".
- **Visual diffs**: Side-by-side HTML comparison showing exactly what's different, with green/red highlights.
- **Price comparison**: Compare prices across multiple stores. See who's cheapest and by how much.
- **Templates**: Pre-built monitoring setups. One command to start tracking price drops, restocks, or sales.
- **JS rendering**: Optional Playwright integration for sites that need a real browser to load.
- **Webhooks**: POST to Slack, Discord, or any URL when conditions are met.

## Setup

No API keys needed. Uses `curl` for fetching and stores data in `~/.web-monitor/`.

Run `monitor.py setup` for a welcome message and quick start guide.

Optional: For JS-heavy sites, install Playwright: `pip3 install playwright && python3 -m playwright install chromium`

## Quick Start

The fastest way to start: `watch` auto-detects what kind of page you're looking at and sets up the right kind of monitoring.

```bash
python3 scripts/monitor.py watch "https://example.com/product"
```

It figures out if it's a product page (sets up price monitoring), a stock page (watches for availability), or just a regular page (tracks content changes). No flags needed.

## Templates

Skip the manual config. Templates set up everything for common use cases:

```bash
python3 scripts/monitor.py template list
python3 scripts/monitor.py template use price-drop "https://example.com/product"
python3 scripts/monitor.py template use restock "https://example.com/product"
python3 scripts/monitor.py template use sale "https://example.com/deals"
```

Available templates:
- `price-drop` - Monitor for price decreases. Snapshots the current price as baseline.
- `restock` - Watch for "in stock", "available", "add to cart" text.
- `content-update` - Track page content changes with smart diff.
- `sale` - Watch for "sale", "discount", "% off" keywords.
- `new-release` - Watch for new items or versions on a page.

Each one pre-configures the condition, check interval, and priority.

## All Commands

Everything goes through `scripts/monitor.py`:

```bash
python3 scripts/monitor.py <command> [args]
```

### Adding Monitors

**watch** (recommended for most cases):
```bash
python3 scripts/monitor.py watch "https://example.com/product"
python3 scripts/monitor.py watch "https://example.com" --group wishlist
python3 scripts/monitor.py watch "https://example.com" --browser --webhook "https://hooks.slack.com/..."
```

**add** (when you want full control):
```bash
python3 scripts/monitor.py add "https://example.com/product" \
  --label "Cool Gadget" \
  --condition "price below 500" \
  --interval 360 \
  --group "wishlist" \
  --priority high \
  --target 3000 \
  --browser \
  --webhook "https://hooks.slack.com/..."
```

Options for `add` and `watch`:
- `--label/-l` - Name for the monitor
- `--selector/-s` - CSS selector to focus on (`#price` or `.stock-status`)
- `--condition/-c` - When to alert (see Conditions below)
- `--interval/-i` - Check interval in minutes (default: 360)
- `--group/-g` - Category name (e.g. "wishlist", "work")
- `--priority/-p` - high, medium, or low (default: medium)
- `--target/-t` - Price target number (e.g. 3000)
- `--browser/-b` - Use Playwright headless browser for JS-rendered pages
- `--webhook/-w` - Webhook URL to POST on changes (repeatable for multiple webhooks)

### Checking Monitors

```bash
python3 scripts/monitor.py check              # Check all enabled monitors
python3 scripts/monitor.py check --id <id>     # Check one specific monitor
python3 scripts/monitor.py check --verbose     # Include content preview in output
```

Returns JSON with status (changed/unchanged), condition info, price data, and smart change summaries.

Change summaries tell you what actually happened:
- Price monitors: "Price dropped from R3,899 to R3,314 (15% off). Lowest price in 30 days."
- Stock monitors: "Back in stock! Was out of stock for 3 days."
- Content: 'New: "Breaking news: AI model achieves new benchmark..."'

When changes are detected, an HTML diff file is auto-generated. The path shows up in the `diff_path` field.

### Visual Diffs

```bash
python3 scripts/monitor.py diff <id>           # Generate and open side-by-side diff
python3 scripts/monitor.py screenshot <id>     # Save current page content for diffing
```

The diff command generates an HTML page with old content on the left, new content on the right. Added text is green, removed is red, changed is yellow. Opens automatically in your browser.

### Price Comparison

Compare prices across all monitors in a group:

```bash
python3 scripts/monitor.py compare mygroup     # Compare monitors in "mygroup"
python3 scripts/monitor.py compare --all       # Compare all price monitors
```

Shows cheapest to most expensive, price history for each, and the best deal with percentage below average.

Add a competitor to an existing monitor:

```bash
python3 scripts/monitor.py add-competitor <id> "https://competitor.com/same-product"
```

This creates a new monitor in the same group with the same condition, so you can compare them.

### Dashboard

See everything at a glance:
```bash
python3 scripts/monitor.py dashboard
python3 scripts/monitor.py dashboard --whatsapp    # Formatted for WhatsApp
```

Shows status icons, last check time, days monitored, current prices, target progress, and whether browser/webhooks are configured. Groups monitors by category.

### Price Trends

```bash
python3 scripts/monitor.py trend <id>
python3 scripts/monitor.py trend <id> --days 30
```

Shows price direction (rising/dropping/stable), min/max/avg with dates, target progress, and a sparkline chart.

### Managing Monitors

```bash
python3 scripts/monitor.py list                    # List all
python3 scripts/monitor.py list --group wishlist   # Filter by group
python3 scripts/monitor.py pause <id>              # Pause (skip during checks)
python3 scripts/monitor.py resume <id>             # Resume
python3 scripts/monitor.py remove <id>             # Delete
```

### Notes

Attach notes to any monitor:
```bash
python3 scripts/monitor.py note <id> "waiting for Black Friday"
python3 scripts/monitor.py notes <id>              # View all notes
```

### Manual Snapshots

Take a snapshot right now, with an optional note:
```bash
python3 scripts/monitor.py snapshot <id>
python3 scripts/monitor.py snapshot <id> --note "price before sale"
```

### History

```bash
python3 scripts/monitor.py history <id>
python3 scripts/monitor.py history <id> --limit 10
```

### Reports

Weekly summary formatted for WhatsApp:
```bash
python3 scripts/monitor.py report
```

### Groups

```bash
python3 scripts/monitor.py groups    # List all groups with counts
```

### Export and Import

```bash
python3 scripts/monitor.py export > monitors.json
python3 scripts/monitor.py import monitors.json      # Skips duplicates by URL
```

## Condition Syntax

- `price below 500` or `price < 500` - Alert when price drops below threshold
- `price above 1000` or `price > 1000` - Alert when price goes above threshold
- `contains 'in stock'` - Alert when text appears on page
- `not contains 'out of stock'` - Alert when text disappears from page

## Priority Levels

- **high** - Immediate alert (shown with fire emoji)
- **medium** - Normal alert (default)
- **low** - Batch into daily/weekly digest

## JS Rendering

Some sites (Takealot, Amazon, most modern SPAs) load content with JavaScript. The default curl fetch won't see that content.

Add `--browser` to use Playwright's headless Chromium:

```bash
python3 scripts/monitor.py add "https://takealot.com/product" --browser
python3 scripts/monitor.py watch "https://takealot.com/product" --browser
```

If Playwright isn't installed, the tool falls back to curl and notes the limitation. Install it with:

```
pip3 install playwright && python3 -m playwright install chromium
```

## Webhooks

Get notified via webhook when a condition is met or content changes:

```bash
python3 scripts/monitor.py add "https://example.com" --webhook "https://hooks.slack.com/services/..."
python3 scripts/monitor.py add "https://example.com" --webhook "https://url1.com" --webhook "https://url2.com"
```

The webhook receives a JSON POST with: monitor_id, label, url, event details (status, condition_met, change_summary, current_price), and timestamp.

Webhooks fire during `check` whenever a change is detected or a condition is met.

## Automation with Cron

Set up a cron job to check monitors and alert on changes:

```
Task: Check all web monitors. Run: python3 <skill_dir>/scripts/monitor.py check
Report any monitors where status is "changed" or "condition_met" is true.
If nothing changed, say so briefly or stay silent.
```

Recommended: every 6 hours (`0 */6 * * *`).

For weekly reports: `python3 <skill_dir>/scripts/monitor.py report` on Mondays.

## Feedback

Found a bug? Have an idea? We want to hear it.

```bash
monitor.py feedback "your message"
monitor.py feedback --bug "something broke"
monitor.py feedback --idea "wouldn't it be cool if..."
```

Need to file a detailed bug report? Run `monitor.py debug` to get system info you can paste into an issue.

## Tips

- For JS-heavy sites, use `--browser` or the OpenClaw browser tool to get rendered content
- Up to 50 snapshots per monitor are kept for history
- Content is capped at 10KB per snapshot
- Use `--selector` to focus on a specific element and reduce noise
- When a user says "watch this" or "let me know when", create a monitor + cron job
- Price targets show progress in dashboard and check output
- The `watch` command is the easiest entry point for new monitors
- Use `template use` for quick setups without figuring out conditions
- Group related monitors together, then use `compare` to see who's cheapest
