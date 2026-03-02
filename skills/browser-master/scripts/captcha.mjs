/**
 * CAPTCHA Solver Module
 * 
 * Handles various CAPTCHA types with AI-powered solving
 */

import fetch from 'node-fetch';
import FormData from 'form-data';

/**
 * Solve reCAPTCHA using 2Captcha API
 */
export async function solveRecaptcha2Captcha(siteKey, pageUrl, apiKey) {
  try {
    // Submit captcha
    const submitUrl = `http://2captcha.com/in.php?key=${apiKey}&method=userrecaptcha&googlekey=${siteKey}&pageurl=${encodeURIComponent(pageUrl)}`;
    
    const submitResponse = await fetch(submitUrl);
    const submitText = await submitResponse.text();
    
    if (!submitText.startsWith('OK|')) {
      throw new Error(`Failed to submit: ${submitText}`);
    }
    
    const captchaId = submitText.split('|')[1];
    
    // Poll for result
    for (let i = 0; i < 60; i++) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const resultUrl = `http://2captcha.com/res.php?key=${apiKey}&action=get&id=${captchaId}`;
      const resultResponse = await fetch(resultUrl);
      const resultText = await resultResponse.text();
      
      if (resultText.startsWith('OK|')) {
        return resultText.split('|')[1];
      }
      
      if (resultText !== 'CAPCHA_NOT_READY') {
        throw new Error(`Error: ${resultText}`);
      }
    }
    
    throw new Error('Timeout waiting for CAPTCHA');
  } catch (e) {
    console.error('2Captcha error:', e.message);
    return null;
  }
}

/**
 * Solve hCaptcha using 2Captcha API
 */
export async function solveHCaptcha2Captcha(siteKey, pageUrl, apiKey) {
  try {
    const submitUrl = `http://2captcha.com/in.php?key=${apiKey}&method=hcaptcha&sitekey=${siteKey}&pageurl=${encodeURIComponent(pageUrl)}`;
    
    const submitResponse = await fetch(submitUrl);
    const submitText = await submitResponse.text();
    
    if (!submitText.startsWith('OK|')) {
      throw new Error(`Failed to submit: ${submitText}`);
    }
    
    const captchaId = submitText.split('|')[1];
    
    for (let i = 0; i < 60; i++) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const resultUrl = `http://2captcha.com/res.php?key=${apiKey}&action=get&id=${captchaId}`;
      const resultResponse = await fetch(resultUrl);
      const resultText = await resultResponse.text();
      
      if (resultText.startsWith('OK|')) {
        return resultText.split('|')[1];
      }
    }
    
    throw new Error('Timeout waiting for hCaptcha');
  } catch (e) {
    console.error('hCaptcha error:', e.message);
    return null;
  }
}

/**
 * Solve image CAPTCHA using 2Captcha API
 */
export async function solveImageCaptcha2Captcha(imageUrl, apiKey) {
  try {
    const form = new FormData();
    form.append('key', apiKey);
    form.append('method', 'post');
    form.append('url', imageUrl);
    
    const submitResponse = await fetch('http://2captcha.com/in.php', {
      method: 'POST',
      body: form
    });
    
    const submitText = await submitResponse.text();
    
    if (!submitText.startsWith('OK|')) {
      throw new Error(`Failed to submit: ${submitText}`);
    }
    
    const captchaId = submitText.split('|')[1];
    
    for (let i = 0; i < 60; i++) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const resultUrl = `http://2captcha.com/res.php?key=${apiKey}&action=get&id=${captchaId}`;
      const resultResponse = await fetch(resultUrl);
      const resultText = await resultResponse.text();
      
      if (resultText.startsWith('OK|')) {
        return resultText.split('|')[1];
      }
    }
    
    throw new Error('Timeout waiting for image CAPTCHA');
  } catch (e) {
    console.error('Image CAPTCHA error:', e.message);
    return null;
  }
}

/**
 * Anti-Captcha API solver
 */
