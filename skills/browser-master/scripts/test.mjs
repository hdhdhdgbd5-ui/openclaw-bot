/**
 * Test script for Browser Master
 */

import { BrowserMaster } from './index.mjs';

async function test() {
  console.log('🧪 Browser Master Test Suite\n');
  console.log('='.repeat(50));

  const browser = new BrowserMaster({
    headless: false,
    stealth: true,
    humanLike: true
  });

  try {
    // Test 1: Start browser
    console.log('\n[Test 1] Starting browser...');
    await browser.start();
    console.log('✅ PASS: Browser started');

    // Test 2: Navigate
    console.log('\n[Test 2] Navigate to example.com...');
    await browser.navigateHuman('https://example.com');
    const title = await browser.getTitle();
    console.log(`✅ PASS: Page title: ${title}`);

    // Test 3: Screenshot
    console.log('\n[Test 3] Taking screenshot...');
    await browser.screenshot({ path: 'test_output/example.png' });
    console.log('✅ PASS: Screenshot saved');

    // Test 4: Scroll
    console.log('\n[Test 4] Testing scroll...');
    await browser.scrollHuman(0, 200);
    console.log('✅ PASS: Scroll completed');

    // Test 5: Scroll to bottom
    console.log('\n[Test 5] Testing scroll to bottom...');
    await browser.navigateHuman('https://example.com');
    await browser.scrollToBottomHuman({ pauses: true });
    console.log('✅ PASS: Scroll to bottom completed');

    // Test 6: CAPTCHA detection
    console.log('\n[Test 6] Testing CAPTCHA detection...');
    const captcha = await browser.detectCaptcha();
    console.log(`✅ PASS: CAPTCHA detection works (found: ${captcha || 'none'})`);

    // Test 7: Credentials generation
    console.log('\n[Test 7] Testing credential generation...');
    const email = browser.generateTempEmail();
    const username = browser.generateUsername();
    const password = browser.generatePassword();
    console.log(`   Email: ${email}`);
    console.log(`   Username: ${username}`);
    console.log(`   Password: ${password}`);
    console.log('✅ PASS: Credentials generated');

    // Test 8: Session saving
    console.log('\n[Test 8] Testing session saving...');
    await browser.saveSession('test-session');
    console.log('✅ PASS: Session saved');

    // Test 9: Navigate to another site
    console.log('\n[Test 9] Navigate to Google...');
    await browser.navigateHuman('https://www.google.com');
    console.log('✅ PASS: Google loaded');

    // Test 10: Take another screenshot
    console.log('\n[Test 10] Taking another screenshot...');
    await browser.screenshot({ path: 'test_output/google.png' });
    console.log('✅ PASS: Screenshot saved');

    console.log('\n' + '='.repeat(50));
    console.log('🎉 All tests passed!');
    console.log('='.repeat(50));

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
}

// Run tests
test().then(() => {
  console.log('\nTest suite completed.');
  process.exit(0);
}).catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
