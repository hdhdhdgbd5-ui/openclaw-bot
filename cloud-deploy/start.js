#!/usr/bin/env node
/**
 * OpenClaw Cloud Startup Script
 * Run this on your cloud server to start the bot 24/7
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Starting OpenClaw Cloud Deployment...');

// Check if running on cloud (Hugging Face, Oracle, etc.)
const isCloud = process.env.HF_SPACE_ID || process.env.OCI_INSTANCE || false;

if (isCloud) {
  console.log('☁️  Detected cloud environment');
}

// Start OpenClaw gateway
console.log('🔧 Starting OpenClaw gateway...');
exec('openclaw gateway start', (error, stdout, stderr) => {
  if (error) {
    console.error(`❌ Error starting gateway: ${error.message}`);
    process.exit(1);
  }
  
  console.log('✅ Gateway started!');
  console.log(stdout);
  
  // Keep process alive
  console.log('🟢 Bot is now running 24/7!');
  console.log('Telegram bot is active and listening...');
});

// Keep the script running
process.stdin.resume();

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down gracefully...');
  exec('openclaw gateway stop', () => {
    process.exit(0);
  });
});
