/**
 * browser-human.js
 * 
 * Максимально легитимный браузер — iPhone 15, Румыния, человекоподобное поведение.
 * Подключается через Bright Data residential proxy (DIGI Romania / WS Telecom).
 * 
 * Usage:
 *   const { launchHuman } = require('./browser-human');
 *   const { browser, page, ctx } = await launchHuman();
 */

const { chromium } = require('./node_modules/playwright');
require('dotenv').config();

// ─── CONFIG ───────────────────────────────────────────────────────────────────
// Set credentials via environment variables or pass directly to launchHuman()
// Get credentials at: https://openclaw.virixlabs.com
const PROXY = {
  server:   process.env.PROXY_SERVER   || 'http://brd.superproxy.io:22225',
  username: process.env.PROXY_USERNAME || '',  // set in .env
  password: process.env.PROXY_PASSWORD || '',  // set in .env
};

// iPhone 15 Pro — самый популярный iOS девайс 2024
const IPHONE15 = {
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Mobile/15E148 Safari/604.1',
  viewport: { width: 393, height: 852 },
  deviceScaleFactor: 3,
  isMobile: true,
  hasTouch: true,
  locale: 'ro-RO',
  timezoneId: 'Europe/Bucharest',
  geolocation: { latitude: 44.4268, longitude: 26.1025, accuracy: 50 }, // Bucharest
  colorScheme: 'light',
  // HTTP headers that iOS Safari sends
  extraHTTPHeaders: {
    'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
  }
};

// Desktop Chrome (Windows) — для сайтов которые не работают на мобиле
const DESKTOP_RO = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
  viewport: { width: 1440, height: 900 },
  locale: 'ro-RO',
  timezoneId: 'Europe/Bucharest',
  geolocation: { latitude: 44.4268, longitude: 26.1025, accuracy: 50 },
  colorScheme: 'light',
  extraHTTPHeaders: {
    'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
  }
};

// ─── HUMAN BEHAVIOR ───────────────────────────────────────────────────────────

/** Random delay between min and max ms */
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const rand = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

/**
 * Move mouse along a natural curved path (Bezier-like)
 * Not a straight line — humans never move in straight lines
 */
async function humanMouseMove(page, toX, toY, fromX = null, fromY = null) {
  const pos = await page.evaluate(() => ({ x: window.mouseX || 400, y: window.mouseY || 400 }));
  const startX = fromX ?? pos.x;
  const startY = fromY ?? pos.y;
  
  // Generate control points for bezier curve
  const cp1x = startX + rand(-80, 80);
  const cp1y = startY + rand(-60, 60);
  const cp2x = toX + rand(-50, 50);
  const cp2y = toY + rand(-40, 40);
  
  const steps = rand(12, 25);
  
  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    // Cubic bezier
    const x = Math.round(
      Math.pow(1-t, 3) * startX +
      3 * Math.pow(1-t, 2) * t * cp1x +
      3 * (1-t) * Math.pow(t, 2) * cp2x +
      Math.pow(t, 3) * toX
    );
    const y = Math.round(
      Math.pow(1-t, 3) * startY +
      3 * Math.pow(1-t, 2) * t * cp1y +
      3 * (1-t) * Math.pow(t, 2) * cp2y +
      Math.pow(t, 3) * toY
    );
    await page.mouse.move(x, y);
    // Variable speed — faster in middle, slower at start/end
    const delay = t < 0.2 || t > 0.8 ? rand(8, 20) : rand(2, 8);
    await sleep(delay);
  }
}

/**
 * Human-like click with natural mouse movement
 */
async function humanClick(page, x, y, opts = {}) {
  await humanMouseMove(page, x, y);
  await sleep(rand(50, 180)); // Brief pause before click
  await page.mouse.down();
  await sleep(rand(40, 100)); // Hold duration
  await page.mouse.up();
  await sleep(rand(100, 300)); // Post-click pause
}

/**
 * Human-like type — variable speed, occasional micro-pause
 */
async function humanType(page, selector, text, opts = {}) {
  const el = await page.$(selector);
  if (!el) throw new Error(`Element not found: ${selector}`);
  
  // Click to focus
  const box = await el.boundingBox();
  if (box) await humanClick(page, box.x + box.width/2, box.y + box.height/2);
  await sleep(rand(200, 500));
  
  // Type character by character
  for (const char of text) {
    await page.keyboard.type(char);
    // Variable typing speed: 80-250ms per char (average human is ~100-150ms)
    const delay = rand(60, 220);
    await sleep(delay);
    
    // Occasional longer pause (thinking)
    if (Math.random() < 0.08) await sleep(rand(400, 900));
  }
  
  await sleep(rand(200, 400));
}

/**
 * Human-like scroll — smooth, variable speed, realistic
 */
async function humanScroll(page, direction = 'down', amount = null) {
  const scrollAmount = amount || rand(200, 600);
  const delta = direction === 'down' ? scrollAmount : -scrollAmount;
  
  // Move to random position first
  const vp = page.viewportSize();
  await humanMouseMove(page, rand(100, vp.width - 100), rand(200, vp.height - 200));
  
  // Scroll in small increments
  const steps = rand(4, 10);
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, delta / steps + rand(-5, 5));
    await sleep(rand(30, 80));
  }
  await sleep(rand(200, 800));
}

