/**
 * Page Utilities - Common page operations
 */

import fs from 'fs';

/**
 * Open a new tab
 * @param {BrowserContext} context - Playwright browser context
 * @param {string} url - Optional URL to navigate to
 * @returns {Promise<Page>}
 */
export async function openTab(context, url = null) {
  const page = await context.newPage();
  
  if (url) {
    await page.goto(url);
  }
  
  return page;
}

/**
 * Close a tab
 * @param {Page} page - Playwright page to close
 * @returns {Promise<void>}
 */
export async function closeTab(page) {
  await page.close();
}

/**
 * Switch to a tab by index
 * @param {BrowserContext} context - Playwright browser context
 * @param {number} index - Tab index (0-based)
 * @returns {Promise<Page|null>}
 */
export async function switchTab(context, index) {
  const pages = context.pages();
  
  if (index >= 0 && index < pages.length) {
    return pages[index];
  }
  
  return null;
}

/**
 * Get all open tabs
 * @param {BrowserContext} context - Playwright browser context
 * @returns {Promise<Array<Page>>}
 */
export async function getTabs(context) {
  return context.pages();
}

/**
 * Take a screenshot
 * @param {Page} page - Playwright page
 * @param {string} filename - Filename to save (optional, returns buffer if not provided)
 * @param {Object} options - Screenshot options
 * @returns {Promise<Buffer|string>}
 */
export async function screenshot(page, filename = null, options = {}) {
  const screenshotOptions = {
    type: options.type || 'png',
    fullPage: options.fullPage || false,
    ...(options.clip && { clip: options.clip })
  };
  
  const buffer = await page.screenshot(screenshotOptions);
  
  if (filename) {
    fs.writeFileSync(filename, buffer);
    console.log(`Screenshot saved: ${filename}`);
    return filename;
  }
  
  return buffer;
}

/**
 * Fill a form with data
 * @param {Page} page - Playwright page
 * @param {Object} formData - Object with field selectors and values
 * @returns {Promise<void>}
 */
export async function fillForm(page, formData) {
  for (const [selector, value] of Object.entries(formData)) {
    try {
      const element = await page.$(selector);
      
      if (!element) {
        console.warn(`Element not found: ${selector}`);
        continue;
      }
      
      const tagName = await element.evaluate(el => el.tagName);
      
      if (tagName === 'INPUT') {
        const type = await element.getAttribute('type');
        
        if (type === 'checkbox' || type === 'radio') {
          const isChecked = await element.isChecked();
          if ((value === true && !isChecked) || (value === false && isChecked)) {
            await element.click();
          }
        } else {
          await element.fill(value);
        }
      } else if (tagName === 'SELECT') {
        await element.selectOption(value);
      } else if (tagName === 'TEXTAREA') {
        await element.fill(value);
      } else {
        await element.fill(value);
      }
      
      console.log(`Filled: ${selector} = ${value}`);
    } catch (e) {
      console.error(`Error filling ${selector}:`, e.message);
    }
  }
}

/**
 * Click an element
 * @param {Page} page - Playwright page
 * @param {string} selector - Element selector
 * @param {Object} options - Click options
 * @returns {Promise<boolean>}
 */
export async function clickElement(page, selector, options = {}) {
  try {
    const element = await page.waitForSelector(selector, { 
      timeout: options.timeout || 5000 
    });
    
    if (!element) {
      console.warn(`Element not found: ${selector}`);
      return false;
    }
    
    await element.click({
      button: options.button || 'left',
      clickCount: options.clickCount || 1,
      delay: options.delay || 0
    });
    
    console.log(`Clicked: ${selector}`);
    return true;
  } catch (e) {
    console.error(`Error clicking ${selector}:`, e.message);
    return false;
  }
}

/**
 * Get page content
 * @param {Page} page - Playwright page
 * @param {string} format - Format: 'html', 'text', or 'json'
 * @returns {Promise<string>}
 */
export async function getPageContent(page, format = 'html') {
  if (format === 'html') {
    return page.content();
  }
  
  if (format === 'text') {
    return page.evaluate(() => document.body.innerText);
  }
  
  if (format === 'json') {
    return page.evaluate(() => {
      const data = {};
      const elements = document.querySelectorAll('[data-testid], [data-id], [id], [class]');
      elements.forEach((el, i) => {
        const id = el.getAttribute('data-testid') || el.getAttribute('data-id') || el.id || el.className || `element-${i}`;
        data[id] = {
          tag: el.tagName,
          text: el.innerText?.substring(0, 100),
          attributes: {}
        };
        
        // Get some attributes
        if (el.href) data[id].attributes.href = el.href;
        if (el.src) data[id].attributes.src = el.src;
      });
      return data;
    });
  }
  
  return page.content();
}

/**
 * Execute JavaScript on the page
 * @param {Page} page - Playwright page
 * @param {Function|string} script - Script to execute
 * @returns {Promise<any>}
 */
export async function executeScript(page, script) {
  if (typeof script === 'string') {
    return page.evaluate(script);
  }
  
  return page.evaluate(script);
}

/**
 * Wait for element
 * @param {Page} page - Playwright page
 * @param {string} selector - Element selector
 * @param {Object} options - Wait options
 * @returns {Promise<ElementHandle|null>}
 */
export async function waitForElement(page, selector, options = {}) {
  try {
    return await page.waitForSelector(selector, {
      timeout: options.timeout || 10000,
      state: options.state || 'visible'
    });
  } catch (e) {
    if (options.silent !== true) {
      console.warn(`Element not found: ${selector}`);
    }
    return null;
  }
}

/**
 * Scroll page
 * @param {Page} page - Playwright page
 * @param {number} scrollX - X position
 * @param {number} scrollY - Y position
 * @returns {Promise<void>}
 */
export async function scrollPage(page, scrollX = 0, scrollY = 500) {
  await page.evaluate(({ scrollX, scrollY }) => {
    window.scrollBy(scrollX, scrollY);
  }, { scrollX, scrollY });
}

/**
 * Get element text
 * @param {Page} page - Playwright page
 * @param {string} selector - Element selector
 * @returns {Promise<string|null>}
 */
export async function getElementText(page, selector) {
  try {
    const element = await page.$(selector);
    if (element) {
      return await element.innerText();
    }
    return null;
  } catch (e) {
    return null;
  }
}

/**
 * Get element attribute
 * @param {Page} page - Playwright page
 * @param {string} selector - Element selector
 * @param {string} attribute - Attribute name
 * @returns {Promise<string|null>}
 */
export async function getElementAttribute(page, selector, attribute) {
  try {
    const element = await page.$(selector);
    if (element) {
      return await element.getAttribute(attribute);
    }
    return null;
  } catch (e) {
    return null;
  }
}
