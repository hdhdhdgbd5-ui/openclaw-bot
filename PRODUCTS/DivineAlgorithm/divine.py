#!/usr/bin/env python3
"""
DIVINE ALGORITHM - Unified Launcher
The God-Mode Trading AI
"""

import sys
import asyncio

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     █████╗  ██████╗ ██████╗███████╗███████╗███████╗           ║
║    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝           ║
║    ███████║██║     ██║     █████╗  ███████╗███████╗           ║
║    ██╔══██║██║     ██║     ██╔══╝  ╚════██║╚════██║           ║
║    ██║  ██║╚██████╗╚██████╗███████╗███████║███████║           ║
║    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝           ║
║                                                               ║
║             ██████╗ ███████╗███████╗                         ║
║             ██╔══██╗██╔════╝██╔════╝                         ║
║             ██║  ██║█████╗  ███████╗                         ║
║             ██║  ██║██╔══╝  ╚════██║                         ║
║             ██████╔╝███████╗███████║                         ║
║             ╚═════╝ ╚══════╝╚══════╝                         ║
║                                                               ║
║              THE GOD-MODE TRADING AI                          ║
║           ⚡ GUARANTEED MONEY THROUGH ARBITRAGE ⚡            ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("Usage: python divine.py <mode>")
        print()
        print("Modes:")
        print("  arbitrage    - Monitor exchanges for arbitrage opportunities")
        print("  signals      - Generate trading signals")
        print("  portfolio    - Track portfolio")
        print("  all          - Run all modules")
        return
        
    mode = sys.argv[1].lower()
    
    if mode == "arbitrage":
        from divine_algorithm import quick_scan
        asyncio.run(quick_scan())
        
    elif mode == "signals":
        from trading_signals import TradingSignals
        trader = TradingSignals()
        trader.print_report()
        
    elif mode == "portfolio":
        from portfolio_tracker import PortfolioTracker
        tracker = PortfolioTracker()
        tracker.add_holding('BTCUSDT', 0.5, 42000)
        tracker.add_holding('ETHUSDT', 5.0, 2200)
        tracker.add_holding('SOLUSDT', 50, 95)
        tracker.print_portfolio()
        
    elif mode == "all":
        print("\n" + "="*60)
        print("RUNNING ALL MODULES")
        print("="*60)
        
        # Arbitrage
        from divine_algorithm import quick_scan
        print("\n[1/3] CHECKING ARBITRAGE...")
        asyncio.run(quick_scan())
        
        # Signals
        from trading_signals import TradingSignals
        print("\n[2/3] GENERATING SIGNALS...")
        trader = TradingSignals()
        trader.print_report()
        
        # Portfolio
        from portfolio_tracker import PortfolioTracker
        print("\n[3/3] PORTFOLIO STATUS...")
        tracker = PortfolioTracker()
        tracker.add_holding('BTCUSDT', 0.5, 42000)
        tracker.add_holding('ETHUSDT', 5.0, 2200)
        tracker.add_holding('SOLUSDT', 50, 95)
        tracker.print_portfolio()
        
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()
