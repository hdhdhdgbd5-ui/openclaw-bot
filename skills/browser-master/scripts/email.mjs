/**
 * Temporary Email Module
 * 
 * Handles temporary email creation and verification
 */

import fetch from 'node-fetch';

/**
 * Get random temp email domain
 */
const tempDomains = [
  'mailinator.com',
  'guerrillamail.com',
  'guerrillamail.net',
  'guerrillamail.org',
  'guerrillamail.biz',
  'sharklasers.com',
  'spam4.me',
  'spamgourmet.com',
  'temp-mail.io',
  'tempmail.com',
  '10minutemail.com',
  'fakeinbox.com',
  'yopmail.com',
  'trashmail.com'
];

/**
 * Generate random email username
 */
function generateUsername(prefix = 'auto') {
  const random = Math.random().toString(36).substring(2, 10);
  return `${prefix}${random}`;
}

/**
 * Create temp email using Mailinator
 */
export async function createMailinatorEmail() {
  const username = generateUsername('browser');
  const email = `${username}@mailinator.com`;
  return { email, username, domain: 'mailinator.com' };
}

/**
 * Create temp email using Guerrilla Mail
 */
export async function createGuerrillaEmail() {
  const response = await fetch('https://api.guerrillamail.com/ajax.php', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'f=get_email_address'
  });
  
  const data = await response.text();
  const match = data.match(/<email>([^<]+)<\/email>/);
  
  if (match) {
    const email = match[1];
    const [username, domain] = email.split('@');
    return { email, username, domain };
  }
  
  throw new Error('Failed to create Guerrilla email');
}

/**
 * Create temp email using Yopmail
 */
export async function createYopmailEmail() {
  const username = generateUsername('browser');
  const email = `${username}@yopmail.com`;
  return { email, username, domain: 'yopmail.com' };
}

/**
 * Create temp email using 10 Minute Mail
 */
export async function create10MinuteEmail() {
  const response = await fetch('https://10minutemail.com/address.api.new');
  const data = await response.json();
  
  return {
    email: data.fullAddress,
    username: data.localPart,
    domain: data.domain,
    expires: Date.now() + 10 * 60 * 1000
  };
}

/**
 * Check Mailinator inbox
 */
export async function checkMailinatorInbox(email) {
  const [username] = email.split('@');
  const response = await fetch(`https://www.mailinator.com/api/v2/inboxes/${username}`);
  const data = await response.json();
  
  return data.messages || [];
}

/**
 * Check Guerrilla Mail inbox
 */
export async function checkGuerrillaInbox(email) {
  const [username] = email.split('@');
  const response = await fetch(
    `https://api.guerrillamail.com/ajax.php?f=get_email_list&offset=0&alias=${username}`
  );
  const data = await response.text();
  
  const messages = [];
  const regex = /<mail><id>(\d+)<\/id><from>([^<]+)<\/from><subject>([^<]*)<\/subject><date>([^<]+)<\/date><\/mail>/g;
  let match;
  
  while ((match = regex.exec(data)) !== null) {
    messages.push({
      id: match[1],
      from: match[2],
      subject: match[3],
      date: match[4]
    });
  }
  
  return messages;
}

/**
 * Get Guerrilla Mail content
 */
export async function getGuerrillaEmailContent(emailId) {
  const response = await fetch(
    `https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id=${emailId}`
  );
  const data = await response.text();
  
  const match = data.match(/<body>([\s\S]*?)<\/body>/);
  return match ? match[1] : '';
}

/**
 * Check Yopmail inbox
 */
export async function checkYopmailInbox(email) {
  const [username] = email.split('@');
  const response = await fetch(
    `https://yopmail.com/inbox?b=1&c=1&r=&s=${username}&v=2`
  );
  const html = await response.text();
  
  const messages = [];
  const regex = /<div class="m"[^>]*data-id="([^"]+)"[^>]*>[\s\S]*?<span class="lf">([^<]+)<\/span>[\s\S]*?<span class="sf">([^<]+)<\/span>/g;
  let match;
  
  while ((match = regex.exec(html)) !== null) {
    messages.push({
      id: match[1],
      from: match[2],
      subject: match[3]
    });
  }
  
  return messages;
}

/**
 * Get Yopmail email content
 */
