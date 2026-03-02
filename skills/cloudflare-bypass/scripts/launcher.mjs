/**
 * Cloudflare Bypass Launcher
 * Usage: node launcher.mjs <url> [--headless] [--timeout <seconds>] [--user-agent <ua>] [--proxy <proxy>]
 */

import { getStealthBrowser, navigateWithBypass, waitForCloudflare } from './stealth.mjs';

const args = process.argv.slice(2);
const url = args[0];

if (!url) {
  console.log('Usage: node launcher.mjs <url> [options]');
  console.log('');
  console.log('Options:');
  console.log('  --headless           Run in headless mode (not recommended for Cloudflare)');
  console.log('  --timeout <seconds> Max wait time for challenge (default: 30)');
  console.log('  --user-agent <ua>   Custom user agent');
  console.log('  --proxy <proxy>     Proxy server (e.g., socks5://127.0.0.1:1080)');
  console.log('');
  console.log('Examples:');
  console.log('  node launcher.mjs "https://groq.com"');
  console.log('  node launcher.mjs "https://example.com" --timeout 60');
  process.exit(1);
}

// Parse options
const options = {
  headless: args.includes('--headless'),
  timeout: 30,
  userAgent: null,
  proxy: null
};

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--timeout' && args[i + 1]) {
    options.timeout = parseInt(args[i + 1], 10);
    i++;
  } else if (args[i] === '--user-agent' && args[i + 1]) {
    options.userAgent = args[i + 1];
    i++;
  } else if (args[i] === '--proxy' && args[i + 1]) {
    options.proxy = args[i + 1];
    i++;
  }
}

console.log('='.repeat(50));
console.log('Cloudflare Bypass Launcher');
console.log('='.repeat(50));
console.log('Target URL:', url);
console.log('Headless:', options.headless ? 'Yes' : 'No (recommended for Cloudflare)');
console.log('Timeout:', options.timeout + 's');
console.log('='.repeat(50));

async function main() {
  let browser;
  
  try {
    console.log('\n[+] Launching stealth browser...');
    browser = await getStealthBrowser({
      headless: options.headless,
      userAgent: options.userAgent,
      proxy: options.proxy
    });
    
    const page = (await browser.pages())[0] || await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    console.log('[+] Navigating to', url);
    console.log('[+] Waiting for Cloudflare challenge...\n');
    
    await page.goto(url, { waitUntil: 'networkidle2', timeout: options.timeout * 1000 });
    
    // Wait for Cloudflare
    await waitForCloudflare(page, options.timeout * 1000);
    
    // Get page title
    const title = await page.title();
    console.log('\n[+] Page title:', title);
    
    // Check if we're past Cloudflare
    const hasProtection = await page.evaluate(() => {
      return !!(
        document.querySelector('.cloudflare') ||
        document.querySelector('#challenge-form') ||
        document.body.textContent.includes('Checking your browser')
      );
    });
    
    if (hasProtection) {
      console.log('[!] WARNING: May still have Cloudflare protection');
    } else {
      console.log('[+] Successfully bypassed Cloudflare!');
    }
    
    // Get some content
    const content = await page.content();
    console.log('\n[+] Page loaded, content length:', content.length, 'bytes');
    console.log('[+] First 500 chars:', content.substring(0, 500));
    
    console.log('\n[+] Keeping browser open for 10 seconds...');
    await new Promise(resolve => setTimeout(resolve, 10000));
    
  } catch (error) {
    console.error('\n[-] Error:', error.message);
  } finally {
    if (browser) {
      console.log('\n[+] Closing browser...');
      await browser.close();
    }
  }
}

main();
