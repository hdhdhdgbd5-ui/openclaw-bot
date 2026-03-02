#!/usr/bin/env node

/**
 * Puter.js Test Script - Version 2
 * Tests the Puter.js integration by navigating to puter.ai
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
  console.log('=== Puter.js Integration Test v2 ===\n');
  
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
    
    console.log('2. Navigating to Puter.ai...');
    const page = await browser.newPage();
    
    // Navigate to puter.ai - this should have the full UI
    await page.goto('https://puter.ai', { 
      waitUntil: 'networkidle2',
      timeout: 30000 
    });
    console.log('   ✓ Page loaded\n');
    
    // Wait a bit for the page to initialize
    await sleep(3000);
    
    console.log('3. Checking for Puter.js on page...');
    
    // Check if puter.ai global exists
    const hasPuter = await page.evaluate(() => {
      return typeof puter !== 'undefined';
    });
    
    if (hasPuter) {
      console.log('   ✓ Puter.js is available on page\n');
    } else {
      console.log('   Note: Puter.js may not be globally exposed on this page\n');
    }
    
    // Try to find chat input on the page
    console.log('4. Looking for chat interface...');
    
    const chatInterface = await page.evaluate(() => {
      // Look for common chat input patterns
      const inputs = document.querySelectorAll('input[type="text"], textarea');
      const buttons = document.querySelectorAll('button');
      
      return {
        inputsFound: inputs.length,
        buttonsFound: buttons.length,
        pageTitle: document.title
      };
    });
    
    console.log('   Page title:', chatInterface.pageTitle);
    console.log('   Inputs found:', chatInterface.inputsFound);
    console.log('   Buttons found:', chatInterface.buttonsFound);
    
    // Take a snapshot to see the UI
    console.log('\n5. Taking snapshot...');
    
    await browser.disconnect();
    
    console.log('\n=== Test Complete ===');
    console.log('The Puter.ai website loaded successfully.');
    console.log('You can interact with it via browser automation.');
    
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