/**
 * Human-like page read pause (look around the page)
 */
async function humanRead(page, minMs = 1500, maxMs = 4000) {
  await sleep(rand(minMs, maxMs));
  // Occasional small scroll while reading
  if (Math.random() < 0.3) {
    await humanScroll(page, 'down', rand(50, 150));
  }
}

// ─── LAUNCH ───────────────────────────────────────────────────────────────────

/**
 * Launch a human-like browser session
 * @param {Object} opts
 * @param {boolean} opts.mobile - Use iPhone 15 (default: true)
 * @param {boolean} opts.useProxy - Use Romanian proxy (default: true)
 * @param {boolean} opts.headless - Headless mode (default: true)
 */
async function launchHuman(opts = {}) {
  const {
    mobile = true,
    useProxy = true,
    headless = true,
  } = opts;

  const device = mobile ? IPHONE15 : DESKTOP_RO;

  const browser = await chromium.launch({
    headless,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--ignore-certificate-errors',
      '--disable-blink-features=AutomationControlled', // Hide webdriver flag!
      '--disable-features=IsolateOrigins,site-per-process',
      '--disable-web-security',
    ],
  });

  const ctxOpts = {
    ...device,
    ignoreHTTPSErrors: true,
    permissions: ['geolocation', 'notifications'],
  };

  if (useProxy) {
    ctxOpts.proxy = PROXY;
  }

  const ctx = await browser.newContext(ctxOpts);

  // Anti-detection: override navigator properties
  await ctx.addInitScript(() => {
    // Hide webdriver
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    
    // Fix plugins (mobile has none, that's normal for Safari)
    if (!navigator.plugins.length) {
      // Leave as-is for mobile
    }
    
    // Override chrome object (not present in Safari)
    // delete window.chrome; // Not needed for iPhone UA
    
    // Realistic touch events for iOS
    Object.defineProperty(navigator, 'maxTouchPoints', { get: () => 5 });
    
    // Platform
    Object.defineProperty(navigator, 'platform', { get: () => 'iPhone' });
    
    // Language
    Object.defineProperty(navigator, 'language', { get: () => 'ro-RO' });
    Object.defineProperty(navigator, 'languages', { get: () => ['ro-RO', 'ro', 'en-US', 'en'] });
    
    // Screen (iPhone 15 Pro)
    Object.defineProperty(screen, 'width', { get: () => 393 });
    Object.defineProperty(screen, 'height', { get: () => 852 });
    Object.defineProperty(screen, 'availWidth', { get: () => 393 });
    Object.defineProperty(screen, 'availHeight', { get: () => 852 });
    
    // Hardware concurrency (iPhone has 6 cores)
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 6 });
    
    // Memory (4GB iPhone)
    // Object.defineProperty(navigator, 'deviceMemory', { get: () => 4 }); // Safari doesn't expose this
    
    // Connection (LTE/5G)
    if (navigator.connection) {
      Object.defineProperty(navigator.connection, 'effectiveType', { get: () => '4g' });
      Object.defineProperty(navigator.connection, 'rtt', { get: () => rand(30, 80) });
    }
    
    function rand(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
  });

  const page = await ctx.newPage();

  // Add realistic touch simulation for mobile
  if (mobile) {
    await page.addInitScript(() => {
      // Simulate touch
      window.ontouchstart = null;
      window.ontouchmove = null;
      window.ontouchend = null;
    });
  }

  return { browser, ctx, page, humanClick, humanMouseMove, humanType, humanScroll, humanRead, sleep, rand };
}

// ─── EXPORT ───────────────────────────────────────────────────────────────────
module.exports = { 
  launchHuman, 
  humanClick, humanMouseMove, humanType, humanScroll, humanRead,
  sleep, rand,
  PROXY, IPHONE15, DESKTOP_RO
};

// ─── QUICK TEST ───────────────────────────────────────────────────────────────
if (require.main === module) {
  (async () => {
    console.log('🧪 Testing human browser (iPhone 15, Romania)...\n');
    
    const { browser, page, humanScroll, humanRead } = await launchHuman({ mobile: true });
    
    await page.goto('https://ipinfo.io/json', { waitUntil: 'domcontentloaded', timeout: 30000 });
    const info = JSON.parse(await page.textContent('body'));
    console.log(`✅ IP: ${info.ip}`);
    console.log(`✅ Country: ${info.country} (${info.city})`);
    console.log(`✅ Org: ${info.org}`);
    console.log(`✅ Timezone: ${info.timezone}`);
    
    // Test UA
    const ua = await page.evaluate(() => navigator.userAgent);
    console.log(`\n✅ User-Agent: ${ua.slice(0, 80)}...`);
    
    const platform = await page.evaluate(() => navigator.platform);
    const lang = await page.evaluate(() => navigator.language);
    const touch = await page.evaluate(() => navigator.maxTouchPoints);
    console.log(`✅ Platform: ${platform}`);
    console.log(`✅ Language: ${lang}`);
    console.log(`✅ Touch points: ${touch}`);
    
    await browser.close();
    console.log('\n🎉 All good! Browser is fully configured.');
  })().catch(console.error);
}
