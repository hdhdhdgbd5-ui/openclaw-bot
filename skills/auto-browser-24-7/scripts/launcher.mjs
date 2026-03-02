/**
 * Auto Browser 24/7 Launcher
 * Starts the browser and API server for 24/7 operation
 */

import { createBrowser, getBrowser, closeBrowser } from './browser.mjs';
import { navigateWithCloudflareBypass, waitForCloudflare } from './cloudflare.mjs';
import { startAPIServer, stopAPIServer } from './api-server.mjs';
import fs from 'fs';
import path from 'path';

const CONFIG_FILE = path.join(process.cwd(), '.auto-browser-config.json');

const DEFAULT_CONFIG = {
  headless: true,
  stealth: true,
  apiPort: 3000,
  autoRestart: true,
  maxRestarts: 5,
  restartDelay: 10000,
  startupUrls: [],
  screenshotDir: './screenshots',
  sessionDir: './sessions'
};

/**
 * Load configuration
 */
function loadConfig() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    }
  } catch (e) {
    console.warn('Could not load config, using defaults');
  }
  return DEFAULT_CONFIG;
}

/**
 * Save configuration
 */
function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

/**
 * Main launcher
 */
async function main() {
  const args = process.argv.slice(2);
  const config = loadConfig();
  
  if (args.includes('--help') || args.includes('-h')) {
    printHelp();
    return;
  }
  
  if (args.includes('--version') || args.includes('-v')) {
    console.log('Auto Browser 24/7 v1.0.0');
    return;
  }
  
  const mode = args[0] || 'server';
  
  switch (mode) {
    case 'server':
      await runServer(config);
      break;
    case 'browser':
      await runBrowserOnly(config);
      break;
    case 'test':
      await runTest(config);
      break;
    default:
      console.error(`Unknown mode: ${mode}`);
      printHelp();
  }
}

/**
 * Run server mode (API + Browser)
 */
async function runServer(config) {
  console.log('Starting Auto Browser 24/7 Server...');
  console.log('Config:', config);
  
  // Ensure directories exist
  ensureDir(config.screenshotDir);
  ensureDir(config.sessionDir);
  
  try {
    // Start browser
    console.log('Initializing browser...');
    const { browser, context } = await createBrowser({
      headless: config.headless,
      stealth: config.stealth
    });
    
    // Navigate to startup URLs
    if (config.startupUrls && config.startupUrls.length > 0) {
      console.log('Navigating to startup URLs...');
      const page = context.pages()[0] || await context.newPage();
      
      for (const url of config.startupUrls) {
        try {
          await navigateWithCloudflareBypass(page, url);
          await waitForCloudflare(page);
        } catch (e) {
          console.error(`Error navigating to ${url}:`, e.message);
        }
      }
    }
    
    // Start API server
    console.log(`Starting API server on port ${config.apiPort}...`);
    await startAPIServer({ port: config.apiPort });
    
    console.log('\n✅ Auto Browser 24/7 is running!');
    console.log(`   API: http://localhost:${config.apiPort}`);
    console.log(`   Docs: http://localhost:${config.apiPort}/`);
    console.log('\nPress Ctrl+C to stop\n');
    
    // Keep process alive
    process.on('SIGINT', async () => {
      console.log('\nShutting down...');
      await stopAPIServer();
      process.exit(0);
    });
    
  } catch (e) {
    console.error('Failed to start:', e);
    process.exit(1);
  }
}

/**
 * Run browser only (no API)
 */
async function runBrowserOnly(config) {
  console.log('Starting browser only mode...');
  
  try {
    const { browser, context } = await createBrowser({
      headless: config.headless,
      stealth: config.stealth
    });
    
    const page = await context.newPage();
    
    // Interactive mode
    console.log('Browser opened. Use:');
    console.log('  await page.goto("url")');
    console.log('  await page.screenshot({ path: "file.png" })');
    console.log('  await browser.close()');
    console.log('\nPress Ctrl+C to close browser');
    
    // Keep alive
    process.on('SIGINT', async () => {
      await browser.close();
      process.exit(0);
    });
    
  } catch (e) {
    console.error('Error:', e);
    process.exit(1);
  }
}

/**
 * Run test
 */
async function runTest(config) {
  console.log('Running test...\n');
  
  try {
    // Create browser
    console.log('1. Creating browser...');
    const { browser, context } = await createBrowser({
      headless: false,
      stealth: true
    });
    
    const page = await context.newPage();
    
    // Test navigation
    console.log('2. Testing navigation to example.com...');
    await navigateWithCloudflareBypass(page, '');
    consolehttps://example.com.log(`   Title: ${await page.title()}`);
    
    // Test screenshot
    console.log('3. Testing screenshot...');
    const screenshotPath = `test-${Date.now()}.png`;
    await page.screenshot({ path: screenshotPath });
    console.log(`   Saved: ${screenshotPath}`);
    
    // Test session save
    console.log('4. Testing session save...');
    await saveSession(context, 'test-session');
    console.log('   Session saved');
    
    // Clean up
    console.log('\n✅ All tests passed!');
    await browser.close();
    
    // Clean test files
    if (fs.existsSync(screenshotPath)) {
      fs.unlinkSync(screenshotPath);
    }
    
  } catch (e) {
    console.error('\n❌ Test failed:', e.message);
    process.exit(1);
  }
}

/**
 * Ensure directory exists
 */
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

/**
 * Print help
 */
function printHelp() {
  console.log(`
Auto Browser 24/7 - Fully Automated Browser

Usage:
  node launcher.js [mode] [options]

Modes:
  server    Start API server + browser (default)
  browser   Start browser only (interactive)
  test      Run diagnostic tests

Options:
  --help, -h     Show this help
  --version, -v  Show version

Examples:
  node launcher.js server          # Start API server
  node launcher.js browser        # Start browser only
  node launcher.js test           # Run tests
  PORT=3001 node launcher.js      # Custom port

Environment Variables:
  PORT          API server port (default: 3000)
  HEADLESS=0    Run in visible mode
  TWOCAPTCHA_API_KEY  2Captcha API key for CAPTCHA solving
`);
}

// Import for saveSession
import { saveSession } from './session.mjs';

// Run
main().catch(console.error);
