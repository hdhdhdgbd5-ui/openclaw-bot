/**
 * 🤖 Browser Master - ULTIMATE Human-Like Browser Automation
 * 
 * The most advanced browser automation that mimics real human behavior!
 */

import { chromium } from 'playwright';
import { random, delay } from './utils.mjs';
import { createServer } from './server.mjs';

export class BrowserMaster {
  constructor(options = {}) {
    this.options = {
      headless: options.headless ?? true,
      stealth: options.stealth ?? true,
      humanLike: options.humanLike ?? true,
      viewport: options.viewport ?? { width: 1920, height: 1080 },
      userAgent: options.userAgent ?? 'random',
      ...options
    };
    
    this.browser = null;
    this.context = null;
    this.page = null;
    this.sessions = new Map();
  }

  /**
   * Start the browser
   */
  async start() {
    // Generate user agent if random
    let userAgent = this.options.userAgent;
    if (userAgent === 'random') {
      userAgent = this.getRandomUserAgent();
    }

    // Launch browser
    const args = [
      '--disable-blink-features=AutomationControlled',
      '--disable-dev-shm-usage',
      '--no-sandbox'
    ];

    if (this.options.stealth) {
      args.push(
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-web-security'
      );
    }

    this.browser = await chromium.launch({
      headless: this.options.headless,
      args
    });

    // Create context with stealth
    this.context = await this.browser.newContext({
      viewport: this.options.viewport,
      userAgent,
      locale: 'en-US',
      timezoneId: 'America/New_York',
      permissions: ['geolocation'],
      extraHTTPHeaders: {
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
      }
    });

    // Create first page
    this.page = await this.context.newPage();
    
    // Apply stealth fixes (must be after page creation)
    if (this.options.stealth) {
      await this.applyStealth();
    }
    
    // Set default timeout
    this.page.setDefaultTimeout(60000);

    return this;
  }

  /**
   * Apply stealth modifications to avoid detection
   */
  async applyStealth() {
    await this.page.addInitScript(() => {
      // Remove webdriver property
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
      });

      // Add Chrome runtime
      window.chrome = {
        runtime: {}
      };

      // Override permissions
      const originalQuery = window.navigator.permissions.query;
      window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
          Promise.resolve({ state: Notification.permission }) :
          originalQuery(parameters)
      );

