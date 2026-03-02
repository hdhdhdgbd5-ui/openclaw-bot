/**
 * Utility functions for Browser Master
 */

/**
 * Generate random number between min and max
 */
export function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate random float between min and max
 */
export function randomFloat(min, max) {
  return Math.random() * (max - min) + min;
}

/**
 * Generate random delay promise
 */
export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Random delay between min and max ms
 */
export async function randomDelay(min, max) {
  const ms = random(min, max);
  return delay(ms);
}

/**
 * Generate random string
 */
export function randomString(length = 10) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

/**
 * Generate random email
 */
export function randomEmail(domain = 'mailinator.com') {
  const username = randomString(8).toLowerCase();
  return `${username}@${domain}`;
}

/**
 * Generate random username
 */
export function randomUsername() {
  const prefixes = ['user', 'dev', 'test', 'bot', 'auto', 'guest'];
  const suffixes = ['', '123', '99', 'xx', 'pro', 'dev'];
  const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
  const suffix = suffixes[Math.floor(Math.random() * suffixes.length)];
  return `${prefix}${randomString(4)}${suffix}`;
}

/**
 * Generate random password
 */
export function randomPassword(length = 16) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}

/**
 * Generate random phone number
 */
export function randomPhone() {
  return `+1${random(2000000000, 9999999999)}`;
}

/**
 * Check if element exists
 */
export async function elementExists(page, selector) {
  const count = await page.locator(selector).count();
  return count > 0;
}

/**
 * Wait for element to be visible
 */
export async function waitForVisible(page, selector, timeout = 30000) {
  try {
    await page.waitForSelector(selector, { state: 'visible', timeout });
    return true;
  } catch {
    return false;
  }
}

/**
 * Wait for element to disappear
 */
export async function waitForHidden(page, selector, timeout = 30000) {
  try {
    await page.waitForSelector(selector, { state: 'hidden', timeout });
    return true;
  } catch {
    return false;
  }
}

/**
 * Scroll to element
 */
export async function scrollToElement(page, selector) {
  await page.locator(selector).scrollIntoViewIfNeeded();
}

/**
 * Smooth scroll to position
 */
export async function smoothScroll(page, targetY, duration = 1000) {
  const startY = await page.evaluate(() => window.scrollY);
  const distance = targetY - startY;
  const steps = Math.floor(duration / 16);
  const stepSize = distance / steps;

  for (let i = 1; i <= steps; i++) {
    await page.mouse.wheel(0, stepSize);
    await delay(16);
  }
}

/**
 * Check if page has CAPTCHA
 */
export async function detectCaptcha(page) {
  return await page.evaluate(() => {
    // reCAPTCHA
    if (document.querySelector('.g-recaptcha, [data-sitekey]')) {
      return 'recaptcha';
    }
    // hCaptcha
    if (document.querySelector('.h-captcha, [data-hcaptcha-sitekey]')) {
      return 'hcaptcha';
    }
    // Cloudflare
    if (document.querySelector('#cf-challenge, .challenge-running')) {
      return 'cloudflare';
    }
    // Generic
    if (document.querySelector('input[name="captcha"]')) {
      return 'generic';
    }
    return null;
  });
}

/**
 * Wait for network idle
 */
export async function waitForNetworkIdle(page, timeout = 5000) {
  await page.waitForLoadState('networkidle', { timeout });
}

/**
 * Generate random user agent
 */
export function getRandomUserAgent() {
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
  ];
  return userAgents[Math.floor(Math.random() * userAgents.length)];
}

/**
 * Sleep utility
 */
export const sleep = delay;

/**
 * Retry function
 */
export async function retry(fn, maxAttempts = 3, delayMs = 1000) {
  let lastError;
  for (let i = 0; i < maxAttempts; i++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (i < maxAttempts - 1) {
        await delay(delayMs);
      }
    }
  }
  throw lastError;
}

/**
 * Clamp number between min and max
 */
export function clamp(num, min, max) {
  return Math.min(Math.max(num, min), max);
}

/**
 * Map number from one range to another
 */
export function mapRange(value, inMin, inMax, outMin, outMax) {
  return ((value - inMin) * (outMax - outMin)) / (inMax - inMin) + outMin;
}
