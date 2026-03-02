/**
 * API Server - HTTP API to control the browser
 */

import http from 'http';
import url from 'url';
import querystring from 'querystring';
import { createBrowser, getBrowser, closeBrowser } from './browser.mjs';
import { navigateWithCloudflareBypass, waitForCloudflare } from './cloudflare.mjs';
import { solveCaptcha, detectCaptcha } from './captcha.mjs';
import { saveSession, loadSession, clearSession, listSessions, getSessionInfo } from './session.mjs';
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

let server = null;
let currentContext = null;
let currentPage = null;
let config = {
  port: 3000,
  headless: true,
  stealth: true
};

/**
 * Parse request body
 */
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        if (body) {
          resolve(JSON.parse(body));
        } else {
          resolve({});
        }
      } catch (e) {
        resolve({});
      }
    });
    req.on('error', reject);
  });
}

/**
 * Send JSON response
 */
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

/**
 * Handle API requests
 */
async function handleRequest(req, res) {
  const parsedUrl = url.parse(req.url);
  const pathname = parsedUrl.pathname;
  const method = req.method;
  
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (method === 'OPTIONS') {
    sendJSON(res, 200, { ok: true });
    return;
  }
  
  try {
    const body = await parseBody(req);
    const query = querystring.parse(parsedUrl.query);
    
    // Routes
    // === Browser ===
    if (pathname === '/api/browser/start' && method === 'POST') {
      const { headless, stealth } = { ...config, ...body };
      const result = await createBrowser({ headless, stealth });
      currentContext = result.context;
      currentPage = result.pages[0] || await currentContext.newPage();
      sendJSON(res, 200, { success: true, message: 'Browser started' });
      return;
    }
    
    if (pathname === '/api/browser/stop' && method === 'POST') {
      await closeBrowser();
      currentContext = null;
      currentPage = null;
      sendJSON(res, 200, { success: true, message: 'Browser stopped' });
      return;
    }
    
    if (pathname === '/api/browser/status' && method === 'GET') {
      const browser = await getBrowser();
      sendJSON(res, 200, { 
        running: !!browser,
        hasContext: !!currentContext,
        hasPage: !!currentPage
      });
      return;
    }
    
    // === Navigation ===
    if (pathname === '/api/navigate' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available. Start browser first.' });
        return;
      }
      
      const { url, waitTime, bypassCloudflare } = body;
      await navigateWithCloudflareBypass(currentPage, url, { 
        waitTime: waitTime || 5000,
        bypassCloudflare: bypassCloudflare !== false
      });
      
      sendJSON(res, 200, { 
        success: true, 
        url: currentPage.url(),
        title: await currentPage.title()
      });
      return;
    }
    
    // === Tabs ===
    if (pathname === '/api/tabs' && method === 'GET') {
      if (!currentContext) {
        sendJSON(res, 400, { error: 'No context available' });
        return;
      }
      
      const tabs = await getTabs(currentContext);
      const tabInfo = await Promise.all(tabs.map(async (tab, i) => ({
        index: i,
        url: tab.url(),
        title: await tab.title().catch(() => 'N/A')
      })));
      
      sendJSON(res, 200, { tabs: tabInfo });
      return;
    }
    
    if (pathname === '/api/tabs/new' && method === 'POST') {
      if (!currentContext) {
        sendJSON(res, 400, { error: 'No context available' });
        return;
      }
      
      const page = await openTab(currentContext, body.url || null);
      currentPage = page;
      sendJSON(res, 200, { success: true, index: currentContext.pages().length - 1 });
      return;
    }
    
    if (pathname === '/api/tabs/switch' && method === 'POST') {
      if (!currentContext) {
        sendJSON(res, 400, { error: 'No context available' });
        return;
      }
      
      const page = await switchTab(currentContext, body.index);
      if (page) {
        currentPage = page;
        sendJSON(res, 200, { success: true });
      } else {
        sendJSON(res, 404, { error: 'Tab not found' });
      }
      return;
    }
    
    if (pathname === '/api/tabs/close' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      await closeTab(currentPage);
      const tabs = currentContext.pages();
      currentPage = tabs.length > 0 ? tabs[0] : null;
      sendJSON(res, 200, { success: true, remainingTabs: tabs.length });
      return;
    }
    
    // === Screenshot ===
    if (pathname === '/api/screenshot' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const { filename, fullPage, type } = body;
      const path = await screenshot(currentPage, filename || `screenshot-${Date.now()}.png`, {
        fullPage: fullPage || false,
        type: type || 'png'
      });
      
      sendJSON(res, 200, { success: true, path });
      return;
    }
    
    // === Content ===
    if (pathname === '/api/content' && method === 'GET') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const format = query.format || 'html';
      const content = await getPageContent(currentPage, format);
      
      sendJSON(res, 200, { content, format });
      return;
    }
    
    // === Form ===
    if (pathname === '/api/form/fill' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      await fillForm(currentPage, body);
      sendJSON(res, 200, { success: true });
      return;
    }
    
    // === Click ===
    if (pathname === '/api/click' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const { selector } = body;
      const clicked = await clickElement(currentPage, selector);
      sendJSON(res, 200, { success: clicked });
      return;
    }
    
    // === Script ===
    if (pathname === '/api/execute' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const result = await executeScript(currentPage, body.script);
      sendJSON(res, 200, { result });
      return;
    }
    
    // === Session ===
    if (pathname === '/api/session/save' && method === 'POST') {
      if (!currentContext) {
        sendJSON(res, 400, { error: 'No context available' });
        return;
      }
      
      await saveSession(currentContext, body.name || 'default');
      sendJSON(res, 200, { success: true });
      return;
    }
    
    if (pathname === '/api/session/load' && method === 'POST') {
      if (!currentContext) {
        sendJSON(res, 400, { error: 'No context available' });
        return;
      }
      
      const loaded = await loadSession(currentContext, body.name || 'default');
      sendJSON(res, 200, { success: loaded });
      return;
    }
    
    if (pathname === '/api/session/list' && method === 'GET') {
      const sessions = listSessions();
      sendJSON(res, 200, { sessions });
      return;
    }
    
    if (pathname === '/api/session/info' && method === 'GET') {
      const info = getSessionInfo(query.name || 'default');
      sendJSON(res, 200, { info });
      return;
    }
    
    if (pathname === '/api/session/clear' && method === 'POST') {
      clearSession(body.name || 'default');
      sendJSON(res, 200, { success: true });
      return;
    }
    
    // === CAPTCHA ===
    if (pathname === '/api/captcha/detect' && method === 'GET') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const detected = await detectCaptcha(currentPage);
      sendJSON(res, 200, detected);
      return;
    }
    
    if (pathname === '/api/captcha/solve' && method === 'POST') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const solved = await solveCaptcha(currentPage, body);
      sendJSON(res, 200, { success: solved });
      return;
    }
    
    // === Cloudflare ===
    if (pathname === '/api/cloudflare/wait' && method === 'GET') {
      if (!currentPage) {
        sendJSON(res, 400, { error: 'No page available' });
        return;
      }
      
      const bypassed = await waitForCloudflare(currentPage);
      sendJSON(res, 200, { bypassed });
      return;
    }
    
    // === Root ===
    if (pathname === '/' && method === 'GET') {
      sendJSON(res, 200, { 
        name: 'Auto Browser 24/7 API',
        version: '1.0.0',
        endpoints: {
          browser: ['/api/browser/start', '/api/browser/stop', '/api/browser/status'],
          navigation: ['/api/navigate'],
          tabs: ['/api/tabs', '/api/tabs/new', '/api/tabs/switch', '/api/tabs/close'],
          screenshot: ['/api/screenshot'],
          content: ['/api/content'],
          form: ['/api/form/fill'],
          click: ['/api/click'],
          script: ['/api/execute'],
          session: ['/api/session/save', '/api/session/load', '/api/session/list', '/api/session/clear'],
          captcha: ['/api/captcha/detect', '/api/captcha/solve'],
          cloudflare: ['/api/cloudflare/wait']
        }
      });
      return;
    }
    
    // 404
    sendJSON(res, 404, { error: 'Not found' });
    
  } catch (e) {
    console.error('API Error:', e);
    sendJSON(res, 500, { error: e.message });
  }
}

/**
 * Start the API server
 * @param {Object} options - Server options
 * @returns {Promise<http.Server>}
 */
export async function startAPIServer(options = {}) {
  config = { ...config, ...options };
  
  if (server) {
    console.log('Server already running');
    return server;
  }
  
  server = http.createServer(handleRequest);
  
  return new Promise((resolve) => {
    server.listen(config.port, () => {
      console.log(`API Server running on http://localhost:${config.port}`);
      console.log('API Documentation: http://localhost:' + config.port + '/');
      resolve(server);
    });
  });
}

/**
 * Stop the API server
 * @returns {Promise<void>}
 */
export async function stopAPIServer() {
  if (server) {
    await closeBrowser();
    server.close();
    server = null;
    console.log('API Server stopped');
  }
}

/**
 * Get server status
 */
export function getServerStatus() {
  return {
    running: !!server,
    port: config.port
  };
}
