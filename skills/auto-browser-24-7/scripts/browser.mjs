/**
 * Browser Manager - Handles Playwright browser creation and management
 */

import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

let globalBrowser = null;
let globalContext = null;

// Default browser options
const DEFAULT_OPTIONS = {
  headless: true,
  stealth: true,
  userDataDir: null,  // For persistent sessions
  viewport: { width: 1920, height: 1080 },
  locale: 'en-US',
  timezoneId: 'America/New_York',
  permissions: [],
  extraHTTPHeaders: {},
  args: [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process'
  ]
};

/**
 * Create a new browser instance
 * @param {Object} options - Browser options
 * @returns {Promise<{browser, context, pages: Array}>}
 */
export async function createBrowser(options = {}) {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  
  // If browser already exists, return existing
  if (globalBrowser && globalBrowser.isConnected()) {
    const pages = globalBrowser.contexts()[0]?.pages() || [];
    return { 
      browser: globalBrowser, 
      context: globalContext, 
      pages 
    };
  }
  
  console.log('Launching browser...');
  
  // Build launch options
  const launchOptions = {
    headless: opts.headless,
    args: opts.args,
    ignoreDefaultArgs: ['--enable-automation'],
    locale: opts.locale,
    timezoneId: opts.timezoneId,
    viewport: opts.viewport
  };
  
  // For persistent sessions, we don't use userDataDir in launch
  // Instead we'll manage sessions separately
  
  // Launch browser
  globalBrowser = await chromium.launch(launchOptions);
  
  // Create context with stealth settings
  globalContext = await globalBrowser.newContext({
    locale: opts.locale,
    timezoneId: opts.timezoneId,
    viewport: opts.viewport,
    permissions: opts.permissions,
    extraHTTPHeaders: opts.extraHTTPHeaders,
    ignoreHTTPSErrors: true
  });
  
  // Inject stealth scripts
  if (opts.stealth) {
    await injectStealthScripts(globalContext);
  }
  
  // Handle browser close
  globalBrowser.on('disconnected', () => {
    console.log('Browser disconnected');
    globalBrowser = null;
    globalContext = null;
  });
  
  const pages = globalContext.pages();
  
  console.log('Browser launched successfully');
  return { 
    browser: globalBrowser, 
    context: globalContext, 
    pages 
  };
}

/**
 * Get the current browser instance
 * @returns {Promise<Browser|null>}
 */
export async function getBrowser() {
  if (globalBrowser && globalBrowser.isConnected()) {
    return globalBrowser;
  }
  return null;
}

/**
 * Close the browser
 */
export async function closeBrowser() {
  if (globalBrowser) {
    try {
      await globalBrowser.close();
    } catch (e) {
      console.error('Error closing browser:', e);
    }
    globalBrowser = null;
    globalContext = null;
    console.log('Browser closed');
  }
}

/**
 * Get current context
 */
export function getContext() {
  return globalContext;
}

/**
 * Inject stealth scripts to avoid detection
 */
async function injectStealthScripts(context) {
  await context.addInitScript(() => {
    // Remove webdriver property
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined,
      configurable: true
    });
    
    // Add chrome runtime
    window.chrome = window.chrome || {};
    
    // Override plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5],
      configurable: true
    });
    
    // Override languages
    Object.defineProperty(navigator, 'languages', {
      get: () => ['en-US', 'en'],
      configurable: true
    });
    
    // Remove automation flags
    window.navigator.chrome = {
      app: {
        isInstalled: false,
        GetDetails: false,
        InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
        RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }
      },
      runtime: {
        lastError: null,
        connect: () => ({}),
        sendMessage: () => ({})
      }
    };
    
    // Prevent detection
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    
    // Add fake notification permission
    Object.defineProperty(Notification, 'permission', {
      get: () => 'default',
      configurable: true
    });
  });
}
