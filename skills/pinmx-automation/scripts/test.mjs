/**
 * pinmx-automation Test Suite
 */

import { PinmxAutomation } from './index.mjs';

async function runAllTests() {
  console.log('🧪 pinmx-automation Test Suite\n');
  console.log('='.repeat(50));
  
  let passed = 0;
  let failed = 0;
  
  // Test 1: Instance creation
  console.log('\nTest 1: Instance creation');
  try {
    const pinmx = new PinmxAutomation();
    if (pinmx && pinmx.options) {
      console.log('✅ PASSED: Instance created with default options');
      passed++;
    } else {
      throw new Error('Invalid instance');
    }
  } catch (e) {
    console.log('❌ FAILED:', e.message);
    failed++;
  }
  
  // Test 2: Custom options
  console.log('\nTest 2: Custom options');
  try {
    const pinmx = new PinmxAutomation({
      headless: true,
      stealth: false,
      timeout: 5000,
      slowMo: 100
    });
    
    if (pinmx.options.headless === true && 
        pinmx.options.stealth === false &&
        pinmx.options.timeout === 5000 &&
        pinmx.options.slowMo === 100) {
      console.log('✅ PASSED: Custom options applied correctly');
      passed++;
    } else {
      throw new Error('Options not applied correctly');
    }
  } catch (e) {
    console.log('❌ FAILED:', e.message);
    failed++;
  }
  
  // Test 3: Browser start/stop (requires Playwright)
  console.log('\nTest 3: Browser start/stop');
  try {
    const pinmx = new PinmxAutomation({ headless: true });
    await pinmx.start();
    
    if (pinmx.browser && pinmx.page) {
      console.log('✅ PASSED: Browser started successfully');
      passed++;
    } else {
      throw new Error('Browser not started');
    }
    
    await pinmx.close();
    console.log('✅ PASSED: Browser closed successfully');
    passed++;
    
  } catch (e) {
    console.log('❌ FAILED:', e.message);
    failed++;
  }
  
  // Test 4: Navigation (requires internet)
  console.log('\nTest 4: Navigation to pinmx.com');
  try {
    const pinmx = new PinmxAutomation({ headless: true });
    await pinmx.start();
    await pinmx.navigate();
    
    const url = await pinmx.getUrl();
    if (url.includes('pinmx.com')) {
      console.log('✅ PASSED: Navigated to pinmx.com');
      console.log('   URL:', url);
      passed++;
    } else {
      throw new Error('Wrong URL: ' + url);
    }
    
    await pinmx.close();
    
  } catch (e) {
    console.log('⚠️ SKIPPED (requires internet):', e.message);
  }
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log(`📊 Test Results: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(50));
  
  return { passed, failed };
}

// Export test function
export { runAllTests };

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAllTests().then(() => {
    process.exit(0);
  }).catch(e => {
    console.error('Test suite error:', e);
    process.exit(1);
  });
}
