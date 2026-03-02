/**
 * Numeric CAPTCHA Solver
 * Uses AI vision to solve numeric CAPTCHAs (like pinmx.com)
 */

import fs from 'fs';
import path from 'path';
import os from 'os';

export class CaptchaSolver {
  constructor(options = {}) {
    this.options = {
      maxRetries: 3,
      timeout: 30000,
      retryDelay: 1000,
      verifySelector: 'button:has-text("verifizieren")',
      inputSelector: 'input[type="text"]',
      dialogSelector: 'dialog, [role="dialog"], .modal, [class*="dialog"]',
      ...options
    };
    
    this.page = options.page || null;
    this.tempDir = os.tmpdir();
  }

  /**
   * Main solve function - solves CAPTCHA and returns the code entered
   */
  async solve() {
    if (!this.page) {
      throw new Error('Page object is required. Pass { page: yourPlaywrightPage }');
    }

    let lastError = null;
    
    for (let attempt = 1; attempt <= this.options.maxRetries; attempt++) {
      console.log(`🔄 CAPTCHA solving attempt ${attempt}/${this.options.maxRetries}...`);
      
      try {
        // Wait for CAPTCHA dialog to appear
        await this.waitForCaptcha();
        
        // Solve the CAPTCHA
        const code = await this.solveOnce();
        
        // Check if successful
        const success = await this.checkSuccess();
        
        if (success) {
          console.log(`✅ CAPTCHA solved successfully with code: ${code}`);
          return code;
        } else {
          console.log(`⚠️ CAPTCHA verification failed on attempt ${attempt}`);
          lastError = new Error('CAPTCHA verification failed');
        }
        
      } catch (error) {
        console.log(`⚠️ Attempt ${attempt} failed:`, error.message);
        lastError = error;
      }
      
      // Wait before retry
      if (attempt < this.options.maxRetries) {
        await this.page.waitForTimeout(this.options.retryDelay);
      }
    }
    
    throw new Error(`Failed to solve CAPTCHA after ${this.options.maxRetries} attempts: ${lastError?.message}`);
  }

  /**
   * Wait for CAPTCHA dialog to appear
   */
  async waitForCaptcha() {
    console.log('⏳ Waiting for CAPTCHA dialog...');
    
    // Try multiple selectors to find CAPTCHA dialog
    const selectors = [
      'dialog',
      '[role="dialog"]', 
      '[class*="dialog"]',
      '[class*="captcha"]',
      'textbox[active]',
      'button:has-text("verifizieren")'
    ];
    
    for (const selector of selectors) {
      try {
        const element = await this.page.locator(selector).first();
        if (await element.isVisible()) {
          console.log('✅ CAPTCHA dialog detected');
          return true;
        }
      } catch (e) {
        // Element not found, try next selector
      }
    }
    
    // If no dialog found, wait a bit and check again
    await this.page.waitForTimeout(1000);
    
    // Final check - look for any dialog
    const dialog = await this.page.locator('dialog, [role="dialog"]').first();
    if (await dialog.isVisible()) {
      console.log('✅ CAPTCHA dialog detected');
      return true;
    }
    
    throw new Error('CAPTCHA dialog not found');
  }

  /**
   * Solve the CAPTCHA once (single attempt)
   */
  async solveOnce() {
    // 1. Screenshot the page with CAPTCHA
    console.log('📸 Taking screenshot of CAPTCHA...');
    const screenshotPath = await this.takeScreenshot();
    
    // 2. Extract numbers from image using AI
    console.log('🔍 Analyzing CAPTCHA image with AI...');
    const code = await this.extractCodeFromImage(screenshotPath);
    
    if (!code || !/^\d{4,6}$/.test(code)) {
      throw new Error(`Invalid CAPTCHA code extracted: "${code}"`);
    }
    
    console.log(`📝 Extracted code: ${code}`);
    
    // 3. Enter the code into the input field
    console.log('⌨️ Entering CAPTCHA code...');
    await this.enterCode(code);
    
    // 4. Click verify button
    console.log('🖱️ Clicking verify button...');
    await this.clickVerify();
    
    // Wait a bit for verification
    await this.page.waitForTimeout(1500);
    
    return code;
  }

  /**
   * Take screenshot of the current page
   */
  async takeScreenshot() {
    const timestamp = Date.now();
    const filename = `captcha_${timestamp}.png`;
    const filepath = path.join(this.tempDir, filename);
    
    await this.page.screenshot({ 
      path: filepath,
      fullPage: false
    });
    
    console.log(`📸 Screenshot saved to: ${filepath}`);
    return filepath;
  }

