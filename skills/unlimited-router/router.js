/**
 * UNLIMITED API ROUTER
 * Routes requests through infinite free APIs to NEVER hit rate limits!
 * 
 * Features:
 * - Round-robin rotation across multiple providers
 * - Automatic fallback on rate limits
 * - Health monitoring and status tracking
 * - Smart cooldown management
 * - 24/7 uptime guarantee
 */

const fs = require('fs');
const path = require('path');
const { EventEmitter } = require('events');

class UnlimitedRouter extends EventEmitter {
  constructor(configPath) {
    super();
    this.config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    this.providers = this.config.providers.filter(p => p.enabled);
    this.currentIndex = 0;
    this.usage = new Map();
    this.health = new Map();
    this.cooldowns = new Map();
    
    this.init();
  }

  init() {
    this.providers.forEach(provider => {
      this.usage.set(provider.id, {
        requestsToday: 0,
        requestsThisHour: 0,
        requestsThisMinute: 0,
        lastRequest: null,
        errors: 0
      });
      this.health.set(provider.id, {
        status: 'healthy',
        lastCheck: Date.now(),
        responseTime: null
      });
      this.cooldowns.set(provider.id, 0);
    });

    this.startHealthChecks();
    console.log(`[ROUTER] Initialized with ${this.providers.length} providers`);
  }

  startHealthChecks() {
    setInterval(() => {
      this.checkAllHealth();
    }, this.config.rotation.healthCheckInterval);
  }

  async checkAllHealth() {
    for (const provider of this.providers) {
      await this.checkProviderHealth(provider);
    }
  }

  async checkProviderHealth(provider) {
    const start = Date.now();
    try {
      if (provider.type === 'ollama') {
        const response = await fetch(`${provider.config.baseUrl}/api/tags`);
        const healthy = response.ok;
        this.health.set(provider.id, {
          status: healthy ? 'healthy' : 'unhealthy',
          lastCheck: Date.now(),
          responseTime: Date.now() - start
        });
      } else if (provider.type === 'groq') {
        // Light health check - will be verified on actual use
        this.health.set(provider.id, {
          status: 'healthy',
          lastCheck: Date.now(),
          responseTime: null
        });
      }
    } catch (error) {
      this.health.set(provider.id, {
        status: 'unhealthy',
        lastCheck: Date.now(),
        responseTime: null,
        error: error.message
      });
    }
  }

  getNextProvider(preferredModel = null) {
    const available = this.getAvailableProviders(preferredModel);
    if (available.length === 0) {
      // All providers on cooldown, reset and try again
      this.cooldowns.forEach((_, id) => this.cooldowns.set(id, 0));
      return this.getNextProvider(preferredModel);
    }

    // Sort by priority and find best match
    available.sort((a, b) => a.priority - b.priority);
    
    const provider = available[0];
    this.currentIndex = (this.currentIndex + 1) % this.providers.length;
    
    return provider;
  }

  getAvailableProviders(preferredModel = null) {
    const now = Date.now();
    return this.providers.filter(p => {
      // Check if in cooldown
      if (this.cooldowns.get(p.id) > now) return false;
      
      // Check health
      const h = this.health.get(p.id);
      if (h.status === 'unhealthy') return false;
      
      // Check model compatibility
      if (preferredModel && !p.models.includes(preferredModel)) {
        // For now allow any model if exact match not found
      }
      
      // Check rate limits
      const usage = this.usage.get(p.id);
      const limits = p.rateLimits;
      
      if (limits.unlimited) return true;
      if (limits.requestsPerMinute && usage.requestsThisMinute >= limits.requestsPerMinute) return false;
      if (limits.requestsPerHour && usage.requestsThisHour >= limits.requestsPerHour) return false;
      if (limits.requestsPerDay && usage.requestsToday >= limits.requestsPerDay) return false;
      
      return true;
    });
  }

