const puppeteer = require('puppeteer-core');

const EMAIL = 'rainyfay@dollicons.com';
const CDP_URL = 'http://127.0.0.1:18800';

async function registerHuggingFace() {
  console.log('Connecting to browser...');
  
  try {
    const browser = await puppeteer.connect({
      browserWSEndpoint: 'ws://127.0.0.1:18800',
      defaultViewport: null
    });
    
    const page = await browser.newPage();
    console.log('Navigating to HuggingFace signup...');
    
    await page.goto('https://huggingface.co/join', { waitUntil: 'networkidle2' });
    
    console.log('Filling email...');
    await page.type('input[type="email"]', EMAIL);
    
    console.log('Filling password...');
    await page.type('input[type="password"]', 'TempPass!2026Secure');
    
    console.log('Clicking Next...');
    await page.click('button[type="submit"]');
    
    await page.waitForTimeout(5000);
    
    const url = page.url();
    console.log('Current URL:', url);
    
    await browser.disconnect();
    console.log('Done! Check temp email for verification.');
    
  } catch (err) {
    console.error('Error:', err.message);
  }
}

registerHuggingFace();
