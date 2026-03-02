/**
 * Image Analyzer for CAPTCHA solving
 * Uses AI vision to extract numbers from CAPTCHA images
 */

import { readFileSync } from 'fs';

/**
 * Analyze a CAPTCHA image and extract the numeric code
 * @param {string} imagePathOrUrl - Path to image file or data URL
 * @returns {Promise<string>} - The extracted numeric code
 */
export async function analyzeCaptcha(imagePathOrUrl) {
  // Import the image tool from OpenClaw
  // The image tool uses the configured AI vision model
  
  let imageInput;
  
  // Check if it's a data URL (base64)
  if (imagePathOrUrl.startsWith('data:')) {
    // Convert data URL to temp file or use directly
    imageInput = imagePathOrUrl;
  } else {
    // It's a file path - read and convert to data URL
    const fs = await import('fs');
    const path = await import('path');
    
    const ext = path.extname(imagePathOrUrl).toLowerCase();
    let mimeType = 'image/png';
    
    if (ext === '.jpg' || ext === '.jpeg') mimeType = 'image/jpeg';
    else if (ext === '.gif') mimeType = 'image/gif';
    else if (ext === '.webp') mimeType = 'image/webp';
    
    const buffer = fs.readFileSync(imagePathOrUrl);
    const base64 = buffer.toString('base64');
    imageInput = `data:${mimeType};base64,${base64}`;
  }
  
  // Call the image analysis tool
  // This uses the configured AI vision (default: Claude)
  const result = await analyzeWithAI(imageInput);
  
  return result;
}

/**
 * Use AI to analyze the CAPTCHA image
 */
async function analyzeWithAI(imageData) {
  // We'll use the built-in vision capability
  // The image parameter can be a data URL or file path
  
  try {
    // Use the 'image' tool from OpenClaw
    // But we need to call it through the proper channel
    
    // For now, we'll create a simple approach using fetch to an AI API
    // In a real implementation, this would use the configured AI vision
    
    // Try using local OCR approach first
    const numbers = await tryOCR(imageData);
    if (numbers) return numbers;
    
    // Fallback: Use a simple pattern recognition
    // This is a simplified approach - in production, you'd use proper OCR
    
    throw new Error('AI vision not available - need to use browser-based extraction');
    
  } catch (error) {
    console.error('Image analysis error:', error.message);
    throw error;
  }
}

/**
 * Try OCR-based extraction using canvas
 * This is a browser-based approach that can work with Playwright
 */
async function tryOCR(imageData) {
  // This would require additional setup
  // For now, return null to trigger fallback
  return null;
}

/**
 * Alternative: Use pixel analysis for simple numeric CAPTCHAs
 * Analyzes the image pixel data to extract numbers
 */
export async function analyzeCaptchaSimple(imagePath) {
  // This is a placeholder for pixel-based analysis
  // Would require canvas and pixel manipulation
  
  // For simple numeric CAPTCHAs with clear digits, we can:
  // 1. Load image
  // 2. Find digit regions
  // 3. Match against digit templates
  
  // This requires additional npm packages like 'canvas'
  // For this skill, we'll rely on AI vision
  
  throw new Error('Simple OCR not implemented - use AI vision');
}

// Re-export for compatibility
export default {
  analyzeCaptcha,
  analyzeCaptchaSimple
};
