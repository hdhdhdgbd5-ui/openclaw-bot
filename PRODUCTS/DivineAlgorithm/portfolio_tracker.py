#!/usr/bin/env python3
"""
DIVINE ALGORITHM - Portfolio Tracker
Track crypto holdings and calculate P&L
"""

import json
from datetime import datetime
from typing import Dict, List
import urllib.request

class PortfolioTracker:
    """Track crypto portfolio with real-time prices"""
    
    def __init__(self):
        self.holdings = []
        self.transactions = []
        
    def add_holding(self, symbol: str, amount: float, avg_price: float):
        """Add a holding to portfolio"""
        holding = {
            'symbol': symbol,
            'amount': amount,
            'avg_price': avg_price,
            'added': datetime.now().isoformat()
        }
        
        # Check if exists
        for h in self.holdings:
            if h['symbol'] == symbol:
                # Update average
                total_cost = h['amount'] * h['avg_price'] + amount * avg_price
                h['amount'] += amount
                h['avg_price'] = total_cost / h['amount']
                return
                
        self.holdings.append(holding)
        
    def remove_holding(self, symbol: str, amount: float):
        """Remove partial or full holding"""
        for h in self.holdings:
            if h['symbol'] == symbol:
                h['amount'] -= amount
                if h['amount'] <= 0:
                    self.holdings.remove(h)
                return
                
    def get_price(self, symbol: str) -> float:
        """Fetch current price from Binance"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return float(data['price'])
        except:
            return 0
            
    def calculate_portfolio(self) -> Dict:
        """Calculate total portfolio value and P&L"""
        total_value = 0
        total_cost = 0
        holdings_data = []
        
        for h in self.holdings:
            current_price = self.get_price(h['symbol'])
            if current_price > 0:
                value = h['amount'] * current_price
                cost = h['amount'] * h['avg_price']
                pnl = value - cost
                pnl_percent = (pnl / cost * 100) if cost > 0 else 0
                
                holdings_data.append({
                    'symbol': h['symbol'],
                    'amount': h['amount'],
                    'avg_price': h['avg_price'],
                    'current_price': current_price,
                    'value': value,
                    'cost': cost,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent
                })
                
                total_value += value
                total_cost += cost
                
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'holdings': holdings_data,
            'total_value': total_value,
            'total_cost': total_cost,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'timestamp': datetime.now().isoformat()
        }
    
    def print_portfolio(self):
        """Print portfolio report"""
        portfolio = self.calculate_portfolio()
        
        print(f"\n{'='*70}")
        print(f"DIVINE ALGORITHM - Portfolio Tracker")
        print(f"{'='*70}")
        print(f"Updated: {portfolio['timestamp']}")
        print()
        
        if not portfolio['holdings']:
            print("No holdings. Add with: tracker.add_holding('BTC', 0.5, 45000)")
            return
            
        print(f"{'Symbol':<10} {'Amount':<12} {'Avg Price':<12} {'Current':<12} {'Value':<14} {'P&L':<14} {'%'}")
        print("-" * 70)
        
        for h in portfolio['holdings']:
            pnl_str = f"${h['pnl']:,.2f}"
            if h['pnl'] < 0:
                pnl_str = f"-${abs(h['pnl']):,.2f}"
                
            print(f"{h['symbol']:<10} {h['amount']:<12.6f} ${h['avg_price']:<11,.2f} ${h['current_price']:<11,.2f} ${h['value']:<13,.2f} {pnl_str:<14} {h['pnl_percent']:+.2f}%")
            
        print("-" * 70)
        print(f"TOTAL:        Cost: ${portfolio['total_cost']:,.2f}  Value: ${portfolio['total_value']:,.2f}")
        print(f"P&L: ${portfolio['total_pnl']:,.2f} ({portfolio['total_pnl_percent']:+.2f}%)")
        print(f"{'='*70}")


# Demo portfolio
if __name__ == "__main__":
    tracker = PortfolioTracker()
    
    # Add some demo holdings
    tracker.add_holding('BTCUSDT', 0.5, 42000)
    tracker.add_holding('ETHUSDT', 5.0, 2200)
    tracker.add_holding('SOLUSDT', 50, 95)
    tracker.add_holding('BNBUSDT', 10, 280)
    
    tracker.print_portfolio()
