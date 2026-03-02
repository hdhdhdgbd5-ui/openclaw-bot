#!/usr/bin/env python3
"""Quick API status check - Run anytime"""

import json
from pathlib import Path
from datetime import datetime

def show_status():
    status_file = Path("logs/api_status.json")
    
    if not status_file.exists():
        print("❌ No status file found. Run api_monitor.py first!")
        return
    
    with open(status_file) as f:
        status = json.load(f)
    
    print("=" * 50)
    print("🌐 API STATUS DASHBOARD")
    print("=" * 50)
    
    groq_status = status.get("groq", "unknown")
    minimax_status = status.get("minimax", "unknown")
    
    # Groq
    if groq_status == "online":
        print("✅ Groq API:   ONLINE")
    elif groq_status == "offline":
        print("🚨 Groq API:   OFFLINE")
    else:
        print(f"⚠️  Groq API:   {groq_status.upper()}")
    
    # MiniMax  
    if minimax_status == "online":
        print("✅ MiniMax:    ONLINE")
    elif minimax_status == "offline":
        print("🚨 MiniMax:    OFFLINE")
    else:
        print(f"⚠️  MiniMax:    {minimax_status.upper()}")
    
    print("-" * 50)
    last_check = status.get("last_check", "Never")
    if last_check and last_check != "Never":
        try:
            dt = datetime.fromisoformat(last_check)
            print(f"🕐 Last Check: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            print(f"🕐 Last Check: {last_check}")
    print("=" * 50)

if __name__ == "__main__":
    show_status()
