/**
 * pinmx-automation CLI Entry Point
 */

import { PinmxAutomation } from './index.mjs';

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'test':
      await runTest();
      break;
    case 'server':
      const port = parseInt(args[1] || 3003);
      await startServer(port);
      break;
    default:
      await interactiveMode(args);
  }
}

async function runTest() {
  console.log('🧪 Running pinmx-automation test...\n');

  const pinmx = new PinmxAutomation({
    headless: false,
    stealth: true,
    slowMo: 50
  });

  try {
    // Start browser
    console.log('1. Starting browser...');
    await pinmx.start();
    console.log('   ✓ Browser started\n');

    // Run full automation
    console.log('2. Running automation...');
    const result = await pinmx.runFullAutomation();
    
    if (result.success) {
      console.log('\n✅ Test completed successfully!');
      console.log('📧 Email:', result.email);
    } else {
      console.log('\n❌ Test failed:', result.error);
    }

    // Take screenshot
    console.log('\n3. Taking screenshot...');
    await pinmx.screenshot({ path: 'pinmx_test.png' });
    console.log('   ✓ Screenshot saved to pinmx_test.png');

  } catch (e) {
    console.error('❌ Test error:', e.message);
  } finally {
    await pinmx.close();
  }
}

async function startServer(port) {
  console.log(`📡 Starting pinmx-automation API server on port ${port}...`);
  
  const express = await import('express');
  const app = express.default();
  
  app.use(express.json());
  
  // Health check
  app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
  });
  
  // Create email endpoint
  app.post('/create', async (req, res) => {
    const { headless, stealth } = req.body;
    
    const pinmx = new PinmxAutomation({
      headless: headless ?? false,
      stealth: stealth ?? true
    });
    
    try {
      await pinmx.start();
      const result = await pinmx.runFullAutomation();
      await pinmx.close();
      
      res.json(result);
    } catch (e) {
      await pinmx.close();
      res.status(500).json({ success: false, error: e.message });
    }
  });
  
  app.listen(port, () => {
    console.log(`✅ Server running at http://localhost:${port}`);
  });
}

async function interactiveMode(args) {
  const headless = !args.includes('--visible');
  
  console.log('🚀 Starting pinmx.com automation...\n');

  const pinmx = new PinmxAutomation({
    headless,
    stealth: true,
    slowMo: 50
  });

  try {
    await pinmx.start();
    const result = await pinmx.runFullAutomation();
    
    if (result.success) {
      console.log('\n✅ Automation completed!');
      console.log('📧 Email:', result.email);
      console.log('🔗 Inbox URL:', result.inboxUrl);
    } else {
      console.log('\n❌ Automation failed:', result.error);
    }

    if (!headless) {
      console.log('\n⏸️ Browser open. Press Ctrl+C to close...');
      // Keep browser open in non-headless mode
      await new Promise(() => {});
    } else {
      await pinmx.close();
    }
    
  } catch (e) {
    console.error('❌ Error:', e.message);
    await pinmx.close();
  }
}

// Run main
main().catch(console.error);