  /**
   * Extract numeric code from CAPTCHA image using AI vision
   */
  async extractCodeFromImage(imagePath) {
    // Read the image file
    const imageBuffer = fs.readFileSync(imagePath);
    const base64 = imageBuffer.toString('base64');
    const dataUrl = `data:image/png;base64,${base64}`;
    
    // Use the image analysis tool (configured AI vision)
    // This will use the default image model to analyze the CAPTCHA
    const { default: image } = await import('./image-analyzer.mjs');
    
    const result = await image.analyzeCaptcha(dataUrl);
    return result;
  }

  /**
   * Enter the code into the input field
   */
  async enterCode(code) {
    // Try multiple selectors for the input field
    const selectors = [
      'input[type="text"]',
      'input[placeholder=""]',
      'textbox[active]',
      'input:not([type])',
      '[class*="captcha"] input',
      'dialog input'
    ];
    
    for (const selector of selectors) {
      try {
        const input = await this.page.locator(selector).first();
        if (await input.isVisible()) {
          // Clear and enter the code
          await input.fill('');
          await input.type(code, { delay: 100 });
          console.log(`✅ Entered code: ${code}`);
          return true;
        }
      } catch (e) {
        // Try next selector
      }
    }
    
    // Fallback: try to find any visible text input in the dialog
    const allInputs = await this.page.locator('dialog input, [role="dialog"] input').all();
    for (const input of allInputs) {
      if (await input.isVisible()) {
        await input.fill('');
        await input.type(code, { delay: 100 });
        console.log(`✅ Entered code (fallback): ${code}`);
        return true;
      }
    }
    
    throw new Error('Could not find CAPTCHA input field');
  }

  /**
   * Click the verify button
   */
  async clickVerify() {
    const selectors = [
      'button:has-text("verifizieren")',
      'button:has-text("verify")',
      '[class*="verify"]',
      'button[type="submit"]'
    ];
    
    for (const selector of selectors) {
      try {
        const button = await this.page.locator(selector).first();
        if (await button.isVisible()) {
          await button.click();
          console.log('✅ Clicked verify button');
          return true;
        }
      } catch (e) {
        // Try next selector
      }
    }
    
    // Press Enter as fallback
    await this.page.keyboard.press('Enter');
    console.log('✅ Pressed Enter to verify');
    return true;
  }

  /**
   * Check if CAPTCHA was solved successfully
   */
  async checkSuccess() {
    // Check if the dialog is still visible
    try {
      const dialogSelectors = [
        'dialog',
        '[role="dialog"]',
        '[class*="dialog"]',
        'textbox[active]'
      ];
      
      for (const selector of dialogSelectors) {
        const element = await this.page.locator(selector).first();
        if (await element.isVisible()) {
          // Check if there's an error message
          const pageContent = await this.page.content();
          if (pageContent.includes('Invalid') || pageContent.includes('Falsch') || pageContent.includes('error')) {
            return false;
          }
          // Dialog still visible - might need more time
          await this.page.waitForTimeout(1000);
        }
      }
      
      // If no dialog visible, likely success
      return true;
      
    } catch (e) {
      // If we can't find dialog, assume success
      return true;
    }
  }

  /**
   * Detect if CAPTCHA is present on the page
   */
  async detectCaptcha() {
    const selectors = [
      'dialog',
      '[role="dialog"]',
      '[class*="dialog"]',
      '[class*="captcha"]',
      'button:has-text("verifizieren")'
    ];
    
    for (const selector of selectors) {
      try {
        const element = await this.page.locator(selector).first();
        if (await element.isVisible()) {
          const text = await element.textContent();
          if (text && (text.includes('verifizieren') || text.includes('Bestätigung') || text.includes('captcha'))) {
            return true;
          }
        }
      } catch (e) {
        // Not found
      }
    }
    
    return false;
  }
}

/**
 * Standalone function to solve CAPTCHA on a page
 */
export async function solveCaptcha(page, options = {}) {
  const solver = new CaptchaSolver({ page, ...options });
  return await solver.solve();
}

/**
 * Detect and return CAPTCHA type
 */
export async function detectCaptchaType(page) {
  const content = await page.content();
  
  if (content.includes('verifizieren') || content.includes('Bestätigungscode')) {
    return 'numeric'; // pinmx style
  }
  
  if (content.includes('recaptcha') || content.includes('g-recaptcha')) {
    return 'recaptcha';
  }
  
  if (content.includes('hcaptcha')) {
    return 'hcaptcha';
  }
  
  return 'unknown';
}
