/**
 * CAPTCHA Solver Module
 * Handles automatic CAPTCHA solving using 2captcha and other services
 */

import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';

/**
 * 2Captcha API configuration
 */
const CAPTCHA_CONFIG = {
  provider: '2captcha',
  apiKey: process.env.TWOCAPTCHA_API_KEY || '',
  pollingInterval: 5000,
  maxWaitTime: 120000
};

/**
 * Detect if there's a CAPTCHA on the page
 * @param {Page} page - Playwright page
 * @returns {Promise<{type: string, detected: boolean}>}
 */
export async function detectCaptcha(page) {
  try {
    const result = await page.evaluate(() => {
      const results = {
        detected: false,
        type: null,
        details: {}
      };
      
      // Check for reCAPTCHA
      const recaptcha = document.querySelector('.g-recaptcha, [id*="recaptcha"], iframe[src*="recaptcha"]');
      if (recaptcha) {
        results.detected = true;
        results.type = 'recaptcha';
        results.details.siteKey = recaptcha.getAttribute('data-sitekey');
      }
      
      // Check for hCaptcha
      const hcaptcha = document.querySelector('.h-captcha, [id*="hcaptcha"], iframe[src*="hcaptcha"]');
      if (hcaptcha) {
        results.detected = true;
        results.type = 'hcaptcha';
        const iframe = hcaptcha.querySelector('iframe') || hcaptcha;
        results.details.siteKey = iframe.getAttribute('data-sitekey');
      }
      
      // Check for Turnstile
      const turnstile = document.querySelector('[class*="turnstile"], iframe[src*="turnstile"]');
      if (turnstile) {
        results.detected = true;
        results.type = 'turnstile';
        const iframe = turnstile.querySelector('iframe') || turnstile;
        const src = iframe.src || iframe.getAttribute('data-sitekey');
        const match = src?.match(/sitekey=([^&]+)/);
        results.details.siteKey = match ? match[1] : null;
      }
      
      // Check for image CAPTCHA
      const imageCaptcha = document.querySelector('input[name*="captcha"], img[src*="captcha"], #captcha-image');
      if (imageCaptcha && !results.detected) {
        results.detected = true;
        results.type = 'image';
      }
      
      return results;
    });
    
    if (result.detected) {
      console.log(`CAPTCHA detected: ${result.type}`);
    }
    
    return result;
  } catch (e) {
    console.error('Error detecting CAPTCHA:', e);
    return { detected: false, type: null, details: {} };
  }
}

/**
 * Submit CAPTCHA to 2Captcha for solving
 * @param {string} type - CAPTCHA type (recaptcha, hcaptcha, turnstile)
 * @param {string} siteKey - Site key from the page
 * @param {string} pageUrl - URL of the page
 * @returns {Promise<string>} - CAPTCHA ID
 */
export async function submitCaptcha(type, siteKey, pageUrl) {
  if (!CAPTCHA_CONFIG.apiKey) {
    throw new Error('2Capt_CONFIG.apiKey)cha API key not configured. Set TWOCAPTCHA_API_KEY environment variable.');
  }
  
  const params = new URLSearchParams({
    key: CAPTCHA_CONFIG.apiKey,
    method: type,
    pageurl: pageUrl,
    json: 1
  });
  
  if (type === 'recaptcha' || type === 'hcaptcha' || type === 'turnstile') {
    params.append('googlekey', siteKey);
  }
  
  // For image CAPTCHA, would need to upload image
  const url = `http://2captcha.com/in.php?${params.toString()}`;
  
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.status === 1) {
            resolve(result.request);
          } else {
            reject(new Error(`2Captcha error: ${result.request}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

/**
 * Get solved CAPTCHA from 2Captcha
 * @param {string} captchaId - CAPTCHA ID from submit
 * @returns {Promise<string>} - Solved CAPTCHA response
 */
export async function getSolvedCaptcha(captchaId) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < CAPTCHA_CONFIG.maxWaitTime) {
    await new Promise(resolve => setTimeout(resolve, CAPTCHA_CONFIG.pollingInterval));
    
    const url = `http://2captcha.com/res.php?key=${CAPTCHA_CONFIG.apiKey}&action=get&id=${captchaId}&json=1`;
    
    const result = await new Promise((resolve, reject) => {
      http.get(url, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            resolve({ status: 0, request: data });
          }
        });
      }).on('error', reject);
    });
    
    if (result.status === 1) {
      return result.request;
    } else if (result.request !== 'CAPCHA_NOT_READY') {
      throw new Error(`2Captcha error: ${result.request}`);
    }
  }
  
  throw new Error('CAPTCHA solving timeout');
}

/**
 * Solve CAPTCHA on the page automatically
 * @param {Page} page - Playwright page
 * @param {Object} options - Options
 * @returns {Promise<boolean>}
 */
export async function solveCaptcha(page, options = {}) {
  const {
    autoSubmit = true,
    provider = '2captcha'
  } = options;
  
  // Detect CAPTCHA
  const detected = await detectCaptcha(page);
  
  if (!detected.detected) {
    console.log('No CAPTCHA detected');
    return true;
  }
  
  const { type, details } = detected;
  const pageUrl = page.url();
  
  if (!details.siteKey) {
    console.error('Could not extract site key');
    return false;
  }
  
  console.log(`Solving ${type} CAPTCHA...`);
  
  if (provider === '2captcha') {
    try {
      // Submit CAPTCHA
      const captchaId = await submitCaptcha(type, details.siteKey, pageUrl);
      console.log(`CAPTCHA submitted, ID: ${captchaId}`);
      
      // Get solution
      const solution = await getSolvedCaptcha(captchaId);
      console.log('CAPTCHA solved!');
      
      // Submit solution to page
      if (autoSubmit) {
        await page.evaluate((captchaType, captchaResponse) => {
          if (captchaType === 'recaptcha') {
            const textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
            if (textarea) textarea.value = captchaResponse;
            const iframe = document.querySelector('.g-recaptcha iframe');
            if (iframe) {
              const win = iframe.contentWindow;
              if (win && win.document) {
                const recaptcha = win.document.querySelector('[name="g-recaptcha-response"]');
                if (recaptcha) recaptcha.value = captchaResponse;
              }
            }
          } else if (captchaType === 'hcaptcha') {
            const textarea = document.querySelector('textarea[name="h-captcha-response"]');
            if (textarea) textarea.value = captchaResponse;
          } else if (captchaType === 'turnstile') {
            const input = document.querySelector('input[name="cf-turnstile-response"]');
            if (input) input.value = captchaResponse;
            
            // Also try to call the Turnstile callback
            window.__cfTurnstileCallback && window.__cfTurnstileCallback(captchaResponse);
            window.turnstileCallback && window.turnstileCallback(captchaResponse);
          }
        }, type, solution);
        
        // Wait for submission
        await page.waitForTimeout(1000);
        
        return true;
      }
      
      return solution;
    } catch (e) {
      console.error('Error solving CAPTCHA:', e);
      return false;
    }
  }
  
  return false;
}

/**
 * Set 2Captcha API key
 * @param {string} apiKey - API key
 */
export function setCaptchaApiKey(apiKey) {
  CAPTCHA_CONFIG.apiKey = apiKey;
}

/**
 * Get current API key status
 * @returns {boolean}
 */
export function hasCaptchaApiKey() {
  return !!CAPTCHA_CONFIG.apiKey;
}