export async function solveWithAntiCaptcha(siteKey, pageUrl, apiKey, type = 'RecaptchaV2') {
  try {
    // Submit
    const submitResponse = await fetch('https://api.anti-captcha.com/createTask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clientKey: apiKey,
        task: {
          type,
          websiteURL: pageUrl,
          websiteKey: siteKey
        }
      })
    });
    
    const submitData = await submitResponse.json();
    
    if (!submitData.taskId) {
      throw new Error(`Failed to create task: ${JSON.stringify(submitData)}`);
    }
    
    // Poll for result
    for (let i = 0; i < 60; i++) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const resultResponse = await fetch('https://api.anti-captcha.com/getTaskResult', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clientKey: apiKey,
          taskId: submitData.taskId
        })
      });
      
      const resultData = await resultResponse.json();
      
      if (resultData.status === 'ready') {
        return resultData.solution.gRecaptchaResponse;
      }
      
      if (resultData.status === 'failed') {
        throw new Error('CAPTCHA solving failed');
      }
    }
    
    throw new Error('Timeout waiting for CAPTCHA');
  } catch (e) {
    console.error('Anti-Captcha error:', e.message);
    return null;
  }
}

/**
 * CapMonster API solver
 */
export async function solveWithCapMonster(siteKey, pageUrl, apiKey, type = 'RecaptchaV2Task') {
  try {
    const submitResponse = await fetch('https://api.capmonster.cloud/createTask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clientKey: apiKey,
        task: {
          type,
          websiteURL: pageUrl,
          websiteKey: siteKey
        }
      })
    });
    
    const submitData = await submitResponse.json();
    
    if (!submitData.taskId) {
      throw new Error(`Failed to create task: ${JSON.stringify(submitData)}`);
    }
    
    for (let i = 0; i < 60; i++) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      const resultResponse = await fetch('https://api.capmonster.cloud/getTaskResult', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clientKey: apiKey,
          taskId: submitData.taskId
        })
      });
      
      const resultData = await resultResponse.json();
      
      if (resultData.status === 'ready') {
        return resultData.solution.gRecaptchaResponse;
      }
    }
    
    throw new Error('Timeout waiting for CAPTCHA');
  } catch (e) {
    console.error('CapMonster error:', e.message);
    return null;
  }
}

/**
 * Solve text/image CAPTCHA locally (basic implementation)
 * For more complex CAPTCHAs, use external services above
 */
export async function solveTextCaptchaLocally(imageBase64) {
  // This is a placeholder - in production, integrate with OCR service
  // like Tesseract, Google Cloud Vision, or AWS Textract
  console.log('Local CAPTCHA solving not implemented - use external service');
  return null;
}

/**
 * Auto-detect and solve any CAPTCHA
 */
export class CaptchaSolver {
  constructor(options = {}) {
    this.apiKey = options.apiKey || process.env.TWOCAPTCHA_API_KEY;
    this.service = options.service || '2captcha'; // 2captcha, anticaptcha, capmonster
  }

  async solve(page) {
    const url = page.url();
    const captcha = await page.evaluate(() => {
      // Check reCAPTCHA
      const recaptcha = document.querySelector('.g-recaptcha, [data-sitekey]');
      if (recaptcha) {
        return {
          type: 'recaptcha',
          siteKey: recaptcha.dataset?.sitekey || recaptcha.getAttribute('data-sitekey')
        };
      }

      // Check hCaptcha
      const hcaptcha = document.querySelector('.h-captcha, [data-hcaptcha-sitekey]');
      if (hcaptcha) {
        return {
          type: 'hcaptcha',
          siteKey: hcaptcha.dataset?.hcaptchaSitekey
        };
      }

      return null;
    });

    if (!captcha) return null;

    console.log(`Detected ${captcha.type}, solving...`);

    switch (this.service) {
      case '2captcha':
        if (captcha.type === 'recaptcha') {
          return await solveRecaptcha2Captcha(captcha.siteKey, url, this.apiKey);
        } else if (captcha.type === 'hcaptcha') {
          return await solveHCaptcha2Captcha(captcha.siteKey, url, this.apiKey);
        }
        break;

      case 'anticaptcha':
        return await solveWithAntiCaptcha(
          captcha.siteKey, 
          url, 
          this.apiKey,
          captcha.type === 'recaptcha' ? 'RecaptchaV2' : 'HCaptchaTask'
        );

      case 'capmonster':
        return await solveWithCapMonster(
          captcha.siteKey,
          url,
          this.apiKey,
          captcha.type === 'recaptcha' ? 'RecaptchaV2Task' : 'HCaptchaTask'
        );
    }

    return null;
  }
}

export default {
  solveRecaptcha2Captcha,
  solveHCaptcha2Captcha,
  solveImageCaptcha2Captcha,
  solveWithAntiCaptcha,
  solveWithCapMonster,
  solveTextCaptchaLocally,
  CaptchaSolver
};
