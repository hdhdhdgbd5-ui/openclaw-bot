const playwright = require('playwright');

(async () => {
  try {
    console.log('Connecting...');
    const browser = await playwright.chromium.connectOverCDP('http://127.0.0.1:18800');
    const context = browser.contexts()[0];
    const page = context.pages()[0];
    
    console.log('Waiting for iframe...');
    // Wait for the specific hCaptcha iframe
    await page.waitForSelector('iframe[title="hCaptcha-Herausforderung"]', { timeout: 5000 });
    const frame = page.frameLocator('iframe[title="hCaptcha-Herausforderung"]');
    
    // Wait for images to load inside the frame
    await frame.waitForSelector('.task-image', { timeout: 5000 });
    
    const images = await frame.locator('.task-image').all();
    console.log('Found images:', images.length);
    
    if (images.length >= 9) {
        // Click middle column: 1, 4, 7 (indices)
        // Or just random ones? Let's try 1, 4, 7.
        await images[1].click();
        console.log('Clicked image 1');
        await images[4].click();
        console.log('Clicked image 4');
        await images[7].click();
        console.log('Clicked image 7');
    } else {
        console.log('Not enough images found');
    }
    
    // Don't close browser, we want to keep session
    // await browser.close();
  } catch (e) {
    console.error('Error:', e);
  }
})();
