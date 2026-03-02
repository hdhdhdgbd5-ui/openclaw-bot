/**
 * Cloudflare Bypass API
 * Simple programmatic API for bypassing Cloudflare
 */

import { getStealthBrowser, navigateWithBypass, waitForCloudflare, createStealthPage } from './stealth.mjs';

export default {
  getStealthBrowser,
  createStealthPage,
  navigateWithBypass,
  waitForCloudflare
};

// Example usage
async function example() {
  console.log('Creating stealth browser...');
  const { browser, page } = await createStealthPage({ headless: false });
  
  console.log('Navigating to groq.com...');
  await navigateWithBypass(page, 'https://groq.com', { waitTime: 5000 });
  
  console.log('Page title:', await page.title());
  
  // Get content
  const content = await page.content();
  console.log('Content length:', content.length);
  
  // Close browser
  await browser.close();
}

// If run directly
if (process.argv[1] && process.argv[1].endsWith('api.mjs')) {
  example().catch(console.error);
}