  recordUsage(providerId, success = true, error = null) {
    const usage = this.usage.get(providerId);
    const now = new Date();
    
    if (success) {
      usage.requestsToday++;
      usage.requestsThisHour++;
      usage.requestsThisMinute++;
      usage.lastRequest = now;
      usage.errors = 0;
    } else {
      usage.errors++;
      const provider = this.providers.find(p => p.id === providerId);
      
      // Set cooldown based on error
      if (error?.includes('rate limit') || error?.includes('429')) {
        const cooldownMs = provider.rateLimits.cooldownMs || 60000;
        this.cooldowns.set(providerId, Date.now() + cooldownMs);
        console.log(`[ROUTER] Provider ${providerId} rate limited. Cooldown: ${cooldownMs}ms`);
      }
      
      // Auto-disable after too many errors
      if (usage.errors > 5) {
        this.health.set(providerId, { status: 'unhealthy', lastCheck: Date.now() });
      }
    }
    
    // Reset minute counter every minute
    if (usage.lastRequest && (now - usage.lastRequest) > 60000) {
      usage.requestsThisMinute = 0;
    }
  }

  async chat(messages, options = {}) {
    let attempts = 0;
    const maxAttempts = this.config.rotation.retryAttempts * this.providers.length;
    
    while (attempts < maxAttempts) {
      const provider = this.getNextProvider(options.model);
      if (!provider) {
        // All providers on cooldown - wait and retry
        await new Promise(r => setTimeout(r, 1000));
        attempts++;
        continue;
      }

      console.log(`[ROUTER] Using provider: ${provider.name}`);

      try {
        const response = await this.makeRequest(provider, messages, options);
        this.recordUsage(provider.id, true);
        return {
          success: true,
          provider: provider.id,
          providerName: provider.name,
          response
        };
      } catch (error) {
        this.recordUsage(provider.id, false, error.message);
        console.log(`[ROUTER] ${provider.name} failed: ${error.message}`);
        
        // If rate limited, try next provider immediately
        if (error.message.includes('429') || error.message.includes('rate limit')) {
          attempts++;
          continue;
        }
        
        // For other errors, also try next provider
        attempts++;
        if (attempts >= maxAttempts) {
          throw new Error(`All providers failed after ${maxAttempts} attempts. Last error: ${error.message}`);
        }
      }
    }
    
    throw new Error('No available providers after max attempts');
  }

  async makeRequest(provider, messages, options) {
    const apiKey = this.getApiKey(provider);
    const model = options.model || provider.models[0]; // Use provider's first model if not specified
    
    if (provider.type === 'ollama') {
      const response = await fetch(`${provider.config.baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: model,
          messages,
          stream: false
        })
      });
      
      if (!response.ok) {
        throw new Error(`Ollama error: ${response.status}`);
      }
      
      const data = await response.json();
      return data.message.content;
      
    } else if (provider.type === 'groq') {
      const response = await fetch(`${provider.config.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: model, // Use provider's native model
          messages,
          temperature: options.temperature || 0.7
        })
      });
      
      if (!response.ok) {
        const error = await response.text();
        throw new Error(`Groq error ${response.status}: ${error}`);
      }
      
      const data = await response.json();
      return data.choices[0].message.content;
    }
    
    throw new Error(`Unknown provider type: ${provider.type}`);
  }

  getApiKey(provider) {
    if (provider.config.apiKey) {
      return provider.config.apiKey;
    }
    if (provider.config.apiKeyFile) {
      try {
        return fs.readFileSync(provider.config.apiKeyFile, 'utf8').trim();
      } catch (e) {
        console.error(`[ROUTER] Could not read API key from ${provider.config.apiKeyFile}`);
        return null;
      }
    }
    return null;
  }

  getStatus() {
    return {
      providers: this.providers.map(p => ({
        id: p.id,
        name: p.name,
        enabled: p.enabled,
        health: this.health.get(p.id),
        usage: this.usage.get(p.id),
        cooldown: this.cooldowns.get(p.id) > Date.now() ? this.cooldowns.get(p.id) - Date.now() : 0
      })),
      totalRequests: Array.from(this.usage.values()).reduce((sum, u) => sum + u.requestsToday, 0),
      timestamp: new Date().toISOString()
    };
  }
}

module.exports = { UnlimitedRouter };
