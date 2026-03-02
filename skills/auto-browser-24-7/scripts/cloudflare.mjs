/**
 * Cloudflare Bypass Module
 * Handles Cloudflare protection detection and bypass
 */

import fs from 'fs';

/**
 * Check if page is showing Cloudflare challenge
 * @param {Page} page - Playwright page
 * @returns {Promise<boolean>}
 */
export async function isCloudflareChallenge(page) {
  try {
    // Check for Cloudflare challenge elements
    const challenge = await page.evaluate(() => {
      // Check for Cloudflare challenge page
      const cloudflareInputs = document.querySelectorAll('input[name="cf-chlaptcha-response"], input[name="cf-turnstile-response"]');
      const challengeText = document.body.innerText.toLowerCase();
      
      return {
        hasChallenge: cloudflareInputs.length > 0 || 
                      challengeText.includes('cloudflare') ||
                      challengeText.includes('checking your browser') ||
                      challengeText.includes('just a moment') ||
                      challengeText.includes('ddos guard') ||
                      challengeText.includes('checking if the site connection is secure'),
        hasTurnstile: document.querySelectorAll('[class*="turnstile"]').length > 0,
        hasCaptcha: document.querySelectorAll('[class*="captcha"]').length > 0
      };
    });
    
    return challenge.hasChallenge || challenge.hasTurnstile || challenge.hasCaptcha;
  } catch (e) {
    return false;
  }
}

/**
 * Wait for Cloudflare challenge to complete
 * @param {Page} page - Playwright page
 * @param {Object} options - Options
 * @returns {Promise<boolean>}
 */
export async function waitForCloudflare(page, options = {}) {
  const {
    timeout = 30000,
    waitTime = 2000,
    maxRetries = 3
  } = options;
  
  let retries = 0;
  const startTime = Date.now();
  
  while (retries < maxRetries && (Date.now() - startTime) < timeout) {
    // Check if we're past Cloudflare
    const isChallenge = await isCloudflareChallenge(page);
    
    if (!isChallenge) {
      // Wait a bit more for page to settle
      await page.waitForTimeout(waitTime);
      
      // Double check
      const stillChallenge = await isCloudflareChallenge(page);
      if (!stillChallenge) {
        return true;
      }
    }
    
    // Wait before checking again
    await page.waitForTimeout(2000);
    retries++;
  }
  
  return !(await isCloudflareChallenge(page));
}

/**
 * Navigate to URL with Cloudflare bypass
 * @param {Page} page - Playwright page
 * @param {string} url - URL to navigate to
 * @param {Object} options - Navigation options
 * @returns {Promise<Response|null>}
 */
export async function navigateWithCloudflareBypass(page, url, options = {}) {
  const {
    waitTime = 5000,
    timeout = 60000,
    waitUntil = 'networkidle',
    bypassCloudflare = true
  } = options;
  
  console.log(`Navigating to: ${url}`);
  
  try {
    // Navigate to the URL
    const response = await page.goto(url, {
      waitUntil,
      timeout
    });
    
    // Wait for initial load
    await page.waitForTimeout(2000);
    
    // Check for Cloudflare challenge
    if (bypassCloudflare) {
      const hasChallenge = await isCloudflareChallenge(page);
      
      if (hasChallenge) {
        console.log('Cloudflare challenge detected, waiting for bypass...');
        
        // Wait for Cloudflare to complete
        const bypassed = await waitForCloudflare(page, {
          timeout: timeout - 5000,
          waitTime
        });
        
        if (!bypassed) {
          console.warn('Cloudflare challenge may not be fully bypassed');
        }
      }
    }
    
    return response;
  } catch (e) {
    console.error('Navigation error:', e.message);
    
    // Sometimes Cloudflare causes navigation errors, try again
    if (e.message.includes('net::ERR_') || e.message.includes('Timeout')) {
      console.log('Retrying navigation...');
      await page.waitForTimeout(3000);
      return page.goto(url, { waitUntil, timeout: timeout / 2 });
    }
    
    throw e;
  }
}

/**
 * Click through Cloudflare challenge if present
 * @param {Page} page - Playwright page
 * @returns {Promise<boolean>}
 */
export async function clickCloudflareButton(page) {
  try {
    // Find and click Cloudflare verify button
    const clicked = await page.evaluate(() => {
      // Try various Cloudflare button selectors
      const selectors = [
        '#challenge-button',
        'button[type="submit"]',
        'button[class*="challenge"]',
        'button[class*="verify"]',
        '[data-captcha-type="cloudflare"] button',
        '.cf-button',
        'input[type="submit"][value*="Verify"]'
      ];
      
      for (const sel of selectors) {
        const btn = document.querySelector(sel);
        if (btn) {
          btn.click();
          return true;
        }
      }
      return false;
    });
    
    if (clicked) {
      await page.waitForTimeout(3000);
      return await waitForCloudflare(page);
    }
    
    return false;
  } catch (e) {
    console.error('Error clicking Cloudflare button:', e);
    return false;
  }
}

/**
 * Handle Turnstile challenge
 * @param {Page} page - Playwright page
 * @param {string} siteKey - Turnstile site key (optional, auto-detect)
 * @returns {Promise<boolean>}
 */
export async function handleTurnstile(page, siteKey = null) {
  try {
    // Auto-detect site key if not provided
    if (!siteKey) {
      siteKey = await page.evaluate(() => {
        const turnstile = document.querySelector('[class*="turnstile"]') || 
                          document.querySelector('iframe[src*="turnstile"]');
        if (turnstile) {
          const iframe = turnstile.querySelector('iframe') || turnstile;
          const src = iframe.src || iframe.getAttribute('data-sitekey');
          const match = src?.match(/sitekey=([^&]+)/);
          return match ? match[1] : null;
        }
        return null;
      });
    }
    
    if (!siteKey) {
      console.log('No Turnstile challenge detected');
      return true;
    }
    
    console.log('Turnstile challenge detected, manual intervention may be required');
    // Note: Full Turnstile bypass requires 2captcha or similar service
    return false;
  } catch (e) {
    console.error('Error handling Turnstile:', e);
    return false;
  }
}
