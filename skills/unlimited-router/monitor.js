/**
 * UNLIMITED ROUTER MONITOR
 * Real-time monitoring dashboard for infinite API rotation
 */

const fs = require('fs');
const { UnlimitedRouter } = require('./router');

class RouterMonitor {
  constructor(router) {
    this.router = router;
    this.logFile = 'logs/router-usage.log';
    this.dailyStats = new Map();
    this.ensureLogDir();
  }

  ensureLogDir() {
    const dir = 'logs';
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  start() {
    console.log('[MONITOR] Starting 24/7 uptime monitoring...');
    
    // Periodic status logging
    setInterval(() => this.logStatus(), 60000);
    
    // Daily stats reset
    setInterval(() => this.resetDailyStats(), 24 * 60 * 60 * 1000);
    
    // Alert on issues
    this.router.on('rateLimit', (providerId) => {
      this.alert(`Rate limit hit on ${providerId}`);
    });
    
    this.router.on('providerDown', (providerId) => {
      this.alert(`Provider ${providerId} is down`);
    });
  }

  logStatus() {
    const status = this.router.getStatus();
    const entry = {
      timestamp: new Date().toISOString(),
      ...status
    };
    
    fs.appendFileSync(this.logFile, JSON.stringify(entry) + '\n');
    
    // Console dashboard
    console.clear();
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║       🚀 UNLIMITED ROUTER - LIVE STATUS DASHBOARD          ║');
    console.log('╠══════════════════════════════════════════════════════════╣');
    console.log(`║  Total Requests Today: ${status.totalRequests.toString().padEnd(38)}║`);
    console.log(`║  Time: ${new Date().toLocaleTimeString().padEnd(48)}║`);
    console.log('╠══════════════════════════════════════════════════════════╣');
    console.log('║  PROVIDER           │ HEALTH  │ TODAY  │ COOLDOWN        ║');
    console.log('╠═════════════════════╪═════════╪════════╪══════════════════╣');
    
    status.providers.forEach(p => {
      const health = p.health.status === 'healthy' ? '✅' : '❌';
      const cooldown = p.cooldown > 0 ? `${Math.ceil(p.cooldown/1000)}s` : 'READY';
      const name = p.name.padEnd(19);
      const reqs = p.usage.requestsToday.toString().padEnd(6);
      console.log(`║  ${name}│  ${health}    │ ${reqs}│ ${cooldown.padEnd(15)} ║`);
    });
    
    console.log('╚══════════════════════════════════════════════════════════╝');
  }

  alert(message) {
    console.warn(`[ALERT] ${message}`);
    fs.appendFileSync('logs/router-alerts.log', `[${new Date().toISOString()}] ${message}\n`);
  }

  resetDailyStats() {
    this.router.providers.forEach(p => {
      const usage = this.router.usage.get(p.id);
      usage.requestsToday = 0;
    });
    console.log('[MONITOR] Daily stats reset');
  }

  getReport() {
    const logData = fs.readFileSync(this.logFile, 'utf8')
      .split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line));
    
    return {
      totalEntries: logData.length,
      uptime: '24/7',
      lastHour: logData.slice(-60),
      averageResponseTime: this.calculateAvgResponseTime(logData)
    };
  }

  calculateAvgResponseTime(logs) {
    const times = logs
      .map(l => l.providers?.map(p => p.health?.responseTime).filter(t => t))
      .flat()
      .filter(t => t);
    
    if (times.length === 0) return 0;
    return times.reduce((a, b) => a + b, 0) / times.length;
  }
}

module.exports = { RouterMonitor };
