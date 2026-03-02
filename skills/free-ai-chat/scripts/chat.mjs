#!/usr/bin/env node

/**
 * Free AI Chat Script - Uses Bing Copilot via browser automation
 * No API key required!
 * 
 * Usage: node chat.mjs "Your message here"
 */

import puppeteer from 'puppeteer-core';

const CDP_PORT = 18800; // OpenClaw browser port
const MAX_RETRIES = 3;
const RETRY_DELAY = 2000;

// Simple sleep function
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function connectToBrowser() {
  const browser = await puppeteer.connect({
    browserURL: `http://127.0.0.1:${CDP_PORT}`,
    defaultViewport: null
  });
  return browser;
}

async function findCopilotPage(browser) {
  const targets = await browser.targets();
  
  // Find existing Copilot page
  let copilotTarget = targets.find(t => t.url().includes('copilot.microsoft.com'));
  
  if (copilotTarget) {
    return await copilotTarget.page();
  }
  
  // Create new page
  const page = await browser.newPage();
  await page.goto('https://copilot.microsoft.com', { waitUntil: 'networkidle0' });
  return page;
}

async function sendMessage(page, message) {
  console.log('Sending message to Copilot...');
  
  // Wait for page to settle
  await sleep(2000);
  
  // Type the message using keyboard
  await page.keyboard.type(message, { delay: 30 });
  await sleep(300);
  
  // Press Enter to send
  await page.keyboard.press('Enter');
  
  console.log('Message sent, waiting for response...');
}

async function waitForResponse(page, timeout = 30000) {
  console.log('Waiting for response...');
  
  // Wait for response to appear - need to wait for new article to appear
  let foundResponse = false;
  const maxWait = 15000;
  const startTime = Date.now();
  
  while (!foundResponse && (Date.now() - startTime) < maxWait) {
    const response = await page.evaluate(() => {
      // Find all articles
      const articles = Array.from(document.querySelectorAll('article'));
      
      // Look for articles with "Copilot sagte" heading
      for (let i = articles.length - 1; i >= 0; i--) {
        const article = articles[i];
        const heading = article.querySelector('h5, h6');
        if (heading && heading.textContent.includes('Copilot')) {
          // Get all text from paragraphs
          const paragraphs = article.querySelectorAll('p');
          let text = '';
          paragraphs.forEach(p => {
            text += p.textContent + ' ';
          });
          return text.trim();
        }
      }
      return null;
    });
    
    if (response && response.length > 0) {
      return response;
    }
    
    await sleep(1000);
  }
  
  return null;
}

async function chat(message) {
  let browser;
  let retries = 0;
  
  while (retries < MAX_RETRIES) {
    try {
      console.log(`Connecting to browser (attempt ${retries + 1}/${MAX_RETRIES})...`);
      browser = await connectToBrowser();
      
      console.log('Finding Copilot page...');
      const page = await findCopilotPage(browser);
      
      // Wait for page to be fully loaded
      await page.waitForNetworkIdle(3000);
      
      await sendMessage(page, message);
      const response = await waitForResponse(page);
      
      await browser.disconnect();
      
      if (response && response.length > 5) {
        return response;
      }
      
      console.log('No response yet, waiting more...');
      await sleep(5000);
      
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

// Main execution
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node chat.mjs "Your message here"');
    console.log('Example: node chat.mjs "Hello, how are you?"');
    process.exit(1);
  }
  
  const message = args.join(' ');
  console.log(`Message: ${message}`);
  
  try {
    const response = await chat(message);
    console.log('\n=== RESPONSE ===');
    console.log(response);
    console.log('================\n');
  } catch (error) {
    console.error('Failed to get response:', error.message);
    process.exit(1);
  }
}

main();
