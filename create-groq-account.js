const puppeteer = require('puppeteer-core');
const fs = require('fs');
const path = require('path');

const TEMP_EMAIL = 'oapalmxzcsp6@dollicons.com';
const TEMP_PASSWORD = 'TempPass123!';
const MAIL_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3NzE4ODU4NTQsInJvbGVzIjpbIlJPTEVfVVNFUiJdLCJhZGRyZXNzIjoib2FwYWxteHpjc3A2QGRvbGxpY29ucy5jb20iLCJpZCI6IjY5OWNkNTE5ZmNmZWNhYmZkYzAyN2E1MiIsIm1lcmN1cmUiOnsic3Vic2NyaWJlIjpbIi9hY2NvdW50cy82OTljZDUxOWZjZmVjYWJmZGMwMjdhNTIiXX19.h_zACHHthnkReZ_w-N2YEue0chimiao2etvHFanO22kjBFajhHPfM41N1BDpOxKgmc-C85YOg0MHKR5B9PSlSQ';

const EXECUTABLE_PATH = 'C:\\Users\\armoo\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe';

async function waitForEmail() {
    console.log('Waiting for verification email...');
    let attempts = 0;
    while (attempts < 30) {
        try {
            const response = await fetch('https://api.mail.tm/messages', {
                headers: { 'Authorization': `Bearer ${MAIL_TOKEN}` }
            });
            const data = await response.json();
            if (data['hydra:member'] && data['hydra:member'].length > 0) {
                console.log('Email received!');
                return data['hydra:member'][0];
            }
        } catch (e) {
            console.log('Error checking email:', e.message);
        }
        await new Promise(r => setTimeout(r, 2000));
        attempts++;
    }
    throw new Error('No verification email received');
}

async function getEmailContent(messageId) {
    const response = await fetch(`https://api.mail.tm/messages/${messageId}`, {
        headers: { 'Authorization': `Bearer ${MAIL_TOKEN}` }
    });
    return await response.json();
}

async function createGroqAccount() {
    console.log('Starting browser...');
    const browser = await puppeteer.launch({
        executablePath: EXECUTABLE_PATH,
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-blink-features=AutomationControlled']
    });

    const page = await browser.newPage();
    
    // Go to signup
    console.log('Navigating to Groq signup...');
    await page.goto('https://console.groq.com/login', { waitUntil: 'networkidle2' });
    await new Promise(r => setTimeout(r, 2000));
    
    // Click sign up link if available
    try {
        const signUpLink = await page.$('a[href*="signup"]');
        if (signUpLink) {
            await signUpLink.click();
            await new Promise(r => setTimeout(r, 2000));
        }
    } catch (e) {
        console.log('No signup link found, trying direct URL');
    }
    
    // Check current URL
    console.log('Current URL:', page.url());
    
    // Try to find signup form
    const content = await page.content();
    
    // Look for email input
    const emailInput = await page.$('input[type="email"]');
    if (emailInput) {
        console.log('Found email input, entering temp email...');
        await emailInput.type(TEMP_EMAIL, { delay: 100 });
        await new Promise(r => setTimeout(r, 1000));
        
        // Look for submit button
        const buttons = await page.$$('button');
        for (const btn of buttons) {
            const text = await btn.evaluate(el => el.textContent);
            console.log('Button:', text);
            if (text.toLowerCase().includes('sign up') || text.toLowerCase().includes('continue') || text.toLowerCase().includes('submit')) {
                await btn.click();
                console.log('Clicked submit button');
                break;
            }
        }
        
        await new Promise(r => setTimeout(r, 3000));
        
        // Wait for verification email
        console.log('Waiting for verification email...');
        const email = await waitForEmail();
        console.log('Got email:', email.subject);
        
        // Get email content to find verification link
        const emailContent = await getEmailContent(email.id);
        console.log('Email from:', email.from);
        
        // Note: Full email content would need HTML parsing
    } else {
        console.log('Could not find email input. Page may require different approach.');
    }
    
    await browser.close();
    console.log('Done');
}

createGroqAccount().catch(console.error);
