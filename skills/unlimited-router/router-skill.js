/**
 * UNLIMITED ROUTER SKILL
 * Skill interface for other agents to use the router
 */

const { UnlimitedRouter } = require('./router');

let router = null;

function getRouter() {
  if (!router) {
    router = new UnlimitedRouter('./skills/unlimited-router/config.json');
  }
  return router;
}

async function chat(messages, options = {}) {
  const r = getRouter();
  return await r.chat(messages, options);
}

function status() {
  const r = getRouter();
  return r.getStatus();
}

async function test() {
  const r = getRouter();
  const testPrompt = 'Say "Router test successful" and nothing else.';
  return await r.chat([{ role: 'user', content: testPrompt }]);
}

// Export for skill system
module.exports = { chat, status, test, getRouter };

// CLI for direct execution
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (command === 'chat') {
    const msg = args.slice(1).join(' ') || 'Hello';
    chat([{ role: 'user', content: msg }])
      .then(r => console.log(`Provider: ${r.providerName}\nResponse: ${r.response}`))
      .catch(e => console.error('Error:', e.message));
  } else if (command === 'status') {
    console.log(JSON.stringify(status(), null, 2));
  } else if (command === 'test') {
    test().then(r => console.log('✅ Test passed:', r.response.substring(0, 50)))
      .catch(e => console.error('❌ Test failed:', e.message));
  } else {
    console.log('Usage: node router-skill.js [chat|status|test] [message]');
  }
}
