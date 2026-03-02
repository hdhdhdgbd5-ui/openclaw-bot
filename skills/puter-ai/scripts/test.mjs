#!/usr/bin/env node

/**
 * Puter.js Test Script
 * Tests the Puter.js integration
 */

import puppeteer from 'puppeteer-core';

const CDP_PORT = 18800;

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function connectToBrowser() {
  try {
    const browser = await puppeteer.connect({
      browserURL: `http://127.0.0.1:${CDP_PORT}`,
      defaultViewport: null
    });
    return browser;
  } catch (e) {
    console.error('Failed to connect to browser:', e.message);
    return null;
  }
}

async function testPuterJS() {
  console.log('=== Puter.js Integration Test ===\n');
  
  let browser = null;
  
  try {
    console.log('1. Connecting to browser...');
    browser = await connectToBrowser();
    
    if (!browser) {
      console.log('   ❌ Browser not available. Make sure OpenClaw browser is running.');
      console.log('   Run: browser action=start profile=openclaw');
      return false;
    }
    console.log('   ✓ Connected to browser\n');
    
    console.log('2. Creating test page...');
    const page = await browser.newPage();
    console.log('   ✓ Page created\n');
    
    console.log('3. Loading Puter.js library...');
    await page.goto('data:text/html,<html><head><title>Test</title></head><body></body></html>', {
      waitUntil: 'networkidle0'
    });
    await page.addScriptTag({ url: 'https://js.puter.com/v2/' });
    await sleep(3000);
    console.log('   ✓ Puter.js loaded\n');
    
    console.log('4. Testing puter.ai.chat()...');
    
    // Test basic chat
    const testScript = `
      (async () => {
        try {
          const response = await puter.ai.chat("Say 'Hello from Puter.js!' in exactly those words", {
            model: "gemini-2.5-flash-lite"
          });
          return { success: true, response: response };
        } catch (error) {
          return { success: false, error: error.message };
        }
      })()
    `;
    
    const result = await page.evaluate(testScript);
    
    if (result.success) {
      console.log('   ✓ Chat response received!');
      console.log('   Response:', result.response.substring(0, 200) + '...\n');
    } else {
      console.log('   ❌ Error:', result.error);
      return false;
    }
    
    console.log('5. Testing model: gpt-5-nano...');
    const gptScript = `
      (async () => {
        try {
          const response = await puter.ai.chat("What is 2+2?", { model: "gpt-5-nano" });
          return { success: true, response: response };
        } catch (error) {
          return { success: false, error: error.message };
        }
      })()
    `;
    
    const gptResult = await page.evaluate(gptScript);
    
    if (gptResult.success) {
      console.log('   ✓ GPT-5 nano response:', gptResult.response.substring(0, 100) + '\n');
    } else {
      console.log('   ⚠ GPT-5 nano:', gptResult.error, '\n');
    }
    
    await browser.disconnect();
    
    console.log('=== All Tests Passed! ===');
    console.log('\nPuter.js is working correctly!');
    console.log('You can now use: node skills/puter-ai/scripts/chat.mjs "Your message"');
    
    return true;
    
  } catch (error) {
    console.error('Test failed:', error.message);
    if (browser) {
      try {
        await browser.disconnect();
      } catch (e) {}
    }
    return false;
  }
}

testPuterJS().then(success => {
  process.exit(success ? 0 : 1);
});
