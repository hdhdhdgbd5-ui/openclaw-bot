"""
OMNIGENIUS - Module 3: Arbitrage Monitor
Monitors domain expiries, crypto prices, and alerts for profit opportunities
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict
import random

# Alert thresholds
CRYPTO_PRICE_CHANGE_THRESHOLD = 5  # %
DOMAIN_EXPIRY_DAYS = 30  # Days until expiry


class ArbitrageMonitor:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or "PRODUCTS/OmniGenius/alerts"
        self.alerts = []
        os.makedirs(self.output_dir, exist_ok=True)
        
    def check_crypto_prices(self, coins: List[str] = None) -> List[Dict]:
        """Check for crypto price arbitrage opportunities"""
        opportunities = []
        
        if coins is None:
            coins = ["BTC", "ETH", "SOL", "ADA", "DOT"]
            
        try:
            from web_fetch import web_fetch
            
            # Fetch prices from multiple sources (demo with web fetch)
            for coin in coins:
                try:
                    # Simulate price check - in production use crypto API
                    price_variation = random.uniform(-8, 8)
                    
                    if abs(price_variation) >= CRYPTO_PRICE_CHANGE_THRESHOLD:
                        opportunities.append({
                            "type": "crypto_arbitrage",
                            "asset": coin,
                            "change_percent": round(price_variation, 2),
                            "action": "SELL" if price_variation > 0 else "BUY",
                            "profit_potential": f"${abs(price_variation) * 10:.2f}",
                            "timestamp": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    print(f"[ArbitrageMonitor] Error checking {coin}: {e}")
                    
        except Exception as e:
            print(f"[ArbitrageMonitor] Crypto check error: {e}")
            
        if opportunities:
            self.alerts.extend(opportunities)
            self._send_alerts(opportunities)
            
        return opportunities
    
    def check_domain_expiries(self, domains: List[str] = None) -> List[Dict]:
        """Check for expiring domains with profit potential"""
        opportunities = []
        
        if domains is None:
            # Demo domains
            domains = [
                "example-startup.io",
                "tech-gadgets.com", 
                "fitness-pro.net",
                "crypto-trader.io",
                "smart-home.tech"
            ]
            
        try:
            from web_fetch import web_fetch
            
            for domain in domains:
                try:
                    # Simulate domain expiry check
                    days_until_expiry = random.randint(5, 60)
                    domain_value = random.randint(100, 5000)
                    renewal_cost = random.randint(10, 50)
                    
                    if days_until_expiry <= DOMAIN_EXPIRY_DAYS:
                        profit = domain_value - renewal_cost
                        
                        if profit > 100:  # Only worth it if profit > $100
                            opportunities.append({
                                "type": "domain_arbitrage",
                                "domain": domain,
                                "days_until_expiry": days_until_expiry,
                                "estimated_value": f"${domain_value}",
                                "renewal_cost": f"${renewal_cost}",
                                "profit_potential": f"${profit}",
                                "timestamp": datetime.now().isoformat()
                            })
                            
                except Exception as e:
                    print(f"[ArbitrageMonitor] Error checking {domain}: {e}")
                    
        except Exception as e:
            print(f"[ArbitrageMonitor] Domain check error: {e}")
            
        if opportunities:
            self.alerts.extend(opportunities)
            self._send_alerts(opportunities)
            
        return opportunities
    
    def check_price_gaps(self) -> List[Dict]:
        """Check for cross-market price gaps (NFTs, tokens, etc)"""
        opportunities = []
        
        # Simulate checking various marketplaces
        items = [
            {"name": "Premium Domain Bundle", "buy_price": 500, "sell_price": 1200},
            {"name": "Limited NFT Collection", "buy_price": 200, "sell_price": 800},
            {"name": "DeFi Token", "buy_price": 0.50, "sell_price": 1.20},
        ]
        
        for item in items:
            profit = item["sell_price"] - item["buy_price"]
            margin = (profit / item["buy_price"]) * 100
            
            if margin > 30:  # 30%+ margin
                opportunities.append({
                    "type": "price_gap",
                    "item": item["name"],
                    "buy_price": item["buy_price"],
                    "sell_price": item["sell_price"],
                    "profit": f"${profit:.2f}",
                    "margin_percent": f"{margin:.1f}%",
                    "timestamp": datetime.now().isoformat()
                })
                
        if opportunities:
            self.alerts.extend(opportunities)
            self._send_alerts(opportunities)
            
        return opportunities
    
    def _send_alerts(self, alerts: List[Dict]):
        """Send alert notifications"""
        for alert in alerts:
            print(f"[ArbitrageMonitor] 🚨 ALERT: {alert['type']} - {alert.get('domain', alert.get('asset', alert.get('item', '')))}")
            print(f"   → Profit potential: {alert.get('profit_potential', alert.get('profit', 'TBD'))}")
            
        # Save alerts to file
        alert_file = os.path.join(self.output_dir, f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(alert_file, 'w') as f:
            json.dump(alerts, f, indent=2)
            
        print(f"[ArbitrageMonitor] Alerts saved to {alert_file}")
        
    def run_full_scan(self):
        """Run complete arbitrage scan"""
        print("[ArbitrageMonitor] Starting full arbitrage scan...")
        
        results = {
            "crypto": self.check_crypto_prices(),
            "domains": self.check_domain_expiries(),
            "price_gaps": self.check_price_gaps()
        }
        
        total_opportunities = sum(len(v) for v in results.values())
        print(f"[ArbitrageMonitor] Scan complete. Found {total_opportunities} opportunities.")
        
        return results
    
    def continuous_monitor(self, interval_seconds: int = 3600):
        """Run continuous monitoring"""
        print(f"[ArbitrageMonitor] Starting continuous monitoring (every {interval_seconds}s)...")
        
        while True:
            try:
                self.run_full_scan()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("[ArbitrageMonitor] Monitoring stopped")
                break
            except Exception as e:
                print(f"[ArbitrageMonitor] Error: {e}")
                time.sleep(60)


if __name__ == "__main__":
    monitor = ArbitrageMonitor()
    monitor.run_full_scan()
