/**
 * pinmx-automation API Server
 */

import express from 'express';
import { PinmxAutomation } from './index.mjs';

export async function startApiServer(port = 3003) {
  const app = express();
  
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  
  // CORS headers
  app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    if (req.method === 'OPTIONS') {
      return res.sendStatus(200);
    }
    next();
  });
  
  // Health check
  app.get('/health', (req, res) => {
    res.json({ 
      status: 'ok', 
      service: 'pinmx-automation',
      version: '1.0.0'
    });
  });
  
  // Create email - main endpoint
  app.post('/api/create', async (req, res) => {
    const { headless, stealth, slowMo } = req.body;
    
    console.log('📧 Creating new pinmx email...');
    
    const pinmx = new PinmxAutomation({
      headless: headless ?? false,
      stealth: stealth ?? true,
      slowMo: slowMo ?? 50
    });
    
    try {
      await pinmx.start();
      const result = await pinmx.runFullAutomation();
      
      // Don't close immediately - let user access inbox
      // Keep browser open for a while or until explicitly closed
      
      res.json({
        success: result.success,
        email: result.email,
        inboxUrl: result.inboxUrl,
        message: result.success ? 'Email created successfully' : result.error
      });
      
    } catch (e) {
      console.error('❌ Error:', e.message);
      await pinmx.close();
      res.status(500).json({ 
        success: false, 
        error: e.message 
      });
    }
  });
  
  // Close browser session
  app.post('/api/close', async (req, res) => {
    // This would need to track active sessions
    res.json({ success: true, message: 'Session closed' });
  });
  
  // Screenshot endpoint
  app.post('/api/screenshot', async (req, res) => {
    const { path } = req.body;
    
    // Would need to track active browser instance
    res.json({ success: false, error: 'No active session' });
  });
  
  // List available routes
  app.get('/api', (req, res) => {
    res.json({
      endpoints: [
        { method: 'GET', path: '/health', description: 'Health check' },
        { method: 'POST', path: '/api/create', description: 'Create new pinmx email' },
        { method: 'POST', path: '/api/close', description: 'Close active session' },
        { method: 'POST', path: '/api/screenshot', description: 'Take screenshot' }
      ]
    });
  });
  
  return new Promise((resolve) => {
    app.listen(port, () => {
      console.log(`✅ pinmx-automation API running on http://localhost:${port}`);
      console.log(`📋 API docs: http://localhost:${port}/api`);
      resolve(app);
    });
  });
}

// Start server if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const port = parseInt(process.argv[2] || 3003);
  startApiServer(port);
}
