#!/usr/bin/env node

/**
 * Puter.ai Chat Script
 * Uses browser automation to chat with Puter.ai website
 * No API key required!
 * 
 * Usage: node chat-website.mjs "Your message here"
 */

import puppeteer from 'puppeteer-core';

const CDP_PORT = 18800;
const MAX_RETRIES = 3;
const RETRY_DELAY = 3000;

let MODEL = 'gemini-2.5-flash-lite';

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function connectToBrowser() {
  const browser = await puppeteer.connect({
    browserURL: `http://127.0.0.1:${CDP_PORT}`,
    defaultViewport: null
  });
  return browser;
}

async function findPuterPage(browser) {
  const targets = await browser.targets();
  
  // Find existing Puter.ai page
  let puterTarget = targets.find(t => t.url().includes('puter.ai'));
  
  if (puterTarget) {
    return await puterTarget.page();
  }
  
  // Create new page and navigate
  const page = await browser.newPage();
  await page.goto('https://puter.ai', { waitUntil: 'networkidle2', timeout: 30000 });
  return page;
}

async function sendMessage(page, message) {
  console.log('Looking for chat input...');
  
  // Try to find and fill the chat input
  const inputFound = await page.evaluate(() => {
    // Look for various input types commonly used in chat interfaces
    const selectors = [
      'input[type="text"]',
      'textarea',
      'input[placeholder*="message" i]',
      'input[placeholder*="chat" i]',
      '[contenteditable="true"]'
    ];
    
    for (const selector of selectors) {
      const input = document.querySelector(selector);
      if (input) {
        return { found: true, tag: input.tagName, selector };
      }
    }
    return { found: false };
  });
  
  console.log('Input found:', inputFound);
  
  if (!inputFound.found) {
    throw new Error('Could not find chat input');
  }
  
  // Click on the input and type
  await page.click('input[type="text"], textarea');
  await sleep(500);
  
  // Type the message
  await page.keyboard.type(message, { delay: 30 });
  await sleep(300);
  
  // Look for send button and click it, or press Enter
  const sendButton = await page.evaluate(() => {
    const buttons = document.querySelectorAll('button');
    for (const btn of buttons) {
      if (btn.textContent.toLowerCase().includes('send') ||
          btn.textContent.toLowerCase().includes('submit') ||
          btn.querySelector('svg')) {
        return true;
      }
    }
    return false;
  });
  
  if (sendButton) {
    await page.click('button');
  } else {
    await page.keyboard.press('Enter');
  }
  
  console.log('Message sent');
}

async function waitForResponse(page, timeout = 30000) {
  console.log('Waiting for response...');
  
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    // Look for response in the page
    const response = await page.evaluate(() => {
      // Look for messages/bubbles in the chat
      const messages = document.querySelectorAll('[data-role="message"], .message, .response, article');
      
      if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        return lastMessage.textContent.substring(0, 500);
      }
      return null;
    });
    
    if (response && response.length > 10) {
      console.log('Response found!');
      return response;
    }
    
    await sleep(1000);
  }
  
  // Take snapshot to see what's happening
  console.log('Taking snapshot to debug...');
  return 'Timeout waiting for response';
}

async function chat(message) {
  let browser;
  let retries = 0;
  
  while (retries < MAX_RETRIES) {
    try {
      console.log(`Connecting to browser (attempt ${retries + 1}/${MAX_RETRIES})...`);
      browser = await connectToBrowser();
      
      console.log('Finding Puter.ai page...');
      const page = await findPuterPage(browser);
      
      // Wait for page to settle
      await sleep(2000);
      
      await sendMessage(page, message);
      const response = await waitForResponse(page);
      
      await browser.disconnect();
      
      if (response && response.length > 5) {
        return response;
      }
      
    } catch (error) {
      console.error(`Error: ${error.message}`);
      retries++;
      
      if (browser) {
        try {
          await browser.disconnect();
        } catch (e) {}
      }
      
      if (retries < MAX_RETRIES) {
        console.log(`Retrying in ${RETRY_DELAY}ms...`);
        await sleep(RETRY_DELAY);
      }
    }
  }
  
  throw new Error('Failed to get response after retries');
}

// Parse arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const messages = [];
  
  for (const arg of args) {
    if (!arg.startsWith('--')) {
      messages.push(arg);
    }
  }
  
  return messages.join(' ');
}

// Main
async function main() {
  const message = parseArgs();
  
  if (!message) {
    console.log('Usage: node chat-website.mjs "Your message here"');
    console.log('Example: node chat-website.mjs "Hello AI!"');
    process.exit(1);
  }
  
  console.log(`Message: ${message}\n`);
  
  try {
    const response = await chat(message);
    console.log('\n=== RESPONSE ===');
    console.log(response);
    console.log('================\n');
  } catch (error) {
    console.error('Failed:', error.message);
    process.exit(1);
  }
}

main();
