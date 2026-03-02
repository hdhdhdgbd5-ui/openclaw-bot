const puppeteer = require('puppeteer-core');

const TEMP_EMAIL = 'oapalmxzcsp6@dollicons.com';
const EXECUTABLE_PATH = 'C:\\Users\\armoo\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe';

async function signupWithEmail() {
    const browser = await puppeteer.launch({
        executablePath: EXECUTABLE_PATH,
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const page = await browser.newPage();
    await page.goto('https://console.groq.com/login', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 2000));
    
    // Click 'Continue with email'
    const emailBtn = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button, [role=button]'));
        return buttons.find(b => b.textContent?.includes('email'));
    });
    
    if (emailBtn) {
        console.log('Found email button, clicking...');
        await emailBtn.click();
        await new Promise(r => setTimeout(r, 3000));
    }
    
    console.log('URL after click:', page.url());
    
    // Check for email input
    const emailInput = await page.$('input[type="email"], input[name="email"]');
    if (emailInput) {
        console.log('Found email input!');
        await emailInput.type(TEMP_EMAIL, { delay: 50 });
        await new Promise(r => setTimeout(r, 1000));
        
        // Find and click continue/submit
        const submitBtn = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.find(b => b.textContent?.toLowerCase().includes('continue') || b.textContent?.toLowerCase().includes('submit'));
        });
        
        if (submitBtn) {
            console.log('Found submit button, clicking...');
            await submitBtn.click();
            await new Promise(r => setTimeout(r, 5000));
        }
    }
    
    console.log('Final URL:', page.url());
    console.log('Page title:', await page.title());
    
    await browser.close();
    console.log('Done');
}

signupWithEmail().catch(e => console.error('Error:', e.message));
