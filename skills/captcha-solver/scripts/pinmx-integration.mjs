/**
 * pinmx-captcha Integration
 * Example: How to use captcha-solver with pinmx-automation
 */

import { CaptchaSolver } from '../captcha-solver/scripts/captcha-solver.mjs';

/**
 * Enhanced solveCaptcha method for pinmx-automation
 * Replace the existing solveCaptcha() method in index.mjs with this
 */
export async function solveCaptchaWithSolver(page) {
  console.log('🔄 Using captcha-solver to solve numeric CAPTCHA...');
  
  // Check if it's a numeric CAPTCHA (pinmx style)
  const content = await page.content();
  
  if (content.includes('verifizieren') || content.includes('Bestätigungscode')) {
    // This is a numeric CAPTCHA - use the solver
    const solver = new CaptchaSolver({ 
      page: page,
      maxRetries: 3,
      timeout: 30000
    });
    
    try {
      const code = await solver.solve();
      console.log(`✅ Numeric CAPTCHA solved with code: ${code}`);
      return true;
    } catch (error) {
      console.error('❌ CAPTCHA solving failed:', error.message);
      return false;
    }
  }
  
  // Fall back to original CAPTCHA detection for other types
  console.log('⚠️ Not a numeric CAPTCHA - using original handler');
  return false;
}

/**
 * Full integration - patch the PinmxAutomation class
 */
export function patchPinmxAutomation(PinmxAutomationClass) {
  // Store original method
  const originalSolveCaptcha = PinmxAutomationClass.prototype.solveCaptcha;
  
  // Replace with enhanced version
  PinmxAutomationClass.prototype.solveCaptcha = async function() {
    console.log('🔄 Checking for CAPTCHA...');
    
    // Check for numeric CAPTCHA first
    const content = await this.page.content();
    
    if (content.includes('verifizieren') || content.includes('Bestätigungscode')) {
      console.log('📷 Detected numeric CAPTCHA - using captcha-solver...');
      
      const solver = new CaptchaSolver({ 
        page: this.page,
        maxRetries: 3
      });
      
      try {
        const code = await solver.solve();
        console.log(`✅ Solved numeric CAPTCHA: ${code}`);
        
        // Wait a moment for the verification to process
        await this.page.waitForTimeout(2000);
        
        return true;
      } catch (error) {
        console.error('❌ CAPTCHA solving error:', error.message);
        // Fall through to original handler
      }
    }
    
    // Fall back to original handler for other CAPTCHA types
    if (originalSolveCaptcha) {
      return await originalSolveCaptcha.call(this);
    }
    
    return false;
  };
  
  console.log('✅ PinmxAutomation patched with captcha-solver');
}

/**
 * Quick test - solve a single CAPTCHA
 */
export async function testSolveCaptcha(page) {
  const solver = new CaptchaSolver({ page });
  
  // Wait for CAPTCHA to appear
  await solver.waitForCaptcha();
  
  // Solve it
  const code = await solver.solve();
  
  return code;
}

export default {
  solveCaptchaWithSolver,
  patchPinmxAutomation,
  testSolveCaptcha
};
