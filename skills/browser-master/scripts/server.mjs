/**
 * HTTP API Server for Browser Master
 */

import express from 'express';
import cors from 'cors';

export function createServer(browser, port = 3001) {
  const app = express();
  
  app.use(cors());
  app.use(express.json());

  // ==================== Browser Control ====================

  // Get status
  app.get('/api/browser/status', (req, res) => {
    res.json({
      running: !!browser.browser,
      page: !!browser.page,
      sessions: Array.from(browser.sessions.keys())
    });
  });

  // Stop browser
  app.post('/api/browser/stop', async (req, res) => {
    try {
      await browser.close();
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Navigation ====================

  // Navigate
  app.post('/api/navigate', async (req, res) => {
    try {
      const { url, waitUntil = 'networkidle' } = req.body;
      await browser.navigate(url, { waitUntil });
      res.json({ success: true, url });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Navigate human-like
  app.post('/api/navigate/human', async (req, res) => {
    try {
      const { url, waitUntil = 'networkidle' } = req.body;
      await browser.navigateHuman(url, { waitUntil });
      res.json({ success: true, url });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Interactions ====================

  // Click
  app.post('/api/click', async (req, res) => {
    try {
      const { selector } = req.body;
      await browser.click(selector);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Click human-like
  app.post('/api/click/human', async (req, res) => {
    try {
      const { selector, ...options } = req.body;
      await browser.clickHuman(selector, options);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Type
  app.post('/api/type', async (req, res) => {
    try {
      const { selector, text } = req.body;
      await browser.type(selector, text);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Type human-like
  app.post('/api/type/human', async (req, res) => {
    try {
      const { selector, text, ...options } = req.body;
      await browser.typeHuman(selector, text, options);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Scroll
  app.post('/api/scroll', async (req, res) => {
    try {
      const { x = 0, y = 300 } = req.body;
      await browser.scrollHuman(x, y);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Scroll human-like
  app.post('/api/scroll/human', async (req, res) => {
    try {
      const { toBottom = false, ...options } = req.body;
      if (toBottom) {
        await browser.scrollToBottomHuman(options);
      } else {
        await browser.scrollHuman(options.x || 0, options.y || 300);
      }
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Move to element
  app.post('/api/move', async (req, res) => {
    try {
      const { selector, ...options } = req.body;
      await browser.moveToHuman(selector, options);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Page Operations ====================

  // Get content
  app.get('/api/content', async (req, res) => {
    try {
      const content = await browser.getContent();
      res.json({ content });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Get title
  app.get('/api/title', async (req, res) => {
    try {
      const title = await browser.getTitle();
      res.json({ title });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Screenshot
  app.post('/api/screenshot', async (req, res) => {
    try {
      const { path = 'screenshot.png', fullPage = false } = req.body;
      await browser.screenshot({ path, fullPage });
      res.json({ success: true, path });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Waiting ====================

  // Wait for element
  app.post('/api/wait/element', async (req, res) => {
    try {
      const { selector, state = 'visible', timeout = 30000 } = req.body;
      await browser.waitForElement(selector, { state, timeout });
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Wait for text
  app.post('/api/wait/text', async (req, res) => {
    try {
      const { selector, text, timeout = 30000 } = req.body;
      await browser.waitForText(selector, text, { timeout });
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Wait for network idle
  app.get('/api/wait/network', async (req, res) => {
    try {
      const timeout = parseInt(req.query.timeout || 5000);
      await browser.waitForNetworkIdle(timeout);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== CAPTCHA ====================

  // Detect CAPTCHA
  app.get('/api/captcha/detect', async (req, res) => {
    try {
      const captcha = await browser.detectCaptcha();
      res.json({ captcha });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Solve CAPTCHA
  app.post('/api/captcha/solve', async (req, res) => {
    try {
      const result = await browser.solveCaptcha(req.body);
      res.json({ success: result });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Wait for Cloudflare
  app.get('/api/cloudflare/wait', async (req, res) => {
    try {
      const timeout = parseInt(req.query.timeout || 30000);
      const result = await browser.waitForCloudflare(timeout);
      res.json({ success: result });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Signup ====================

  // Auto-signup
  app.post('/api/signup', async (req, res) => {
    try {
      const { url, ...options } = req.body;
      const account = await browser.autoSignup(url, options);
      res.json({ success: true, account });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Fill form
  app.post('/api/form/fill', async (req, res) => {
    try {
      const { data, ...options } = req.body;
      await browser.fillFormHuman(data, options);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Session ====================

  // Save session
  app.post('/api/session/save', async (req, res) => {
    try {
      const { name = 'default' } = req.body;
      const result = await browser.saveSession(name);
      res.json(result);
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Load session
  app.post('/api/session/load', async (req, res) => {
    try {
      const { name = 'default' } = req.body;
      const result = await browser.loadSession(name);
      res.json(result);
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // List sessions
  app.get('/api/session/list', (req, res) => {
    res.json({ sessions: Array.from(browser.sessions.keys()) });
  });

  // Clear session
  app.post('/api/session/clear', (req, res) => {
    const { name } = req.body;
    if (name) {
      browser.sessions.delete(name);
    } else {
      browser.sessions.clear();
    }
    res.json({ success: true });
  });

  // ==================== Modals ====================

  // Close modal
  app.post('/api/modal/close', async (req, res) => {
    try {
      const { accept = false } = req.body;
      const closed = await browser.closeModal({ accept });
      res.json({ success: true, closed });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // ==================== Iframes ====================

  // Switch to iframe
  app.post('/api/iframe/switch', async (req, res) => {
    try {
      const { selector } = req.body;
      await browser.switchToIframe(selector);
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Switch to main
  app.post('/api/iframe/main', async (req, res) => {
    try {
      await browser.switchToMain();
      res.json({ success: true });
    } catch (e) {
      res.status(500).json({ error: e.message });
    }
  });

  // Start server
  const server = app.listen(port, () => {
    console.log(`🌐 Browser Master API running on http://localhost:${port}`);
  });

  return server;
}

export default createServer;
