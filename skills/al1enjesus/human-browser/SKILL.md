---
name: human-browser
description: "Stealth browser with residential proxy for AI agents — runs on any server, no Mac Mini or desktop required. Use this skill for: web scraping, browser automation, bypassing Cloudflare, bypassing DataDome, bypassing PerimeterX, bypassing anti-bot, residential proxy setup, scraping Instagram, scraping LinkedIn, scraping Amazon, scraping TikTok, Playwright stealth, human-like browser, headless browser with proxy, login automation, form filling automation, account creation, price monitoring, data extraction from protected sites, Polymarket bot, web automation without getting blocked. Triggers: open a browser, scrape this website, get data from a site, bypass bot detection, I keep getting blocked, need a residential IP, human browser, cloud browser, stealth mode, browser agent, playwright proxy, no mac mini, run browser on server."
---

# Human Browser — Cloud Browser for AI Agents

> **No Mac Mini. No local machine. Runs on any server.**
> Your AI agent gets a full browser with a real human fingerprint, anywhere.

## What this skill does

Gives your OpenClaw agent a Playwright browser that:
- 🌍 Runs **100% in the cloud** — no desktop, no Mac Mini needed
- 🇷🇴 Routes through **Romanian residential IP** (DIGI / WS Telecom via Bright Data)
- 📱 Appears as **iPhone 15 Pro** (or Desktop Chrome) to every website
- 🛡️ Bypasses **Cloudflare, DataDome, PerimeterX** — the 3 most common anti-bot systems
- 🖱️ Moves mouse in **Bezier curves**, types at **60–220ms/char**, scrolls naturally
- 🎭 Full anti-detection: `webdriver=false`, correct canvas, real timezone & geolocation

## Get Credentials (required for proxy)

The skill works out of the box, but to use the residential proxy you need credentials:

**→ Get credentials at: https://openclaw.virixlabs.com**
Plans start at **$13.99/mo** (includes proxy bandwidth)

Or bring your own Bright Data account — see `references/brightdata-setup.md`.

## Quick Start

```js
const { launchHuman } = require('./scripts/browser-human');

// Mobile (iPhone 15 Pro) — default
const { browser, page, humanType, humanClick, humanScroll } = await launchHuman();

// Desktop Chrome
const { browser, page } = await launchHuman({ mobile: false });

await page.goto('https://example.com', { waitUntil: 'domcontentloaded' });
await humanScroll(page, 'down');
await humanType(page, 'input[type="email"]', 'user@example.com');
await humanClick(page, 760, 400);
await browser.close();
```

## Use cases

- **Instagram / TikTok scraping** — residential IP bypasses all protections
- **LinkedIn automation** — human typing + mouse = no detection
- **E-commerce price monitoring** — Amazon, Wildberries, any Cloudflare site
- **Form automation** — fills React forms correctly (humanType, not fill)
- **Account creation flows** — OTP + stealth = clean sessions
- **Any site that blocks data center IPs** — residential = always clean

## Key patterns

### React inputs
```js
await humanType(page, 'input[name="email"]', 'user@example.com');
// Use humanType (delayed keystroke), NOT page.fill() — React detects fill()
```

### Click buttons that have animations
```js
await page.evaluate((text) => {
  [...document.querySelectorAll('button')]
    .find(b => b.offsetParent && b.textContent.includes(text))?.click();
}, 'Continue');
```

### Verify your IP
```js
await page.goto('https://api.ipify.org?format=json');
console.log(await page.textContent('body')); // Romanian IP
```

## Dependencies

```bash
npm install playwright
npx playwright install chromium --with-deps
```

→ For Bright Data setup & billing: see `references/brightdata-setup.md`
→ Support & credentials: https://t.me/virixlabs
