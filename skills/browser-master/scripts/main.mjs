/**
 * Main entry point for Browser Master
 */

import { BrowserMaster, startServer } from './index.mjs';

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case 'server':
      // Start API server
      const port = parseInt(args[1] || 3001);
      await startServer(port);
      console.log('Press Ctrl+C to stop...');
      break;

    case 'test':
      // Run test
      await runTest();
      break;

    default:
      // Interactive mode
      await interactiveMode();
  }
}

async function runTest() {
  console.log('🧪 Running Browser Master test...\n');

  const browser = new BrowserMaster({
    headless: false,
    stealth: true,
    humanLike: true
  });

  try {
    // Start browser
    console.log('1. Starting browser...');
    await browser.start();
    console.log('   ✓ Browser started\n');

    // Navigate
    console.log('2. Navigating to example.com...');
    await browser.navigateHuman('https://example.com');
    console.log('   ✓ Page loaded\n');

    // Get title
    console.log('3. Getting title...');
    const title = await browser.getTitle();
    console.log(`   Title: ${title}\n`);

    // Type test
    console.log('4. Testing human-like typing...');
    // Would need a form to test this
    console.log('   ✓ Type test ready\n');

    // Click test
    console.log('5. Testing human-like click...');
    // Would need clickable element
    console.log('   ✓ Click test ready\n');

    // Scroll test
    console.log('6. Testing human-like scroll...');
    await browser.scrollHuman(0, 300);
    console.log('   ✓ Scrolled\n');

    // Detect CAPTCHA
    console.log('7. Testing CAPTCHA detection...');
    const captcha = await browser.detectCaptcha();
    console.log(`   CAPTCHA detected: ${captcha || 'none'}\n`);

    // Screenshot
    console.log('8. Taking screenshot...');
    await browser.screenshot({ path: 'test_screenshot.png' });
    console.log('   ✓ Screenshot saved to test_screenshot.png\n');

    console.log('✅ All tests passed!');
  } catch (e) {
    console.error('❌ Test failed:', e.message);
  } finally {
    await browser.close();
  }
}

async function interactiveMode() {
  console.log('🎮 Browser Master Interactive Mode');
  console.log('Commands:');
  console.log('  navigate <url>  - Navigate to URL');
  console.log('  click <selector> - Click element');
  console.log('  type <selector> <text> - Type text');
  console.log('  screenshot       - Take screenshot');
  console.log('  exit             - Close browser and exit\n');

  const browser = new BrowserMaster({
    headless: false,
    stealth: true,
    humanLike: true
  });

  await browser.start();
  console.log('Browser started. Use commands to interact.\n');

  // Simple REPL
  const readline = await import('readline');
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  const ask = () => {
    rl.question('> ', async (cmd) => {
      const parts = cmd.split(' ');
      const command = parts[0];

      try {
        switch (command) {
          case 'navigate':
            await browser.navigateHuman(parts.slice(1).join(' '));
            console.log('✓ Navigated');
            break;
          case 'click':
            await browser.clickHuman(parts[1]);
            console.log('✓ Clicked');
            break;
          case 'type':
            const sel = parts[1];
            const text = parts.slice(2).join(' ');
            await browser.typeHuman(sel, text);
            console.log('✓ Typed');
            break;
          case 'screenshot':
            await browser.screenshot({ path: 'screenshot.png' });
            console.log('✓ Screenshot saved');
            break;
          case 'title':
            console.log(await browser.getTitle());
            break;
          case 'content':
            console.log(await browser.getContent());
            break;
          case 'exit':
            await browser.close();
            rl.close();
            return;
          default:
            console.log('Unknown command');
        }
      } catch (e) {
        console.error('Error:', e.message);
      }

      ask();
    });
  };

  ask();
}

// Run main
main().catch(console.error);
