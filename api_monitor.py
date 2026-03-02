#!/usr/bin/env python3
"""
API HUNTER 24/7 - System Monitor
Monitors MiniMax and Groq APIs continuously
"""

import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
MINIMAX_API_URL = "https://api.minimax.chat/v1/models"
GROQ_API_URL = "https://api.groq.com/openai/v1/models"
LOG_FILE = Path("logs/api_monitor.log")
STATUS_FILE = Path("logs/api_status.json")
CHECK_INTERVAL = 30  # seconds

# Ensure log directory exists
LOG_FILE.parent.mkdir(exist_ok=True)

def log(message, level="INFO"):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def load_status():
    """Load API status from file"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {"minimax": "unknown", "groq": "unknown", "last_check": None}

def save_status(status):
    """Save API status to file"""
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)

async def check_api(session, name, url, headers=None):
    """Check if an API is responding"""
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status == 200:
                return {"status": "online", "code": response.status, "latency": 0}
            else:
                return {"status": "degraded", "code": response.status, "latency": 0}
    except asyncio.TimeoutError:
        return {"status": "timeout", "code": 0, "latency": 0}
    except Exception as e:
        return {"status": "offline", "code": 0, "latency": 0, "error": str(e)}

async def check_groq_api():
    """Check Groq API status"""
    api_key = os.getenv("GROQ_API_KEY", "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")
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    async with aiohttp.ClientSession() as session:
        result = await check_api(session, "Groq", GROQ_API_URL, headers)
        return result

async def check_minimax_api():
    """Check MiniMax API status"""
    # MiniMax uses different endpoints - checking their API availability
    headers = {
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        result = await check_api(session, "MiniMax", MINIMAX_API_URL, headers)
        return result

async def monitor_cycle():
    """Single monitoring cycle"""
    current_status = load_status()
    
    log("=" * 60)
    log("🔍 API HUNTER - Starting Health Check Cycle")
    
    # Check Groq API
    log("📡 Checking Groq API...", "CHECK")
    groq_result = await check_groq_api()
    
    if groq_result["status"] == "online":
        log("✅ Groq API: ONLINE", "SUCCESS")
    elif groq_result["status"] == "degraded":
        log(f"⚠️  Groq API: DEGRADED (HTTP {groq_result['code']})", "WARNING")
    else:
        log(f"🚨 Groq API: OFFLINE - {groq_result.get('error', 'Unknown error')}", "ERROR")
    
    # Check MiniMax API  
    log("📡 Checking MiniMax API...", "CHECK")
    minimax_result = await check_minimax_api()
    
    if minimax_result["status"] == "online":
        log("✅ MiniMax API: ONLINE", "SUCCESS")
    elif minimax_result["status"] == "degraded":
        log(f"⚠️  MiniMax API: DEGRADED (HTTP {minimax_result['code']})", "WARNING")
    else:
        log(f"🚨 MiniMax API: OFFLINE - {minimax_result.get('error', 'Unknown error')}", "ERROR")
    
    # Update status
    new_status = {
        "groq": groq_result["status"],
        "minimax": minimax_result["status"],
        "last_check": datetime.now().isoformat(),
        "groq_details": groq_result,
        "minimax_details": minimax_result
    }
    
    save_status(new_status)
    
    # Check for status changes
    if current_status.get("groq") != groq_result["status"]:
        log(f"🔄 Groq API status changed: {current_status.get('groq')} -> {groq_result['status']}", "ALERT")
    
    if current_status.get("minimax") != minimax_result["status"]:
        log(f"🔄 MiniMax API status changed: {current_status.get('minimax')} -> {minimax_result['status']}", "ALERT")
    
    # Summary
    log("📊 STATUS SUMMARY:", "SUMMARY")
    log(f"   Groq: {groq_result['status'].upper()}", "SUMMARY")
    log(f"   MiniMax: {minimax_result['status'].upper()}", "SUMMARY")
    log(f"   Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "SUMMARY")
    log("=" * 60)
    
    return new_status

async def main():
    """Main monitoring loop"""
    log("🚀 API HUNTER 24/7 STARTING...")
    log(f"💾 Logs: {LOG_FILE.absolute()}")
    log(f"📁 Status: {STATUS_FILE.absolute()}")
    log(f"⏰ Interval: {CHECK_INTERVAL} seconds")
    log("=" * 60)
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            log(f"\n🔄 CYCLE #{cycle_count}")
            
            try:
                await monitor_cycle()
            except Exception as e:
                log(f"❌ Error in monitor cycle: {e}", "ERROR")
            
            log(f"⏳ Sleeping for {CHECK_INTERVAL} seconds...\n")
            await asyncio.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        log("🛑 Monitoring stopped by user", "STOP")
    except Exception as e:
        log(f"💥 FATAL ERROR: {e}", "FATAL")
        raise

if __name__ == "__main__":
    asyncio.run(main())
