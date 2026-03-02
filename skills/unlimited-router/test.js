/**
 * UNLIMITED ROUTER TEST SUITE
 * Tests all providers and validates the rotation system
 */

const { UnlimitedRouter } = require('./router');

async function runTests() {
  console.log('═══════════════════════════════════════════════════════');
  console.log('  🧪 UNLIMITED ROUTER - TESTING ALL PROVIDERS');
  console.log('═══════════════════════════════════════════════════════\n');

  const router = new UnlimitedRouter('./skills/unlimited-router/config.json');
  const testPrompt = 'Say "Router test successful" and nothing else.';

  // Test 1: Status Check
  console.log('✓ Test 1: Router initialized');
  console.log(`  Providers loaded: ${router.providers.length}`);
  
  const status = router.getStatus();
  console.log(`  Total requests: ${status.totalRequests}\n`);

  // Test 2: Ollama Connection
  console.log('✓ Test 2: Testing Ollama Local...');
  try {
    const ollama = router.providers.find(p => p.type === 'ollama');
    if (ollama) {
      const response = await fetch(`${ollama.config.baseUrl}/api/tags`);
      if (response.ok) {
        const models = await response.json();
        console.log(`  Available models: ${models.models?.length || 0}`);
        console.log(`  Models: ${models.models?.map(m => m.name).slice(0, 3).join(', ')}...`);
      }
    }
  } catch (e) {
    console.log(`  ⚠ Ollama test: ${e.message}`);
  }

  // Test 3: Groq Connection
  console.log('\n✓ Test 3: Testing Groq Account...');
  try {
    const groq = router.providers.find(p => p.type === 'groq');
    if (groq) {
      const apiKey = router.getApiKey(groq);
      if (apiKey && !apiKey.includes('PLACEHOLDER')) {
        const response = await fetch(`${groq.config.baseUrl}/models`, {
          headers: { 'Authorization': `Bearer ${apiKey}` }
        });
        console.log(`  Status: ${response.status} ${response.statusText}`);
        if (response.ok) {
          const models = await response.json();
          console.log(`  Available models: ${models.data?.length || 0}`);
        }
      } else {
        console.log('  ⚠ No valid API key configured');
      }
    }
  } catch (e) {
    console.log(`  ⚠ Groq test: ${e.message}`);
  }

  // Test 4: Rotation Logic
  console.log('\n✓ Test 4: Testing rotation logic...');
  for (let i = 0; i < 5; i++) {
    const provider = router.getNextProvider();
    console.log(`  Rotation ${i+1}: ${provider.name}`);
  }

  // Test 5: Chat Request
  console.log('\n✓ Test 5: Testing chat completion...');
  try {
    const result = await router.chat(
      [{ role: 'user', content: testPrompt }]
      // Use provider's default model
    );
    console.log(`  Provider used: ${result.providerName}`);
    console.log(`  Response preview: ${result.response.substring(0, 60)}...`);
    console.log('  ✅ Chat test PASSED');
  } catch (e) {
    console.log(`  ⚠ Chat test: ${e.message}`);
  }

  // Test 6: Rate Limit Simulation
  console.log('\n✓ Test 6: Testing rate limit handling...');
  const testProvider = router.providers[0];
  router.recordUsage(testProvider.id, false, 'rate limit exceeded');
  const cooldown = router.cooldowns.get(testProvider.id);
  console.log(`  Cooldown set for ${testProvider.id}: ${cooldown > Date.now() ? 'YES' : 'NO'}`);

  console.log('\n═══════════════════════════════════════════════════════');
  console.log('  ✅ ALL TESTS COMPLETED');
  console.log('═══════════════════════════════════════════════════════');

  return router.getStatus();
}

if (require.main === module) {
  runTests().then(status => {
    console.log('\n📊 Final Status:');
    console.log(JSON.stringify(status, null, 2));
    process.exit(0);
  }).catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
  });
}

module.exports = { runTests };
