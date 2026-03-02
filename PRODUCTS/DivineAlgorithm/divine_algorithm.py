#!/usr/bin/env python3
"""
DIVINE ALGORITHM - The God-Mode Trading AI
Arbitrage Monitor - Detects price differences between exchanges
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import urllib.request
import urllib.error

# Configuration
CHECK_INTERVAL = 30  # seconds
MIN_ARBITRAGE_PERCENT = 0.5  # minimum profit % to alert

# Major crypto pairs to monitor
PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "DOTUSDT", "MATICUSDT"
]

class ArbitrageMonitor:
    """Monitor prices across exchanges for arbitrage opportunities"""
    
    def __init__(self):
        self.exchanges = {
            "binance": "https://api.binance.com/api/v3/ticker/price?symbol={symbol}",
            "kucoin": "https://api-api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}",
            # Add more exchanges as needed
        }
        self.prices = {}
        self.opportunities = []
        
    def fetch_binance(self, symbol: str) -> Optional[float]:
        """Fetch price from Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return float(data['price'])
        except Exception as e:
            print(f"Binance error for {symbol}: {e}")
            return None
    
    def fetch_kucoin(self, symbol: str) -> Optional[float]:
        """Fetch price from KuCoin"""
        try:
            # KuCoin uses different symbol format (BTC-USDT)
            ku_symbol = symbol.replace('USDT', '-USDT')
            url = f"https://api-api.kucoin.com/api/v1/market/orderbook/level1?symbol={ku_symbol}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data.get('data'):
                    return float(data['data']['price'])
        except Exception as e:
            pass  # Silent fail for optional exchange
        return None
    
    def fetch_coingecko_simple(self, symbol: str) -> Optional[float]:
        """Fetch price from CoinGecko simple price (limited)"""
        # Map symbols to CoinGecko IDs
        symbol_map = {
            "BTCUSDT": "bitcoin",
            "ETHUSDT": "ethereum",
            "BNBUSDT": "binancecoin",
            "SOLUSDT": "solana",
            "XRPUSDT": "ripple",
            "ADAUSDT": "cardano",
            "DOGEUSDT": "dogecoin",
            "AVAXUSDT": "avalanche-2",
            "DOTUSDT": "polkadot",
            "MATICUSDT": "matic-network"
        }
        
        coin_id = symbol_map.get(symbol)
        if not coin_id:
            return None
            
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                if coin_id in data:
                    return float(data[coin_id]['usd'])
        except Exception as e:
            pass
        return None
    
    async def check_arbitrage(self, symbol: str) -> List[Dict]:
        """Check for arbitrage opportunities for a symbol"""
        opportunities = []
        
        # Get prices from all exchanges
        prices = {}
        
        # Binance (primary)
        binance_price = await asyncio.to_thread(self.fetch_binance, symbol)
        if binance_price:
            prices['Binance'] = binance_price
            
        # CoinGecko (as reference)
        cg_price = await asyncio.to_thread(self.fetch_coingecko_simple, symbol)
        if cg_price:
            prices['CoinGecko'] = cg_price
            
        if len(prices) < 2:
            return opportunities
            
        # Find price differences
        price_list = list(prices.values())
        min_price = min(price_list)
        max_price = max(price_list)
        
        diff_percent = ((max_price - min_price) / min_price) * 100
        
        if diff_percent >= MIN_ARBITRAGE_PERCENT:
            min_exchange = [k for k, v in prices.items() if v == min_price][0]
            max_exchange = [k for k, v in prices.items() if v == max_price][0]
            
            opportunity = {
                'symbol': symbol,
                'buy_exchange': min_exchange,
                'sell_exchange': max_exchange,
                'buy_price': min_price,
                'sell_price': max_price,
                'profit_percent': round(diff_percent, 2),
                'timestamp': datetime.now().isoformat()
            }
            opportunities.append(opportunity)
            
        return opportunities
    
    async def scan_all(self) -> List[Dict]:
        """Scan all pairs for arbitrage"""
        all_opportunities = []
        
        print(f"\n{'='*60}")
        print(f"DIVINE ALGORITHM - Arbitrage Scanner")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        for pair in PAIRS:
            ops = await self.check_arbitrage(pair)
            if ops:
                all_opportunities.extend(ops)
                for op in ops:
                    print(f"🚨 ARBITRAGE: {op['symbol']}")
                    print(f"   Buy at {op['buy_exchange']}: ${op['buy_price']:,.2f}")
                    print(f"   Sell at {op['sell_exchange']}: ${op['sell_price']:,.2f}")
                    print(f"   Profit: {op['profit_percent']}%")
            else:
                print(f"✅ {pair}: No arbitrage")
                
        return all_opportunities
    
    async def run_continuous(self):
        """Run continuous monitoring"""
        print("🚀 DIVINE ALGORITHM started!")
        print(f"Monitoring {len(PAIRS)} pairs every {CHECK_INTERVAL}s")
        print(f"Minimum arbitrage threshold: {MIN_ARBITRAGE_PERCENT}%")
        
        while True:
            try:
                await self.scan_all()
                await asyncio.sleep(CHECK_INTERVAL)
            except KeyboardInterrupt:
                print("\n🛑 Stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(CHECK_INTERVAL)


async def quick_scan():
    """Quick single scan"""
    monitor = ArbitrageMonitor()
    ops = await monitor.scan_all()
    
    if ops:
        print(f"\n💰 Found {len(ops)} arbitrage opportunity(ies)!")
    else:
        print("\n💤 No arbitrage opportunities found")
        
    return ops


if __name__ == "__main__":
    # Quick scan by default
    asyncio.run(quick_scan())
