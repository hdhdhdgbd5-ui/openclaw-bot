"""
OMNIGENIUS - Core Engine
Autonomous Profit Engine - Main Controller
"""

import os
import json
import sys
from datetime import datetime
from typing import List, Dict

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.violation_hunter import ViolationHunter
from modules.affiliate_swarm import AffiliateSwarm
from modules.arbitrage_monitor import ArbitrageMonitor


class OmniGeniusEngine:
    """
    Core Engine for OMNIGENIUS - Autonomous Profit System
    
    Module 1: Violation Hunter - Scan corporations for legal violations
    Module 2: Affiliate Swarm - Find trending products, build landing pages
    Module 3: Arbitrage Monitor - Monitor prices, alert for profit opportunities
    """
    
    def __init__(self):
        self.wallet = "0xe23d9C5422A8bdB5281b15596111814808f98F1A"
        self.modules = {}
        self.running = False
        
        print("[OmniGenius] Engine v1.0 Initialized")
        print(f"[OmniGenius] Wallet: {self.wallet[:10]}...{self.wallet[-4:]}")
        
    def initialize_modules(self):
        """Initialize all profit modules"""
        print("\n[OmniGenius] Initializing modules...")
        
        self.modules['violation_hunter'] = ViolationHunter()
        self.modules['affiliate_swarm'] = AffiliateSwarm()
        self.modules['arbitrage_monitor'] = ArbitrageMonitor()
        
        print("[OmniGenius] All modules ready ✓")
        
    def run_module(self, module_name: str, **kwargs):
        """Run a specific module"""
        if module_name not in self.modules:
            print(f"[OmniGenius] Unknown module: {module_name}")
            return None
            
        print(f"\n[OmniGenius] Running module: {module_name}")
        module = self.modules[module_name]
        
        try:
            if module_name == 'violation_hunter':
                return module.run_scan(kwargs.get('companies'))
            elif module_name == 'affiliate_swarm':
                return module.run(kwargs.get('categories'))
            elif module_name == 'arbitrage_monitor':
                return module.run_full_scan()
        except Exception as e:
            print(f"[OmniGenius] Module error: {e}")
            return None
            
    def run_all_modules(self):
        """Run all profit modules sequentially"""
        print("\n" + "="*50)
        print("[OmniGenius] RUNNING FULL AUTONOMOUS PROFIT SCAN")
        print("="*50 + "\n")
        
        results = {}
        
        # Module 1: Violation Hunter
        print("\n🔍 [1/3] Violation Hunter - Scanning for legal violations...")
        results['violations'] = self.run_module('violation_hunter')
        
        # Module 2: Affiliate Swarm  
        print("\n🛒 [2/3] Affiliate Swarm - Finding trending products...")
        results['affiliates'] = self.run_module('affiliate_swarm')
        
        # Module 3: Arbitrage Monitor
        print("\n💰 [3/3] Arbitrage Monitor - Finding profit opportunities...")
        results['arbitrage'] = self.run_module('arbitrage_monitor')
        
        # Summary
        total_findings = (
            len(results.get('violations', [])) +
            len(results.get('affiliates', {}).get('products', [])) +
            sum(len(v) for v in results.get('arbitrage', {}).values())
        )
        
        print("\n" + "="*50)
        print(f"[OmniGenius] SCAN COMPLETE - {total_findings} profit opportunities found")
        print("="*50)
        
        return results
        
    def start_continuous_mode(self, interval_hours: int = 24):
        """Start continuous profit generation"""
        print(f"\n[OmniGenius] Starting continuous mode (every {interval_hours}h)...")
        self.running = True
        
        import time
        while self.running:
            try:
                self.run_all_modules()
                print(f"[OmniGenius] Sleeping for {interval_hours}h...")
                time.sleep(interval_hours * 3600)
            except KeyboardInterrupt:
                print("\n[OmniGenius] Stopping continuous mode")
                self.running = False
                
    def stop(self):
        """Stop the engine"""
        self.running = False
        print("[OmniGenius] Engine stopped")


if __name__ == "__main__":
    engine = OmniGeniusEngine()
    engine.initialize_modules()
    
    # Run once
    engine.run_all_modules()
