/**
 * Cloudflare Bypass - Stealth Browser Module
 * Uses puppeteer-extra-plugin-stealth to bypass Cloudflare protection
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const path = require('path');

// Use stealth plugin
puppeteer.use(StealthPlugin());

// Real browser user agents for rotation
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
];

/**
 * Get random user agent
 */
function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

/**
 * Wait for Cloudflare challenge to complete
 */
async function waitForCloudflare(page, timeout = 30000) {
  console.log('[Cloudflare] Waiting for challenge...');
  
  try {
    // Wait for either:
    // 1. Cloudflare challenge to complete (no longer showing challenge)
    // 2. Page to load normally after challenge
    
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeout) {
      // Check if still on Cloudflare challenge page
      const challengeVisible = await page.evaluate(() => {
        // Cloudflare challenge elements
        const challenge = document.querySelector('#challenge-form');
        const cloudflare = document.querySelector('.cloudflare');
        const checking = document.querySelector('.checking');
        const challengeTitle = document.querySelector('[title="Cloudflare"]');
        
        return !!(challenge || cloudflare || checking || challengeTitle);
      });
      
      if (!challengeVisible) {
        // Wait a bit more for page to stabilize
        await page.waitForTimeout(2000);
        console.log('[Cloudflare] Challenge completed!');
        return true;
      }
      
      await page.waitForTimeout(1000);
    }
    
    console.log('[Cloudflare] Timeout waiting for challenge');
    return false;
  } catch (error) {
    console.error('[Cloudflare] Error waiting for challenge:', error.message);
    return false;
  }
}

/**
 * Check if page has Cloudflare protection
 */
async function hasCloudflareProtection(page) {
  return await page.evaluate(() => {
    return !!(
      document.querySelector('.cloudflare') ||
      document.querySelector('#challenge-form') ||
      document.querySelector('[title="Cloudflare"]') ||
      document.body.textContent.includes('Cloudflare') ||
      document.body.textContent.includes('Checking your browser')
    );
  });
}

/**
 * Get stealth browser instance
 */
async function getStealthBrowser(options = {}) {
  const {
    headless = false, // Don't use headless for Cloudflare - it blocks!
    userAgent = getRandomUserAgent(),
    proxy = null,
    args = []
  } = options;
  
  const launchOptions = {
    headless,
    userAgent,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
      '--window-size=1920,1080',
      '--start-maximized',
      ...args
    ]
  };
  
  if (proxy) {
    launchOptions.args.push(`--proxy-server=${proxy}`);
  }
  
  console.log('[Stealth] Launching browser with user agent:', userAgent.substring(0, 50) + '...');
  
  const browser = await puppeteer.launch(launchOptions);
  
  // Additional stealth measures
  const pages = await browser.pages();
  const defaultPage = pages[0] || await browser.newPage();
  
  // Set extra headers
  await defaultPage.setExtraHTTPHeaders({
    'DNT': '1',
    'Accept-Language': 'en-US,en;q=0.9',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1'
  });
  
  return browser;
}

/**
 * Navigate to URL with Cloudflare bypass
 */
async function navigateWithBypass(page, url, options = {}) {
  const {
    waitTime = 5000,
    timeout = 60000,
    waitUntil = 'networkidle2'
  } = options;
  
  console.log('[Stealth] Navigating to:', url);
  
  try {
    await page.goto(url, { waitUntil, timeout });
    
    // Wait for Cloudflare
    await waitForCloudflare(page, timeout - 10000);
    
    // Additional wait for dynamic content
    await page.waitForTimeout(waitTime);
    
    return true;
  } catch (error) {
    console.error('[Stealth] Navigation error:', error.message);
    return false;
  }
}

/**
 * Create a stealth page ready for Cloudflare bypass
 */
async function createStealthPage(options = {}) {
  const browser = await getStealthBrowser(options);
  const page = await browser.newPage();
  
  // Set viewport
  await page.setViewport({ width: 1920, height: 1080 });
  
  // Set custom navigation timeout
  page.setDefaultNavigationTimeout(options.timeout || 60000);
  
  return { browser, page };
}

module.exports = {
  getStealthBrowser,
  createStealthPage,
  navigateWithBypass,
  waitForCloudflare,
  hasCloudflareProtection,
  getRandomUserAgent,
  USER_AGENTS
};
