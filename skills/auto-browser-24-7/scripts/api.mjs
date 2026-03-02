/**
 * Auto Browser 24/7 - Main API
 * Fully automated headless browser with Cloudflare bypass, CAPTCHA solving, session management
 */

import { createBrowser, getBrowser, closeBrowser } from './browser.mjs';
import { navigateWithCloudflareBypass, waitForCloudflare } from './cloudflare.mjs';
import { solveCaptcha, detectCaptcha } from './captcha.mjs';
import { saveSession, loadSession, clearSession } from './session.mjs';
import { 
  openTab, 
  closeTab, 
  switchTab, 
  getTabs,
  screenshot,
  fillForm,
  clickElement,
  getPageContent,
  executeScript
} from './page-utils.mjs';
import { startAPIServer, stopAPIServer } from './api-server.mjs';

export default {
  // Browser management
  createBrowser,
  getBrowser,
  closeBrowser,
  
  // Cloudflare
  navigateWithCloudflareBypass,
  waitForCloudflare,
  
  // CAPTCHA
  solveCaptcha,
  detectCaptcha,
  
  // Session management
  saveSession,
  loadSession,
  clearSession,
  
  // Tab management
  openTab,
  closeTab,
  switchTab,
  getTabs,
  
  // Page operations
  screenshot,
  fillForm,
  clickElement,
  getPageContent,
  executeScript,
  
  // API Server
  startAPIServer,
  stopAPIServer
};

// Example usage
async function example() {
  console.log('Starting Auto Browser 24/7...');
  
  // Create browser with stealth mode
  const { browser, context } = await createBrowser({ 
    headless: true,
    stealth: true
  });
  
  // Create a new page/tab
  const page = await context.newPage();
  
  // Navigate with Cloudflare bypass
  console.log('Navigating to example.com...');
  await navigateWithCloudflareBypass(page, 'https://example.com');
  
  // Take screenshot
  await screenshot(page, 'example.png');
  
  // Get page content
  const title = await page.title();
  console.log('Page title:', title);
  
  // Close browser when done
  await browser.close();
}

// Run if executed directly
if (process.argv[1] && process.argv[1].endsWith('api.mjs')) {
  example().catch(console.error);
}
