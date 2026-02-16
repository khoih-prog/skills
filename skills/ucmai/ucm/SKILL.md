---
name: ucm
description: "API marketplace for AI agents — 100 services (web search, image gen, code sandbox, TTS, NASA, recipes, Pokemon, and 90+ more) via one API key"
homepage: https://github.com/ucmai/skills
metadata: {"openclaw": {"emoji": "🛒", "requires": {"env": ["UCM_API_KEY"], "anyBins": ["curl", "node"]}, "primaryEnv": "UCM_API_KEY", "install": [{"id": "node", "kind": "node", "package": "@ucm/mcp-server", "bins": ["ucm-mcp"], "label": "Install UCM MCP Server (node)"}]}}
---

# UCM — Universal Commerce Marketplace

Give your agent access to 100 API services with a single API key. 87 services are completely free.

## Setup

### Option 1: MCP Server (recommended)

If your environment supports MCP, configure the UCM MCP Server:

```json
{
  "mcpServers": {
    "ucm": {
      "command": "npx",
      "args": ["-y", "@ucm/mcp-server@0.3.3"],
      "env": {
        "UCM_API_KEY": "ucm_key_..."
      }
    }
  }
}
```

No API key yet? Use the `ucm_register` tool after connecting — it creates one automatically with $1.00 free credits.

### Option 2: HTTP API (works everywhere)

```bash
# Register (free)
curl -X POST https://registry.ucm.ai/v1/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-openclaw-agent"}'
# Returns: { "api_key": "ucm_key_...", "credits": { "balance": "1.00" } }
```

Save the `UCM_API_KEY` as an environment variable:

```bash
export UCM_API_KEY="ucm_key_..."
```

### Option 3: mcporter

If you have mcporter installed:

```bash
mcporter call ucm.ucm_register name=my-agent
mcporter call ucm.ucm_discover query="search the web"
mcporter call ucm.ucm_call service_id=ucm/web-search endpoint=search query="AI news"
```

## How to Use

### Discover Services

Find the right API for what you need:

```bash
curl -X POST https://registry.ucm.ai/v1/discover \
  -H "Content-Type: application/json" \
  -d '{"query": "generate an image from text"}'
```

### Call a Service

```bash
curl -X POST https://registry.ucm.ai/v1/call \
  -H "Authorization: Bearer $UCM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "ucm/web-search",
    "endpoint": "search",
    "body": {"query": "OpenClaw tutorials"}
  }'
```

### Check Balance

```bash
curl -H "Authorization: Bearer $UCM_API_KEY" \
  https://registry.ucm.ai/v1/credits
```

## Available Services (100 total)

### Paid ($0.01–$0.05/call)

| Service | What It Does | Price |
|---------|-------------|-------|
| ucm/web-search | Search the web (Tavily) | $0.01 |
| ucm/web-scrape | Scrape web pages (Firecrawl) | $0.02 |
| ucm/image-generation | Generate images from text (Together AI) | $0.05 |
| ucm/code-sandbox | Execute code in sandbox (E2B) | $0.03 |
| ucm/text-to-speech | Convert text to audio (Kokoro) | $0.01 |
| ucm/speech-to-text | Transcribe audio (Whisper) | $0.01 |
| ucm/email | Send emails (Resend) | $0.01 |
| ucm/doc-convert | Convert documents (Firecrawl) | $0.02 |
| ucm/us-stock | US stock market data (Finnhub) | $0.01 |
| ucm/cn-finance | China financial data (Tushare) | $0.01 |
| ucm/translate | Text translation (MyMemory) | $0.01 |
| ucm/qr-code | Generate QR codes | $0.01 |
| ucm/news | Latest news (NewsData) | $0.01 |

### Free (87 services, $0.00)

Weather, Wikipedia, currency exchange, countries, holidays, dictionary, books, geocoding, math, IP geolocation, address lookup, academic papers, nutrition, crypto prices, timezone, domain info, quotes, Hacker News, random data, poetry, movies, word associations, universities, zip codes, trivia, jokes, advice, bored activity ideas, Bible verses, Chuck Norris facts, recipes, cocktails, breweries, food products, sunrise/sunset, dog images, cat facts, avatars, colors, Lorem Ipsum, NASA, SpaceX, ISS, space news, arXiv papers, earthquakes, World Bank, FDA data, carbon intensity, elevation, age/gender/nationality prediction, UK postcodes, vehicle data, Met Museum, Art Institute of Chicago, TV shows, anime, iTunes, music, radio stations, free games, game deals, Pokemon, D&D, memes, IP lookup, barcodes, Wayback Machine, npm, PyPI, GitHub repos, country flags, deck of cards, Star Wars, xkcd, Rick & Morty, Nobel Prize, historical events, Kanye quotes, Rust crates, Docker Hub, Lichess, periodic table, airports, random fox images.

## Security & Privacy

### Data Flow

All API calls from your agent go through the UCM registry (`registry.ucm.ai`) which proxies them to third-party providers. Your agent never communicates directly with third-party APIs and never holds their API keys.

```
Your Agent → registry.ucm.ai → Third-party API (Tavily, Firecrawl, etc.)
```

### What Data Leaves Your Machine

| Data | Destination | Purpose |
|------|-------------|---------|
| API key (`ucm_key_...`) | `registry.ucm.ai` | Authentication |
| Service call parameters (e.g. search query, URL) | `registry.ucm.ai` → third-party provider | Fulfill the API request |
| Agent name (at registration) | `registry.ucm.ai` | Account identification |

### What Data Stays Local

- Your OpenClaw configuration and conversation history
- Any results returned by API calls (stored only in your agent's context)
- This skill file itself (instructions only; the optional MCP server runs as a separate process)

### External Endpoints Called

| Endpoint | When |
|----------|------|
| `https://registry.ucm.ai/v1/agents/register` | One-time registration |
| `https://registry.ucm.ai/v1/call` | Every API service call |
| `https://registry.ucm.ai/v1/discover` | Service search |
| `https://registry.ucm.ai/v1/services` | Browse catalog |
| `https://registry.ucm.ai/v1/credits` | Check balance |

All traffic is HTTPS. No other domains are contacted by this skill.

### Trust & Safety

- **No embedded scripts** — this skill file contains only instructions and HTTP call examples; the optional MCP server (`@ucm/mcp-server`) is a published npm package you can audit before installing
- **No third-party key exposure** — UCM manages all upstream API keys server-side
- **Audited calls** — every API call is logged with transaction ID and timestamp
- **Auto-refund** — credits are automatically refunded on upstream failures (5xx, 429, 422)
- **Spending limits** — credit system prevents runaway costs; $1.00 starting balance caps exposure
- **684 tests** covering security, authentication, and all service adapters

## Links

- Website: https://ucm.ai
- Docs: https://ucm.ai/docs
- Dashboard: https://dashboard.ucm.ai
- npm: https://www.npmjs.com/package/@ucm/mcp-server
- GitHub: https://github.com/ucmai/skills
