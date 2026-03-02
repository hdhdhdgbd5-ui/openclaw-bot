const { chromium } = require('playwright');

(async () => {
  console.log('Starting browser...');
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('https://console.groq.com/keys');
  await page.waitForTimeout(8000);
  
  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  
  await page.screenshot({ path: 'C:/Users/armoo/.openclaw/workspace/auto_groq.png' });
  console.log('Screenshot saved!');
  
  await browser.close();
  console.log('Done!');
})();
