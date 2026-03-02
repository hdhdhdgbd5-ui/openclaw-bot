/**
 * Session Manager - Save and restore browser sessions
 */

import fs from 'fs';
import path from 'path';

const SESSION_DIR = path.join(process.cwd(), '.browser-sessions');

/**
 * Ensure session directory exists
 */
function ensureSessionDir() {
  if (!fs.existsSync(SESSION_DIR)) {
    fs.mkdirSync(SESSION_DIR, { recursive: true });
  }
}

/**
 * Save session (cookies, localStorage, sessionStorage) for a domain
 * @param {BrowserContext} context - Playwright browser context
 * @param {string} sessionName - Name for the session
 * @returns {Promise<void>}
 */
export async function saveSession(context, sessionName) {
  ensureSessionDir();
  
  const sessionPath = path.join(SESSION_DIR, `${sessionName}.json`);
  
  // Get cookies
  const cookies = await context.cookies();
  
  // Get origin storage (localStorage, sessionStorage)
  const storageData = await context.evaluate(() => {
    const data = {
      localStorage: {},
      sessionStorage: {}
    };
    
    try {
      // Get localStorage
      for (const key of Object.keys(localStorage)) {
        data.localStorage[key] = localStorage.getItem(key);
      }
      
      // Get sessionStorage
      for (const key of Object.keys(sessionStorage)) {
        data.sessionStorage[key] = sessionStorage.getItem(key);
      }
    } catch (e) {
      // May fail due to cross-origin
      console.warn('Could not access storage:', e.message);
    }
    
    return data;
  });
  
  const session = {
    name: sessionName,
    savedAt: new Date().toISOString(),
    cookies,
    storage: storageData
  };
  
  fs.writeFileSync(sessionPath, JSON.stringify(session, null, 2));
  console.log(`Session saved: ${sessionName}`);
}

/**
 * Load session (cookies, localStorage, sessionStorage) for a domain
 * @param {BrowserContext} context - Playwright browser context
 * @param {string} sessionName - Name of the session to load
 * @returns {Promise<boolean>}
 */
export async function loadSession(context, sessionName) {
  const sessionPath = path.join(SESSION_DIR, `${sessionName}.json`);
  
  if (!fs.existsSync(sessionPath)) {
    console.warn(`Session not found: ${sessionName}`);
    return false;
  }
  
  try {
    const session = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
    
    // Restore cookies
    if (session.cookies && session.cookies.length > 0) {
      await context.addCookies(session.cookies);
      console.log(`Restored ${session.cookies.length} cookies`);
    }
    
    // Restore storage
    if (session.storage) {
      await context.evaluate((storage) => {
        try {
          // Restore localStorage
          if (storage.localStorage) {
            for (const [key, value] of Object.entries(storage.localStorage)) {
              localStorage.setItem(key, value);
            }
          }
          
          // Restore sessionStorage
          if (storage.sessionStorage) {
            for (const [key, value] of Object.entries(storage.sessionStorage)) {
              sessionStorage.setItem(key, value);
            }
          }
        } catch (e) {
          console.warn('Could not restore storage:', e.message);
        }
      }, session.storage);
      console.log('Storage restored');
    }
    
    console.log(`Session loaded: ${sessionName}`);
    return true;
  } catch (e) {
    console.error('Error loading session:', e);
    return false;
  }
}

/**
 * Clear a saved session
 * @param {string} sessionName - Name of the session to clear
 * @returns {boolean}
 */
export function clearSession(sessionName) {
  const sessionPath = path.join(SESSION_DIR, `${sessionName}.json`);
  
  if (fs.existsSync(sessionPath)) {
    fs.unlinkSync(sessionPath);
    console.log(`Session cleared: ${sessionName}`);
    return true;
  }
  
  return false;
}

/**
 * List all saved sessions
 * @returns {Array<string>}
 */
export function listSessions() {
  ensureSessionDir();
  
  const files = fs.readdirSync(SESSION_DIR)
    .filter(f => f.endsWith('.json'))
    .map(f => f.replace('.json', ''));
  
  return files;
}

/**
 * Get session info
 * @param {string} sessionName - Name of the session
 * @returns {Object|null}
 */
export function getSessionInfo(sessionName) {
  const sessionPath = path.join(SESSION_DIR, `${sessionName}.json`);
  
  if (!fs.existsSync(sessionPath)) {
    return null;
  }
  
  try {
    const session = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
    return {
      name: session.name,
      savedAt: session.savedAt,
      cookieCount: session.cookies?.length || 0,
      hasLocalStorage: Object.keys(session.storage?.localStorage || {}).length > 0,
      hasSessionStorage: Object.keys(session.storage?.sessionStorage || {}).length > 0
    };
  } catch (e) {
    return null;
  }
}
