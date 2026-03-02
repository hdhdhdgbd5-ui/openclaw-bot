#!/usr/bin/env node

/**
 * Puter.js AI Chat Script
 * Uses Puter.js library for free AI chat with Gemini models
 * No API key required!
 * 
 * Usage: node chat.mjs "Your message here"
 *        node chat.mjs "Your message" --model gemini-2.5-flash-lite
 *        node chat.mjs "Your message" --stream
 */

import puppeteer from 'puppeteer-core';

const CDP_PORT = 18800; // OpenClaw browser port
const MAX_RETRIES = 3;
const RETRY_DELAY = 3000;

// Default model
let MODEL = 'gemini-2.5-flash-lite';
let STREAM = false;

// Simple sleep function
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
  
  // Try to find existing Puter page
  let puterTarget = targets.find(t => t.url().includes('puter.ai') || t.url().includes('puter.com'));
  
  if (puterTarget) {
    return await puterTarget.page();
  }
  
  // Try to find any blank page
  let blankTarget = targets.find(t => t.url() === 'about:blank');
  
  if (blankTarget) {
    return await blankTarget.page();
  }
  
  // Create new page
  const page = await browser.newPage();
  return page;
}

async function setupPuterJS(page) {
  console.log('Setting up Puter.js...');
  
  // Navigate to a simple page where we can inject Puter.js
  await page.goto('data:text/html,<html><head><title>Puter.js AI</title></head><body><h1>Loading...</h1><div id="output"></div></body></html>', {
    waitUntil: 'networkidle0'
  });
  
  // Inject Puter.js library
  await page.addScriptTag({ url: 'https://js.puter.com/v2/' });
  
  // Wait for Puter.js to load
  await sleep(2000);
  
  console.log('Puter.js loaded');
}

async function chatWithPuter(page, message, model = MODEL, stream = STREAM) {
  console.log(`Sending message to Puter.ai (model: ${model})...`);
  
  // Create the JavaScript to execute
  const script = `
    (async () => {
      try {
        const options = { model: "${model}" };
        ${stream ? 'options.stream = true;' : ''}
        
        console.log('Calling puter.ai.chat...');
        const response = await puter.ai.chat(\`${message.replace(/`/g, '\\`')}\`, options);
        
        if (${stream}) {
          let fullResponse = '';
          for await (const part of response) {
            console.log('STREAM_PART:', JSON.stringify(part));
            if (part && part.text) {
              fullResponse += part.text;
            }
          }
          return fullResponse;
        }
        
        return response;
      } catch (error) {
        return 'ERROR: ' + error.message;
      }
    })()
  `;
  
  // Execute the script
  const result = await page.evaluate(script);
  
  return result;
}

async function chat(message, options = {}) {
  const model = options.model || MODEL;
  const stream = options.stream || STREAM;
  
  let browser;
  let retries = 0;
  
  while (retries < MAX_RETRIES) {
    try {
      console.log(`Connecting to browser (attempt ${retries + 1}/${MAX_RETRIES})...`);
      browser = await connectToBrowser();
      
      console.log('Finding/creating page...');
      const page = await findPuterPage(browser);
      
      // Set up Puter.js
      await setupPuterJS(page);
      
      // Send chat request
      const response = await chatWithPuter(page, message, model, stream);
      
      await browser.disconnect();
      
      if (response && !response.startsWith('ERROR:')) {
        return response;
      }
      
      throw new Error(response || 'Empty response');
      
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

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    model: MODEL,
    stream: STREAM
  };
  
  const messages = [];
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--model' && i + 1 < args.length) {
      options.model = args[i + 1];
      i++;
    } else if (args[i] === '--stream') {
      options.stream = true;
    } else if (!args[i].startsWith('--')) {
      messages.push(args[i]);
    }
  }
  
  return {
    message: messages.join(' '),
    options
  };
}

// Main execution
async function main() {
  const { message, options } = parseArgs();
  
  if (!message) {
    console.log('Usage: node chat.mjs "Your message here" [--model gemini-2.5-flash-lite] [--stream]');
    console.log('');
    console.log('Options:');
    console.log('  --model <name>   AI model to use (default: gemini-2.5-flash-lite)');
    console.log('  --stream         Enable streaming responses');
    console.log('');
    console.log('Available models:');
    console.log('  - gemini-2.5-flash-lite (default, fast)');
    console.log('  - gemini-2.0-flash');
    console.log('  - gpt-5-nano');
    console.log('');
    console.log('Example: node chat.mjs "Hello AI!" --model gemini-2.5-flash-lite');
    process.exit(1);
  }
  
  console.log(`Message: ${message}`);
  console.log(`Model: ${options.model}`);
  console.log(`Stream: ${options.stream}`);
  console.log('');
  
  try {
    const response = await chat(message, options);
    console.log('\n=== RESPONSE ===');
    console.log(response);
    console.log('================\n');
  } catch (error) {
    console.error('Failed to get response:', error.message);
    process.exit(1);
  }
}

main();
