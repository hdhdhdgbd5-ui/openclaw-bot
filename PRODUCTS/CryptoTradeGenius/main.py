#!/usr/bin/env python3
"""
CryptoTradeGenius - Main Entry Point
Institutional-Grade AI Crypto Trading Bot

Usage:
    python main.py              # Start trading engine
    python main.py --api        # Start API server only
    python main.py --backtest   # Run backtest mode
    python main.py --paper      # Force paper trading mode
"""

import asyncio
import argparse
import sys
from loguru import logger

from config.settings import settings
from src.core.trading_engine import trading_engine
from src.api.server import start_server
from src.core.database import init_database


def setup_logging():
    """Configure logging"""
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # File logging
    logger.add(
        "logs/trading.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Error logging
    logger.add(
        "logs/errors.log",
        rotation="10 MB",
        retention="30 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}"
    )


async def main_trading():
    """Main trading mode"""
    logger.info("=" * 60)
    logger.info("🚀 CryptoTradeGenius - AI Trading Bot Starting")
    logger.info("=" * 60)
    logger.info(f"Trading Mode: {'📝 PAPER' if settings.is_paper_trading else '🔴 LIVE'}")
    logger.info(f"Database: {settings.database_url}")
    
    # Initialize and start
    await trading_engine.initialize()
    
    try:
        await trading_engine.start()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down gracefully...")
        trading_engine.stop()


def main_api():
    """API server mode"""
    logger.info("🌐 Starting CryptoTradeGenius API Server...")
    start_server()


def main_backtest():
    """Backtest mode"""
    logger.info("🔬 Running backtest mode...")
    # TODO: Implement backtest CLI
    logger.info("Backtest mode not yet implemented via CLI. Use API instead.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CryptoTradeGenius - AI Crypto Trading Bot"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server only"
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run backtest mode"
    )
    parser.add_argument(
        "--paper",
        action="store_true",
        help="Force paper trading mode"
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize database and exit"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Force paper mode if specified
    if args.paper:
        settings.trading_mode = "paper"
        logger.info("📋 Paper trading mode forced via CLI")
    
    # Initialize database
    if args.init_db:
        logger.info("🗄️ Initializing database...")
        init_database(settings.database_url)
        logger.info("✅ Database initialized")
        return
    
    # Run appropriate mode
    if args.api:
        main_api()
    elif args.backtest:
        main_backtest()
    else:
        asyncio.run(main_trading())


if __name__ == "__main__":
    main()
