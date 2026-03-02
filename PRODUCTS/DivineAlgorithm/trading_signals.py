#!/usr/bin/env python3
"""
DIVINE ALGORITHM - Trading Signal Generator
Simple technical indicators for buy/sell signals
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import urllib.request
import urllib.error

# Configuration
SYMBOL = "BTCUSDT"
INTERVAL = "1h"  # 1h, 4h, 1d

class TradingSignals:
    """Generate trading signals using technical indicators"""
    
    def __init__(self, symbol: str = "BTCUSDT"):
        self.symbol = symbol
        self.base_url = "https://api.binance.com/api/v3"
        
    def fetch_klines(self, interval: str = "1h", limit: int = 100) -> List:
        """Fetch candlestick data"""
        try:
            url = f"{self.base_url}/klines?symbol={self.symbol}&interval={interval}&limit={limit}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                # Parse: [open_time, open, high, low, close, volume, ...]
                return [(item[1], item[2], item[3], item[4], item[5]) for item in data]
        except Exception as e:
            print(f"Error fetching klines: {e}")
            return []
    
    def calculate_sma(self, data: List, period: int) -> float:
        """Simple Moving Average"""
        if len(data) < period:
            return 0
        prices = [float(d[3]) for d in data[-period:]]  # close prices
        return sum(prices) / period
    
    def calculate_ema(self, data: List, period: int) -> float:
        """Exponential Moving Average"""
        if len(data) < period:
            return 0
        prices = [float(d[3]) for d in data[-period:]]
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        return ema
    
    def calculate_rsi(self, data: List, period: int = 14) -> float:
        """Relative Strength Index"""
        if len(data) < period + 1:
            return 50
            
        closes = [float(d[3]) for d in data]
        gains = []
        losses = []
        
        for i in range(1, len(closes)):
            change = closes[i] - closes[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50
            
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data: List) -> Dict:
        """MACD (Moving Average Convergence Divergence)"""
        if len(data) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
            
        ema12 = self.calculate_ema(data, 12)
        ema26 = self.calculate_ema(data, 26)
        macd_line = ema12 - ema26
        
        # Calculate signal line (9-period EMA of MACD)
        # Simplified: just use SMA of recent MACD
        signal_line = macd_line * 0.9  # approximation
        
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def generate_signal(self) -> Dict:
        """Generate trading signal based on indicators"""
        data = self.fetch_klines(INTERVAL)
        
        if not data:
            return {'error': 'No data available'}
        
        current_price = float(data[-1][3])  # close price
        
        # Calculate indicators
        sma_20 = self.calculate_sma(data, 20)
        sma_50 = self.calculate_sma(data, 50)
        ema_9 = self.calculate_ema(data, 9)
        rsi = self.calculate_rsi(data)
        macd = self.calculate_macd(data)
        
        # Generate signals
        signals = []
        
        # RSI signals
        if rsi < 30:
            signals.append("RSI: Oversold (BUY)")
        elif rsi > 70:
            signals.append("RSI: Overbought (SELL)")
        else:
            signals.append(f"RSI: {rsi:.1f} (Neutral)")
        
        # SMA signals
        if current_price > sma_20:
            signals.append(f"Price > SMA20 (Bullish)")
        else:
            signals.append(f"Price < SMA20 (Bearish)")
            
        if sma_20 > sma_50:
            signals.append("Golden Cross (BUY)")
        elif sma_20 < sma_50:
            signals.append("Death Cross (SELL)")
        
        # MACD signals
        if macd['histogram'] > 0:
            signals.append("MACD: Bullish momentum")
        else:
            signals.append("MACD: Bearish momentum")
        
        # Overall signal
        buy_signals = sum(1 for s in signals if 'BUY' in s or 'Bullish' in s or 'Oversold' in s)
        sell_signals = sum(1 for s in signals if 'SELL' in s or 'Bearish' in s or 'Overbought' in s)
        
        if buy_signals > sell_signals + 1:
            overall = "STRONG BUY"
        elif buy_signals > sell_signals:
            overall = "BUY"
        elif sell_signals > buy_signals + 1:
            overall = "STRONG SELL"
        elif sell_signals > buy_signals:
            overall = "SELL"
        else:
            overall = "NEUTRAL"
        
        return {
            'symbol': self.symbol,
            'price': current_price,
            'timestamp': datetime.now().isoformat(),
            'indicators': {
                'rsi': round(rsi, 2),
                'sma_20': round(sma_20, 2),
                'sma_50': round(sma_50, 2),
                'ema_9': round(ema_9, 2),
                'macd': macd
            },
            'signals': signals,
            'overall': overall
        }
    
    def print_report(self):
        """Print trading signal report"""
        signal = self.generate_signal()
        
        if 'error' in signal:
            print(f"Error: {signal['error']}")
            return
            
        print(f"\n{'='*60}")
        print(f"DIVINE ALGORITHM - Trading Signals")
        print(f"{'='*60}")
        print(f"Symbol: {signal['symbol']}")
        print(f"Price: ${signal['price']:,.2f}")
        print(f"Time: {signal['timestamp']}")
        print(f"\n📊 INDICATORS:")
        print(f"   RSI(14): {signal['indicators']['rsi']}")
        print(f"   SMA(20): ${signal['indicators']['sma_20']:,.2f}")
        print(f"   SMA(50): ${signal['indicators']['sma_50']:,.2f}")
        print(f"   EMA(9): ${signal['indicators']['ema_9']:,.2f}")
        print(f"   MACD: {signal['indicators']['macd']}")
        
        print(f"\n🔔 SIGNALS:")
        for s in signal['signals']:
            print(f"   • {s}")
            
        print(f"\n🎯 OVERALL: {signal['overall']}")
        print(f"{'='*60}")


if __name__ == "__main__":
    trader = TradingSignals(SYMBOL)
    trader.print_report()