      // Add plugins
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
      });

      // Add languages
      Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
      });
    });
  }

  /**
   * Get random user agent
   */
  getRandomUserAgents() {
    return [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
      'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ];
  }

  getRandomUserAgent() {
    const agents = this.getRandomUserAgents();
    return agents[Math.floor(Math.random() * agents.length)];
  }

  /**
   * Navigate to URL with human-like behavior
   */
  async navigateHuman(url, options = {}) {
    const { waitUntil = 'networkidle', delay: waitDelay = true } = options;
    
    if (waitDelay && this.options.humanLike) {
      await this.randomDelay(500, 2000);
    }

    await this.page.goto(url, { waitUntil });

    if (this.options.humanLike) {
      // Random scroll after load
      await this.scrollHuman(0, random(100, 300));
    }

    return this;
  }

  /**
   * Navigate to URL
   */
  async navigate(url, options = {}) {
    return this.navigateHuman(url, { ...options, delay: false });
  }

  /**
   * Move mouse to element with human-like curve
   */
  async moveToHuman(selector, options = {}) {
    const { 
      curve = true, 
      overshoot = true, 
      microMovements = true,
      duration = random(500, 1500)
    } = options;

    const element = await this.page.locator(selector).first();
    const box = await element.boundingBox();
    
    if (!box) throw new Error(`Element not found: ${selector}`);

    // Target position (center of element with slight random offset)
    const targetX = box.x + box.width / 2 + random(-10, 10);
    const targetY = box.y + box.height / 2 + random(-10, 10);

    if (curve) {
      // Generate bezier curve points
      const startX = random(0, this.options.viewport.width);
      const startY = random(0, this.options.viewport.height);
      
      // Control points for curve
      const cp1x = startX + (targetX - startX) * random(0.3, 0.7);
      const cp1y = startY + (targetY - startY) * random(-0.5, 0.5);
      const cp2x = targetX + (startX - targetX) * random(0.1, 0.3);
      const cp2y = targetY + (startY - targetY) * random(-0.3, 0.3);

      // Move with curve (simplified - use direct movement with steps)
      await this.page.mouse.move(startX, startY);
      
      // Add micro-movements
      const steps = Math.floor(duration / 16);
      for (let i = 1; i <= steps; i++) {
        const t = i / steps;
        const x = Math.pow(1-t, 3) * startX + 3 * Math.pow(1-t, 2) * t * cp1x + 3 * (1-t) * Math.pow(t, 2) * cp2x + Math.pow(t, 3) * targetX;
        const y = Math.pow(1-t, 3) * startY + 3 * Math.pow(1-t, 2) * t * cp1y + 3 * (1-t) * Math.pow(t, 2) * cp2y + Math.pow(t, 3) * targetY;
        
        if (microMovements && Math.random() < 0.1) {
          // Add jitter
          await this.page.mouse.move(x + random(-2, 2), y + random(-2, 2));
          await this.randomDelay(10, 30);
        }
        
        await this.page.mouse.move(x, y);
        await this.randomDelay(16, 20);
      }
    } else {
      // Direct movement
      await this.page.mouse.move(targetX, targetY);
    }

    // Overshoot and return
    if (overshoot && Math.random() < 0.3) {
      const overshootX = targetX + random(15, 30) * (Math.random() > 0.5 ? 1 : -1);
      const overshootY = targetY + random(15, 30) * (Math.random() > 0.5 ? 1 : -1);
      await this.page.mouse.move(overshootX, overshootY);
      await this.randomDelay(50, 150);
      await this.page.mouse.move(targetX, targetY);
    }

    return this;
  }

  /**
   * Click with human-like behavior
   */
  async clickHuman(selector, options = {}) {
    const { jitter = true, doubleClick = false, rightClick = false } = options;

    // First move to element
    await this.moveToHuman(selector, options);

    // Add micro-jitter before click
    if (jitter) {
      const box = await this.page.locator(selector).first().boundingBox();
      if (box) {
        await this.page.mouse.move(
          box.x + box.width / 2 + random(-3, 3),
          box.y + box.height / 2 + random(-3, 3)
        );
        await this.randomDelay(50, 200);
      }
    }

    // Perform click
    if (rightClick) {
      await this.page.mouse.click(
        await this.getElementCenter(selector),
        { button: 'right' }
      );
    } else if (doubleClick) {
      await this.page.mouse.dblclick(await this.getElementCenter(selector));
    } else {
      await this.page.mouse.click(await this.getElementCenter(selector));
    }

    if (this.options.humanLike) {
      await this.randomDelay(100, 500);
    }

    return this;
  }

  /**
   * Get center of element
   */
  async getElementCenter(selector) {
    const box = await this.page.locator(selector).first().boundingBox();
    if (!box) return { x: 0, y: 0 };
    return { x: box.x + box.width / 2, y: box.y + box.height / 2 };
  }

  /**
   * Type with human-like delays and occasional typos
   */
  async typeHuman(selector, text, options = {}) {
    const { 
      minDelay = 30, 
      maxDelay = 120,
      makeTypos = true,
      typoRate = 0.05,
      correctTypos = true,
      clearFirst = true
    } = options;

    // Clear existing content
    if (clearFirst) {
      await this.page.locator(selector).first().click();
      await this.page.keyboard.press('Control+a');
      await this.page.keyboard.press('Backspace');
    }

    // Type each character
    for (let i = 0; i < text.length; i++) {
      let char = text[i];

      // Occasionally make typos
      if (makeTypos && Math.random() < typoRate) {
        // Type wrong char
        const wrongChar = String.fromCharCode(97 + Math.floor(Math.random() * 26));
        await this.page.keyboard.type(wrongChar);
        
        if (correctTypos) {
          // Backspace and correct
          await this.randomDelay(50, 200);
          await this.page.keyboard.press('Backspace');
        }
      }

      // Type correct char
      await this.page.keyboard.type(char);
      await this.randomDelay(minDelay, maxDelay);
    }

    return this;
  }

  /**
   * Type text (simple version)
   */
  async type(selector, text, options = {}) {
    return this.typeHuman(selector, text, { ...options, makeTypos: false });
  }

  /**
   * Click element (simple version)
   */
  async click(selector) {
    await this.page.locator(selector).click();
    return this;
  }

  /**
   * Scroll like a human
   */
  async scrollHuman(x = 0, y = null, options = {}) {
    const { smooth = true } = options;
    
    const viewportHeight = this.options.viewport.height;
    const scrollY = y ?? random(viewportHeight * 0.5, viewportHeight);
    
    // Get current scroll position
    const currentScroll = await this.page.evaluate(() => window.scrollY);
    const targetScroll = currentScroll + scrollY;

    if (smooth) {
      // Smooth scroll in steps
      const steps = random(5, 15);
      const stepSize = scrollY / steps;
      
      for (let i = 1; i <= steps; i++) {
        await this.page.mouse.wheel(0, stepSize);
        await this.randomDelay(50, 150);
        
        // Occasionally pause
        if (Math.random() < 0.2) {
          await this.randomDelay(200, 800);
        }
      }
    } else {
      await this.page.mouse.wheel(0, scrollY);
    }

    return this;
  }

  /**
   * Scroll to bottom like a human
   */
  async scrollToBottomHuman(options = {}) {
    const { pauses = true, speed = 'medium' } = options;
    
    const speedMap = {
      slow: [200, 400],
      medium: [400, 700],
      fast: [700, 1000]
    };
    
    const [minScroll, maxScroll] = speedMap[speed] || speedMap.medium;

    while (true) {
      const beforeScroll = await this.page.evaluate(() => document.body.scrollHeight);
      
      await this.page.mouse.wheel(0, random(minScroll, maxScroll));
      await this.randomDelay(100, 300);

      if (pauses && Math.random() < 0.3) {
        await this.randomDelay(500, 2000);
      }

      const afterScroll = await this.page.evaluate(() => window.scrollY + window.innerHeight);
      
      if (afterScroll >= beforeScroll) {
        break;
      }
    }

    return this;
  }

  /**
   * Scroll to element
   */
  async scrollTo(selector) {
    await this.page.locator(selector).scrollIntoViewIfNeeded();
    return this;
  }

  /**
   * Random delay
   */
  async randomDelay(min, max) {
    const ms = random(min, max);
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Detect CAPTCHA on page
   */
  async detectCaptcha() {
    const captcha = await this.page.evaluate(() => {
      // Check for reCAPTCHA
      const recaptcha = document.querySelector('.g-recaptcha, [data-sitekey]');
      if (recaptcha) {
        const siteKey = recaptcha.dataset?.sitekey || 
          recaptcha.getAttribute('data-sitekey');
        return { type: 'recaptcha', siteKey };
      }

      // Check for hCaptcha
      const hcaptcha = document.querySelector('.h-captcha, [data-hcaptcha-sitekey]');
      if (hcaptcha) {
        return { type: 'hcaptcha', siteKey: hcaptcha.dataset?.hcaptchaSitekey };
      }

      // Check for Cloudflare challenge
      const cloudflare = document.querySelector('#cf-challenge');
      if (cloudflare) {
        return { type: 'cloudflare' };
      }

      // Check for generic captcha
      const genericCaptcha = document.querySelector(
        'input[name="captcha"], input[id*="captcha"], img[src*="captcha"]'
      );
      if (genericCaptcha) {
        return { type: 'generic' };
      }

      return null;
    });

    return captcha;
  }

  /**
   * Solve detected CAPTCHA
   */
  async solveCaptcha(options = {}) {
    const { autoSubmit = true } = options;
    
    const captcha = await this.detectCaptcha();
    if (!captcha) {
      console.log('No CAPTCHA detected');
      return false;
    }

    console.log('Detected CAPTCHA:', captcha.type);

    switch (captcha.type) {
      case 'recaptcha':
        return await this.solveRecaptcha(captcha.siteKey, { autoSubmit });
      case 'hcaptcha':
        return await this.solveHCaptcha(captcha.siteKey, { autoSubmit });
      case 'cloudflare':
        return await this.waitForCloudflare();
      default:
        console.log('Unknown CAPTCHA type');
        return false;
    }
  }

  /**
   * Solve reCAPTCHA
   */
  async solveRecaptcha(siteKey, options = {}) {
    const { autoSubmit = true } = options;
    
    try {
      // Click on reCAPTCHA iframe
      const recaptchaFrame = await this.page.frameLocator(
        'iframe[src*="google.com/recaptcha"]'
      ).first();
      
      if (recaptchaFrame) {
        await recaptchaFrame.locator('.recaptcha-checkbox').click();
        await this.randomDelay(1000, 3000);
      }

      // Note: In production, integrate with 2Captcha or similar
      // For now, just wait for manual solve
      console.log('Please complete reCAPTCHA manually...');
      await this.randomDelay(5000, 10000);

      return true;
    } catch (e) {
      console.error('Failed to solve reCAPTCHA:', e.message);
      return false;
    }
  }

  /**
   * Solve hCaptcha
   */
  async solveHCaptcha(siteKey, options = {}) {
    try {
      // Click on hCaptcha
      const hcaptcha = await this.page.locator('.h-captcha');
      if (await hcaptcha.count() > 0) {
        await hcaptcha.click();
        await this.randomDelay(1000, 3000);
      }

      // Note: In production, integrate with 2Captcha or similar
      console.log('Please complete hCaptcha manually...');
      await this.randomDelay(5000, 10000);

      return true;
    } catch (e) {
      console.error('Failed to solve hCaptcha:', e.message);
      return false;
    }
  }

  /**
   * Wait for Cloudflare challenge
   */
  async waitForCloudflare(timeout = 30000) {
    try {
      await this.page.waitForFunction(() => {
        return !document.querySelector('#cf-challenge, .challenge-running');
      }, { timeout });

      await this.randomDelay(1000, 3000);
      return true;
    } catch (e) {
      console.error('Cloudflare challenge timeout');
      return false;
    }
  }

  /**
   * Navigate with Cloudflare bypass
   */
  async navigateWithCloudflare(url) {
    await this.navigateHuman(url);
    return await this.waitForCloudflare();
  }

  /**
   * Auto-signup for a service
   */
  async autoSignup(url, options = {}) {
    const {
      email = 'auto',
      username = 'auto',
      password = 'auto',
      fillProfile = true,
      verifyEmail = false
    } = options;

    // Generate credentials
    const creds = {
      email: email === 'auto' ? this.generateTempEmail() : email,
      username: username === 'auto' ? this.generateUsername() : username,
      password: password === 'auto' ? this.generatePassword() : password
    };

    // Navigate to signup page
    await this.navigateHuman(url);

    // Try to fill common signup fields
    const fieldMappings = {
      'input[name="email"], input[type="email"], input[id="email"]': creds.email,
      'input[name="username"], input[id="username"], input[name="login"]': creds.username,
      'input[name="password"], input[type="password"], input[id="password"]': creds.password,
      'input[name="confirm_password"], input[name="confirmPassword"]': creds.password,
      'input[name="name"], input[name="full_name"], input[id="name"]': creds.username
    };

    for (const [selector, value] of Object.entries(fieldMappings)) {
      try {
        const element = await this.page.locator(selector).first();
        if (await element.count() > 0) {
          await this.typeHuman(selector, value);
        }
      } catch (e) {
        // Element not found, skip
      }
    }

    // Click submit if found
    try {
      const submitBtn = await this.page.locator(
        'button[type="submit"], input[type="submit"], a[data-action="signup"]'
      ).first();
      if (await submitBtn.count() > 0) {
        await this.clickHuman(await submitBtn);
      }
    } catch (e) {
      // No submit button found
    }

    // Wait for verification email if needed
    if (verifyEmail) {
      await this.randomDelay(5000, 10000);
      // In production, check temp email for verification link
    }

    return creds;
  }

  /**
   * Generate temp email
   */
  generateTempEmail() {
    const randomStr = Math.random().toString(36).substring(2, 10);
    return `auto${randomStr}@mailinator.com`;
  }

  /**
   * Generate random username
   */
  generateUsername() {
    const randomStr = Math.random().toString(36).substring(2, 8);
    const names = ['user', 'dev', 'test', 'auto', 'bot'];
    return `${names[Math.floor(Math.random() * names.length)]}${randomStr}`;
  }

  /**
   * Generate strong password
   */
  generatePassword() {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return password;
  }

  /**
   * Fill form with human-like typing
   */
  async fillFormHuman(formData, options = {}) {
    for (const [selector, value] of Object.entries(formData)) {
      try {
        await this.typeHuman(selector, String(value), options);
      } catch (e) {
        console.log(`Failed to fill ${selector}:`, e.message);
      }
    }
    return this;
  }

  /**
   * Close modal if present
   */
  async closeModal(options = {}) {
    const { accept = false } = options;

    // Try close button
    const closeButtons = await this.page.locator(
      '.modal .close, .modal-header .close, [data-dismiss="modal"], button.close'
    ).all();
    
    for (const btn of closeButtons) {
      if (await btn.isVisible()) {
        await btn.click();
        return true;
      }
    }

    // Try escape key
    await this.page.keyboard.press('Escape');
    
    return false;
  }

  /**
   * Switch to iframe
   */
  async switchToIframe(selector) {
    const frame = await this.page.frameLocator(selector);
    return frame;
  }

  /**
   * Switch to main frame
   */
  async switchToMain() {
    // Just use the main page
    return this.page;
  }

  /**
   * Wait for element
   */
  async waitForElement(selector, options = {}) {
    const { state = 'visible', timeout = 30000 } = options;
    await this.page.waitForSelector(selector, { state, timeout });
    return this;
  }

  /**
   * Wait for text
   */
  async waitForText(selector, text, options = {}) {
    const { timeout = 30000 } = options;
    await this.page.waitForSelector(selector, { timeout });
    const elementText = await this.page.locator(selector).textContent();
    if (!elementText.includes(text)) {
      throw new Error(`Text "${text}" not found in element`);
    }
    return this;
  }

  /**
   * Wait for network idle
   */
  async waitForNetworkIdle(timeout = 5000) {
    await this.page.waitForLoadState('networkidle', { timeout });
    return this;
  }

  /**
   * Save session
   */
  async saveSession(name) {
    const storage = await this.context.storageState();
    this.sessions.set(name, storage);
    return { name, saved: true };
  }

  /**
   * Load session
   */
  async loadSession(name) {
    const storage = this.sessions.get(name);
    if (!storage) {
      throw new Error(`Session "${name}" not found`);
    }

    // Create new context with saved storage
    const newContext = await this.browser.newContext({
      storageState: storage
    });
    
    this.context = newContext;
    this.page = await newContext.newPage();
    
    return { name, loaded: true };
  }

  /**
   * Get page content
   */
  async getContent() {
    return await this.page.content();
  }

  /**
   * Get page title
   */
  async getTitle() {
    return await this.page.title();
  }

  /**
   * Take screenshot
   */
  async screenshot(options = {}) {
    const { path = 'screenshot.png', fullPage = false } = options;
    await this.page.screenshot({ path, fullPage });
    return path;
  }

  /**
   * Close browser
   */
  async close() {
    if (this.browser) {
      await this.browser.close();
      this.browser = null;
      this.context = null;
      this.page = null;
    }
    return this;
  }
}

/**
 * Start API server
 */
export async function startServer(port = 3001, options = {}) {
  const browser = new BrowserMaster(options);
  await browser.start();
  
  const server = createServer(browser, port);
  return { browser, server };
}

export default BrowserMaster;
