/**
 * Browser Tool CAPTCHA Solver
 * Works with OpenClaw's browser tool (not just Playwright)
 */

import { browser } from './browser-tool.mjs';
import { image } from './image-tool.mjs';

/**
 * Solve CAPTCHA using OpenClaw's browser and image tools
 * This version works with the browser tool directly
 */
export class BrowserCaptchaSolver {
  constructor(options = {}) {
    this.options = {
      profile: options.profile || 'openclaw',
      maxRetries: options.maxRetries || 3,
      ...options
    };
    
    this.browser = null;
    this.targetId = null;
  }

  /**
   * Solve CAPTCHA on the current page
   * @param {string} targetId - The browser tab target ID
   */
  async solve(targetId) {
    this.targetId = targetId;
    let lastError = null;
    
    for (let attempt = 1; attempt <= this.options.maxRetries; attempt++) {
      console.log(`🔄 CAPTCHA attempt ${attempt}/${this.options.maxRetries}...`);
      
      try {
        // Wait for and solve CAPTCHA
        const code = await this.solveOnce();
        
        // Check if successful
        const success = await this.checkSuccess();
        
        if (success) {
          console.log(`✅ CAPTCHA solved with code: ${code}`);
          return code;
        } else {
          console.log(`⚠️ Verification failed on attempt ${attempt}`);
          lastError = new Error('Verification failed');
        }
        
      } catch (error) {
        console.log(`⚠️ Attempt ${attempt} error:`, error.message);
        lastError = error;
      }
      
      // Wait before retry
      await new Promise(r => setTimeout(r, 1000));
    }
    
    throw new Error(`Failed after ${this.options.maxRetries} attempts: ${lastError?.message}`);
  }

  /**
   * Solve once
   */
  async solveOnce() {
    // 1. Get page snapshot to find CAPTCHA
    console.log('🔍 Looking for CAPTCHA dialog...');
    const snapshot = await this.getSnapshot();
    
    // 2. Find CAPTCHA image and input refs
    const refs = this.findCaptchaRefs(snapshot);
    
    if (!refs.image) {
      throw new Error('CAPTCHA image not found in snapshot');
    }
    
    console.log('📸 Taking screenshot...');
    const screenshot = await this.takeScreenshot();
    
    // 3. Extract code using AI vision
    console.log('🤖 Analyzing CAPTCHA with AI...');
    const code = await this.extractCode(screenshot);
    console.log(`📝 Extracted code: ${code}`);
    
    // 4. Enter the code
    console.log('⌨️ Entering code...');
    await this.enterCode(refs.input, code);
    
    // 5. Click verify
    console.log('🖱️ Clicking verify...');
    await this.clickVerify(refs.button);
    
    // Wait for processing
    await new Promise(r => setTimeout(r, 1500));
    
    return code;
  }

  /**
   * Get page snapshot
   */
  async getSnapshot() {
    const result = await browser({
      action: 'snapshot',
      profile: this.options.profile,
      targetId: this.targetId
    });
    
    return result;
  }

  /**
   * Take screenshot
   */
  async takeScreenshot() {
    const result = await browser({
      action: 'screenshot',
      profile: this.options.profile,
      targetId: this.targetId
    });
    
    return result;
  }

  /**
   * Find CAPTCHA-related element refs from snapshot
   */
  function findCaptchaRefs(snapshot) {
    const refs = {
      dialog: null,
      image: null,
      input: null,
      button: null
    };
    
    // Parse snapshot to find elements
    // Look for dialog with verifizieren button
    const lines = snapshot.split('\n');
    
    for (const line of lines) {
      // Find input field (textbox)
      if (line.includes('textbox') && !refs.input) {
        const match = line.match(/\[ref=([^\]]+)\]/);
        if (match) refs.input = match[1];
      }
      
      // Find verify button
      if (line.includes('verifizieren') && line.includes('button')) {
        const match = line.match(/\[ref=([^\]]+)\]/);
        if (match) refs.button = match[1];
      }
      
      // Find CAPTCHA image
      if (line.includes('img') && !refs.image) {
        // Check if it's in a dialog
        const dialogIdx = snapshot.indexOf('dialog');
        const imgIdx = snapshot.indexOf('img');
        
        if (dialogIdx !== -1 && imgIdx > dialogIdx && imgIdx < dialogIdx + 500) {
          const match = line.match(/\[ref=([^\]]+)\]/);
          if (match) refs.image = match[1];
        }
      }
    }
    
    console.log('📋 Found refs:', refs);
    return refs;
  }

  /**
   * Extract code from screenshot using AI vision
   */
  async extractCode(screenshotResult) {
    // The screenshot result contains the file path
    const imagePath = screenshotResult;
    
    // Use the image tool to analyze
    const result = await image({
      image: imagePath,
      prompt: 'What numbers do you see in this CAPTCHA image? Return ONLY the digits, nothing else.'
    });
    
    // Clean up the result - extract just digits
    const digits = result.replace(/\D/g, '');
    
    if (digits.length < 4) {
      throw new Error(`Invalid code extracted: "${result}"`);
    }
    
    return digits.substring(0, 6); // Take first 6 digits
  }

  /**
   * Enter code into input field
   */
  async enterCode(inputRef, code) {
    if (!inputRef) {
      throw new Error('Input ref not found');
    }
    
    await browser({
      action: 'act',
      profile: this.options.profile,
      targetId: this.targetId,
      request: {
        kind: 'type',
        ref: inputRef,
        text: code
      }
    });
  }

  /**
   * Click verify button
   */
  async clickVerify(buttonRef) {
    if (!buttonRef) {
      // Try pressing Enter as fallback
      await browser({
        action: 'act',
        profile: this.options.profile,
        targetId: this.targetId,
        request: {
          kind: 'press',
          key: 'Enter'
        }
      });
      return;
    }
    
    await browser({
      action: 'act',
      profile: this.options.profile,
      targetId: this.targetId,
      request: {
        kind: 'click',
        ref: buttonRef
      }
    });
  }

  /**
   * Check if CAPTCHA was solved
   */
  async checkSuccess() {
    const snapshot = await this.getSnapshot();
    
    // Check if dialog is still visible
    if (snapshot.includes('dialog') && snapshot.includes('verifizieren')) {
      // Check for error message
      if (snapshot.includes('Invalid') || snapshot.includes('Falsch')) {
        return false;
      }
      // Still showing - might need more time
      await new Promise(r => setTimeout(r, 1000));
    }
    
    return true;
  }
}

/**
 * Quick solve function - for use with browser tool
 */
export async function solveCaptcha(targetId, options = {}) {
  const solver = new BrowserCaptchaSolver(options);
  return await solver.solve(targetId);
}

export default {
  BrowserCaptchaSolver,
  solveCaptcha
};
