/**
 * Simple CAPTCHA Solver - Agent Workflow Version
 * Designed to be used with OpenClaw's agent tools
 * 
 * This module provides functions that can be called from an agent
 * to solve CAPTCHAs step by step using the browser and image tools
 */

/**
 * Solve numeric CAPTCHA on pinmx.com
 * Call this function from your agent workflow
 * 
 * @param {Object} tools - OpenClaw tools (browser, image)
 * @param {string} targetId - Browser tab target ID
 * @param {string} profile - Browser profile to use
 * @returns {Promise<string>} - The solved CAPTCHA code
 */
export async function solvePinmxCaptcha(tools, targetId, profile = 'openclaw') {
  console.log('🔢 Starting PINMX CAPTCHA solver...');
  
  let lastError = null;
  const maxRetries = 3;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    console.log(`📷 Attempt ${attempt}/${maxRetries}`);
    
    try {
      // Step 1: Get snapshot to find CAPTCHA elements
      console.log('🔍 Looking for CAPTCHA dialog...');
      const snapshot = await tools.browser({
        action: 'snapshot',
        profile,
        targetId
      });
      
      // Step 2: Find the input and button refs
      const refs = findCaptchaRefs(snapshot);
      
      if (!refs.input) {
        throw new Error('CAPTCHA input field not found');
      }
      
      // Step 3: Take screenshot
      console.log('📸 Taking screenshot...');
      const screenshotResult = await tools.browser({
        action: 'screenshot',
        profile,
        targetId
      });
      
      // Step 4: Analyze with AI vision
      console.log('🤖 Analyzing with AI...');
      const imageResult = await tools.image({
        image: screenshotResult,
        prompt: 'Look very carefully at this CAPTCHA image. It shows a 6-digit number made of individual colored digits. Tell me EXACTLY what each digit is, from left to right. List them one by one as a single string of 6 digits, nothing else.'
      });
      
      // Extract digits only
      const code = imageResult.replace(/\D/g, '');
      
      if (code.length < 4) {
        throw new Error(`Could not extract valid code: "${imageResult}"`);
      }
      
      console.log(`📝 Extracted code: ${code}`);
      
      // Step 5: Enter the code
      console.log('⌨️ Entering code...');
      await tools.browser({
        action: 'act',
        profile,
        targetId,
        request: {
          kind: 'type',
          ref: refs.input,
          text: code
        }
      });
      
      // Step 6: Click verify
      if (refs.button) {
        console.log('🖱️ Clicking verify...');
        await tools.browser({
          action: 'act',
          profile,
          targetId,
          request: {
            kind: 'click',
            ref: refs.button
          }
        });
      } else {
        // Press Enter as fallback
        console.log('⌨️ Pressing Enter...');
        await tools.browser({
          action: 'act',
          profile,
          targetId,
          request: {
            kind: 'press',
            key: 'Enter'
          }
        });
      }
      
      // Step 7: Wait and check result
      await new Promise(r => setTimeout(r, 2000));
      
      // Check if CAPTCHA is still there (failed) or gone (success)
      const checkSnapshot = await tools.browser({
        action: 'snapshot',
        profile,
        targetId
      });
      
      if (checkSnapshot.includes('Invalid') || checkSnapshot.includes('Falsch') || checkSnapshot.includes('Ungültig')) {
        console.log(`⚠️ Code ${code} was incorrect, retrying...`);
        lastError = new Error('Invalid CAPTCHA code');
        continue;
      }
      
      if (!checkSnapshot.includes('dialog') || !checkSnapshot.includes('verifizieren')) {
        console.log('✅ CAPTCHA dialog closed - success!');
        return code;
      }
      
      console.log('⚠️ CAPTCHA still showing, retrying...');
      lastError = new Error('CAPTCHA not solved');
      
    } catch (error) {
      console.log(`⚠️ Attempt ${attempt} error:`, error.message);
      lastError = error;
    }
    
    // Wait before retry
    await new Promise(r => setTimeout(r, 1000));
  }
  
  throw new Error(`Failed after ${maxRetries} attempts: ${lastError?.message}`);
}

/**
 * Find CAPTCHA-related element refs from snapshot
 */
function findCaptchaRefs(snapshot) {
  const refs = {
    input: null,
    button: null,
    image: null
  };
  
  // Parse snapshot text to find refs
  // Format: element type [ref=xxx]
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
    
    // Find CAPTCHA image (img in dialog context)
    if (line.includes('img') && !refs.image) {
      // Check if it's in a CAPTCHA dialog context
      const lowerLine = line.toLowerCase();
      if (lowerLine.includes('captcha') || lowerLine.includes('bestätigung')) {
        const match = line.match(/\[ref=([^\]]+)\]/);
        if (match) refs.image = match[1];
      }
    }
  }
  
  // If we found input but not button, look for any button in dialog
  if (refs.input && !refs.button) {
    for (const line of lines) {
      if (line.includes('button') && line.includes('generic')) {
        const match = line.match(/\[ref=([^\]]+)\]/);
        if (match && !refs.button) {
          // Check if this button is after the input (in the same dialog)
          const inputIdx = snapshot.indexOf(`[ref=${refs.input}]`);
          const btnIdx = snapshot.indexOf(`[ref=${match[1]}]`);
          
          if (btnIdx > inputIdx && btnIdx < inputIdx + 300) {
            refs.button = match[1];
          }
        }
      }
    }
  }
  
  console.log('📋 Found refs:', JSON.stringify(refs));
  return refs;
}

/**
 * Detect if a numeric CAPTCHA is present
 */
export async function detectNumericCaptcha(tools, targetId, profile = 'openclaw') {
  const snapshot = await tools.browser({
    action: 'snapshot',
    profile,
    targetId
  });
  
  // Check for verification dialog
  const hasDialog = snapshot.includes('dialog') || snapshot.includes('[role="dialog"]');
  const hasVerify = snapshot.includes('verifizieren') || snapshot.includes('verify');
  const hasCodeInput = snapshot.includes('textbox');
  
  return hasDialog && hasVerify && hasCodeInput;
}

/**
 * Generic CAPTCHA solver that works with the current page
 * Call this from your agent workflow
 */
export async function solveCaptcha(tools, targetId, options = {}) {
  const profile = options.profile || 'openclaw';
  
  // Detect CAPTCHA type
  const isNumeric = await detectNumericCaptcha(tools, targetId, profile);
  
  if (isNumeric) {
    return await solvePinmxCaptcha(tools, targetId, profile);
  }
  
  throw new Error('Unknown CAPTCHA type');
}

export default {
  solveCaptcha,
  solvePinmxCaptcha,
  detectNumericCaptcha
};