export async function getYopmailContent(emailId, username) {
  const response = await fetch(
    `https://yopmail.com/inbox/${username}?m=${emailId}`
  );
  const html = await response.text();
  
  // Extract body content
  const match = html.match(/<iframe[^>]*src="([^"]+embed[^"]+)"/);
  if (match) {
    const iframeResponse = await fetch(match[1]);
    const iframeHtml = await iframeResponse.text();
    const bodyMatch = iframeHtml.match(/<body[^>]*>([\s\S]*)<\/body>/);
    return bodyMatch ? bodyMatch[1] : '';
  }
  
  return '';
}

/**
 * Wait for verification email
 */
export async function waitForVerificationEmail(email, options = {}) {
  const {
    timeout = 120000,
    interval = 5000,
    domain = email.split('@')[1]
  } = options;

  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    let messages = [];

    try {
      if (domain === 'mailinator.com') {
        messages = await checkMailinatorInbox(email);
      } else if (domain.includes('guerrilla')) {
        messages = await checkGuerrillaInbox(email);
      } else if (domain === 'yopmail.com') {
        messages = await checkYopmailInbox(email);
      }
    } catch (e) {
      console.log('Error checking inbox:', e.message);
    }

    // Look for verification email
    const verifyEmail = messages.find(m => 
      m.subject.toLowerCase().includes('verify') ||
      m.subject.toLowerCase().includes('confirm') ||
      m.subject.toLowerCase().includes('activation') ||
      m.from.toLowerCase().includes('noreply') ||
      m.from.toLowerCase().includes('no-reply')
    );

    if (verifyEmail) {
      // Get email content
      let content = '';
      if (domain.includes('guerrilla')) {
        content = await getGuerrillaEmailContent(verifyEmail.id);
      }
      
      return {
        found: true,
        message: verifyEmail,
        content
      };
    }

    await new Promise(resolve => setTimeout(resolve, interval));
  }

  return { found: false };
}

/**
 * Extract verification link from email content
 */
export function extractVerificationLink(content) {
  // Match various verification link patterns
  const patterns = [
    /https?:\/\/[^\s"'>]+verify[^\s"'>]+/i,
    /https?:\/\/[^\s"'>]+confirm[^\s"'>]+/i,
    /https?:\/\/[^\s"'>]+activation[^\s"'>]+/i,
    /https?:\/\/[^\s"'>]+\/verify\/[^\s"'>]+/i,
    /https?:\/\/[^\s"'>]+token[^\s"'>]+/i,
    /href=["'](https?:\/\/[^"']+)["']/i
  ];

  for (const pattern of patterns) {
    const match = content.match(pattern);
    if (match) {
      return match[1] || match[0];
    }
  }

  return null;
}

/**
 * Temp email factory
 */
export class TempEmail {
  constructor(options = {}) {
    this.provider = options.provider || 'guerrilla';
    this.email = null;
  }

  async create() {
    switch (this.provider) {
      case 'mailinator':
        this.email = await createMailinatorEmail();
        break;
      case 'guerrilla':
      default:
        this.email = await createGuerrillaEmail();
        break;
      case 'yopmail':
        this.email = await createYopmailEmail();
        break;
      case '10minutemail':
        this.email = await create10MinuteEmail();
        break;
      default:
        this.email = await createGuerrillaEmail();
    }

    return this.email;
  }

  async checkInbox() {
    if (!this.email) {
      throw new Error('No email created');
    }

    const domain = this.email.domain;

    if (domain === 'mailinator.com') {
      return await checkMailinatorInbox(this.email.email);
    } else if (domain.includes('guerrilla')) {
      return await checkGuerrillaInbox(this.email.email);
    } else if (domain === 'yopmail.com') {
      return await checkYopmailInbox(this.email.email);
    }

    return [];
  }

  async waitForVerification(options = {}) {
    return await waitForVerificationEmail(this.email.email, options);
  }

  getEmail() {
    return this.email?.email;
  }
}

export default {
  createMailinatorEmail,
  createGuerrillaEmail,
  createYopmailEmail,
  create10MinuteEmail,
  checkMailinatorInbox,
  checkGuerrillaInbox,
  getGuerrillaEmailContent,
  checkYopmailInbox,
  getYopmailContent,
  waitForVerificationEmail,
  extractVerificationLink,
  TempEmail
};
