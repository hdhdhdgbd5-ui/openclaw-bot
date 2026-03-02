#!/usr/bin/env node

/**
 * Simple HTTP server to serve Puter.js test page
 * Usage: node server.mjs
 * Then open http://localhost:3456 in browser
 */

import http from 'http';
import fs from 'fs';
import path from 'path';

const PORT = 3456;

const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Puter.js AI Chat Test</title>
  <script src="https://js.puter.com/v2/"></script>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #1a1a2e; color: #eee; }
    h1 { color: #00d4ff; }
    .controls { margin: 20px 0; }
    input, select, button { padding: 10px; margin: 5px; border-radius: 5px; border: none; font-size: 16px; }
    input { width: 300px; background: #16213e; color: #fff; border: 1px solid #0f3460; }
    select { background: #16213e; color: #fff; border: 1px solid #0f3460; }
    button { background: #00d4ff; color: #1a1a2e; cursor: pointer; font-weight: bold; }
    button:hover { background: #00a8cc; }
    #response { margin-top: 20px; padding: 20px; background: #16213e; border-radius: 10px; min-height: 100px; white-space: pre-wrap; font-family: monospace; }
    .loading { color: #ffd700; }
    .success { color: #00ff88; }
    .error { color: #ff4444; }
    #log { margin-top: 20px; padding: 10px; background: #0f0f1a; border-radius: 5px; font-size: 12px; font-family: monospace; max-height: 200px; overflow-y: auto; }
  </style>
</head>
<body>
  <h1>🚀 Puter.js AI Chat</h1>
  <p>Free AI Chat with Gemini Models - No API Key Required!</p>
  
  <div class="controls">
    <input type="text" id="prompt" placeholder="Enter your message..." value="Hello! What is JavaScript?">
    <select id="model">
      <option value="gemini-2.5-flash-lite">gemini-2.5-flash-lite (Fast)</option>
      <option value="gemini-2.0-flash">gemini-2.0-flash</option>
      <option value="gpt-5-nano">gpt-5-nano</option>
    </select>
    <button onclick="sendChat()">Send</button>
    <button onclick="clearResponse()">Clear</button>
  </div>
  
  <div>
    <label><input type="checkbox" id="stream"> Enable Streaming</label>
  </div>
  
  <h3>Response:</h3>
  <div id="response">Ready to chat...</div>
  
  <h3>Log:</h3>
  <div id="log"></div>
  
  <script>
    function log(msg, type = 'info') {
      const logDiv = document.getElementById('log');
      const entry = document.createElement('div');
      entry.className = type;
      entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + msg;
      logDiv.appendChild(entry);
      logDiv.scrollTop = logDiv.scrollHeight;
      console.log(msg);
    }
    
    function showResponse(text, type = 'success') {
      const respDiv = document.getElementById('response');
      respDiv.textContent = text;
      respDiv.className = type;
    }
    
    async function sendChat() {
      const prompt = document.getElementById('prompt').value;
      const model = document.getElementById('model').value;
      const stream = document.getElementById('stream').checked;
      
      if (!prompt.trim()) {
        showResponse('Please enter a message!', 'error');
        return;
      }
      
      showResponse('Loading...', 'loading');
      log('Sending: ' + prompt);
      log('Model: ' + model + ', Stream: ' + stream);
      
      try {
        if (stream) {
          log('Starting streaming response...');
          const resp = await puter.ai.chat(prompt, { model, stream: true });
          
          let fullResponse = '';
          for await (const part of resp) {
            if (part && part.text) {
              fullResponse += part.text;
              showResponse(fullResponse, 'success');
            }
          }
          log('Stream complete!');
        } else {
          log('Getting non-streaming response...');
          const response = await puter.ai.chat(prompt, { model });
          showResponse(response, 'success');
          log('Response received!');
        }
      } catch (error) {
        showResponse('Error: ' + error.message, 'error');
        log('Error: ' + error.message, 'error');
      }
    }
    
    function clearResponse() {
      showResponse('Ready to chat...');
      document.getElementById('log').innerHTML = '';
    }
    
    window.addEventListener('load', () => {
      log('Puter.js loaded, ready to chat!');
      log('Available models: gemini-2.5-flash-lite, gemini-2.0-flash, gpt-5-nano');
    });
  </script>
</body>
</html>`;

const server = http.createServer((req, res) => {
  if (req.url === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(htmlContent);
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(PORT, () => {
  console.log(`Puter.js Test Server running at http://localhost:${PORT}`);
  console.log('Press Ctrl+C to stop');
});
