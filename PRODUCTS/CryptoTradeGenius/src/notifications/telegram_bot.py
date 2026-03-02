"""
Telegram Bot for Trade Alerts and Notifications
Sends real-time alerts for trades, risk events, and performance reports
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    CallbackQueryHandler, MessageHandler, filters
)

from config.settings import settings
from src.core.database import Trade, get_session


class TelegramNotifier:
    """Telegram bot for trading notifications"""
    
    def __init__(self):
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.admin_ids = settings.telegram_admin_ids
        self.application: Optional[Application] = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize Telegram bot"""
        if not self.bot_token:
            logger.warning("Telegram bot token not configured")
            return
        
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self._cmd_start))
            self.application.add_handler(CommandHandler("status", self._cmd_status))
            self.application.add_handler(CommandHandler("portfolio", self._cmd_portfolio))
            self.application.add_handler(CommandHandler("trades", self._cmd_trades))
            self.application.add_handler(CommandHandler("pnl", self._cmd_pnl))
            self.application.add_handler(CommandHandler("risk", self._cmd_risk))
            self.application.add_handler(CommandHandler("stopbot", self._cmd_stop))
            self.application.add_handler(CommandHandler("help", self._cmd_help))
            
            # Callback query handler for buttons
            self.application.add_handler(CallbackQueryHandler(self._handle_callback))
            
            # Start the bot
            await self.application.initialize()
            await self.application.start()
            
            # Start polling in background
            asyncio.create_task(self.application.updater.start_polling())
            
            self.is_running = True
            logger.info("🤖 Telegram Bot initialized and running")
            
            # Send startup message
            await self.send_startup_message()
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
    
    async def send_startup_message(self):
        """Send bot startup notification"""
        mode = "📝 PAPER TRADING" if settings.is_paper_trading else "🔴 LIVE TRADING"
        
        message = f"""
🚀 <b>CryptoTradeGenius Bot Started</b>

{mode} Mode
━━━━━━━━━━━━━━━
📊 Max Risk/Trade: {settings.max_risk_per_trade}%
🛑 Max Daily Loss: {settings.max_daily_loss}%
📈 Max Positions: {settings.max_open_positions}
🤖 AI Threshold: {settings.ai_prediction_threshold:.0%}

Use /help for available commands
        """
        await self.send_message(message)
    
    async def send_message(self, message: str, parse_mode: str = "HTML"):
        """Send message to configured chat"""
        if not self.application or not self.chat_id:
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    async def send_trade_alert(self, trade: Dict[str, Any], pnl: Optional[float] = None):
        """Send trade execution alert"""
        side_emoji = "🟢" if trade.get("side") == "buy" else "🔴"
        
        if pnl is not None:
            # Closed position
            pnl_emoji = "🟢" if pnl > 0 else "🔴"
            message = f"""
{side_emoji} <b>Trade Closed</b>

Symbol: {trade.get('symbol')}
Side: {trade.get('side').upper()}
Entry: ${trade.get('entry_price'):,.2f}
Exit: ${trade.get('exit_price'):,.2f}

{pnl_emoji} P&L: ${pnl:,.2f} ({trade.get('pnl_percent', 0):.2f}%)

Risk: {trade.get('risk_percent', 0):.2f}%
Strategy: {trade.get('strategy', 'AI')}
            """
        else:
            # New position
            message = f"""
{side_emoji} <b>New Trade Opened</b>

Symbol: {trade.get('symbol')}
Side: {trade.get('side').upper()}
Entry: ${trade.get('entry_price'):,.2f}
Quantity: {trade.get('quantity', 0):.6f}

🛑 Stop Loss: ${trade.get('stop_loss', 0):,.2f}
🎯 Take Profit: ${trade.get('take_profit', 0):,.2f}

Risk: {trade.get('risk_percent', 0):.2f}%
AI Confidence: {trade.get('ai_confidence', 0):.0%}
Strategy: {trade.get('strategy', 'AI')}
            """
        
        await self.send_message(message)
    
    async def send_risk_alert(self, event_type: str, severity: str, description: str):
        """Send risk management alert"""
        emoji_map = {
            "low": "⚠️",
            "medium": "🚨",
            "high": "⛔",
            "critical": "☠️"
        }
        emoji = emoji_map.get(severity, "⚠️")
        
        message = f"""
{emoji} <b>RISK ALERT - {severity.upper()}</b>

Event: {event_type}
Description: {description}

Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
        """
        
        await self.send_message(message)
    
    async def send_daily_report(self, report: Dict[str, Any]):
        """Send daily performance report"""
        total_pnl = report.get('total_pnl', 0)
        pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
        
        message = f"""
📊 <b>Daily Performance Report</b>
{datetime.utcnow().strftime('%Y-%m-%d')}
━━━━━━━━━━━━━━━

{pnl_emoji} Total P&L: ${total_pnl:,.2f}
📈 Win Rate: {report.get('win_rate', 0):.1f}%
🔄 Total Trades: {report.get('total_trades', 0)}
✅ Winning: {report.get('winning_trades', 0)}
❌ Losing: {report.get('losing_trades', 0)}

💰 Portfolio Value: ${report.get('portfolio_value', 0):,.2f}
📉 Max Drawdown: {report.get('max_drawdown', 0):.2f}%
        """
        
        await self.send_message(message)
    
    # Command Handlers
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🚀 Welcome to CryptoTradeGenius!\n\n"
            "I'm your AI-powered crypto trading assistant.\n"
            "Use /help to see available commands."
        )
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        mode = "📝 Paper Trading" if settings.is_paper_trading else "🔴 LIVE TRADING"
        
        keyboard = [
            [InlineKeyboardButton("📊 Portfolio", callback_data="portfolio")],
            [InlineKeyboardButton("📈 Open Trades", callback_data="trades")],
            [InlineKeyboardButton("⚠️ Risk Status", callback_data="risk")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🤖 <b>Bot Status</b>\n\n"
            f"Mode: {mode}\n"
            f"Trading: {'✅ Active' if True else '🚫 Paused'}\n\n"
            f"Select an option:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
    async def _cmd_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        # Get portfolio data
        from src.portfolio.portfolio_manager import portfolio_manager
        await portfolio_manager.update_portfolio_state()
        summary = portfolio_manager.get_portfolio_summary()
        
        message = f"""
💼 <b>Portfolio Summary</b>

Total Value: ${summary.get('total_value', 0):,.2f}
Available: ${summary.get('available_usd', 0):,.2f}

<b>Allocations:</b>
"""
        for alloc in summary.get('allocations', []):
            emoji = "✅" if not alloc.get('needs_rebalance') else "⚠️"
            message += f"\n{emoji} {alloc['symbol']}: {alloc['current_percent']}% (target: {alloc['target_percent']:.0f}%)"
        
        await update.message.reply_text(message, parse_mode="HTML")
    
    async def _cmd_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        try:
            session = get_session(settings.database_url)
            from sqlalchemy import desc
            from src.core.database import Trade as TradeModel
            
            # Get recent open trades
            open_trades = session.query(TradeModel).filter(
                TradeModel.status == "open"
            ).order_by(desc(TradeModel.opened_at)).all()
            
            # Get recent closed trades
            closed_trades = session.query(TradeModel).filter(
                TradeModel.status == "closed"
            ).order_by(desc(TradeModel.closed_at)).limit(5).all()
            
            message = "📈 <b>Recent Trades</b>\n\n"
            
            if open_trades:
                message += "<b>Open Positions:</b>\n"
                for t in open_trades[:5]:
                    pnl_emoji = "🟢" if t.pnl_absolute >= 0 else "🔴"
                    message += f"{pnl_emoji} {t.symbol} {t.side.upper()} @ ${t.entry_price:,.2f} (P&L: ${t.pnl_absolute:,.2f})\n"
            else:
                message += "No open positions\n"
            
            if closed_trades:
                message += "\n<b>Recently Closed:</b>\n"
                for t in closed_trades:
                    pnl_emoji = "🟢" if t.pnl_absolute >= 0 else "🔴"
                    message += f"{pnl_emoji} {t.symbol} P&L: ${t.pnl_absolute:,.2f} ({t.pnl_percent:.2f}%)\n"
            
            session.close()
            await update.message.reply_text(message, parse_mode="HTML")
            
        except Exception as e:
            await update.message.reply_text(f"Error fetching trades: {e}")
    
    async def _cmd_pnl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl command"""
        try:
            session = get_session(settings.database_url)
            from sqlalchemy import func
            from src.core.database import Trade as TradeModel
            
            # Calculate total P&L
            total_pnl = session.query(func.sum(TradeModel.pnl_absolute)).scalar() or 0
            
            # Calculate today's P&L
            from datetime import datetime, timedelta
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_pnl = session.query(func.sum(TradeModel.pnl_absolute)).filter(
                TradeModel.closed_at >= today
            ).scalar() or 0
            
            # Win rate
            total_trades = session.query(TradeModel).filter(
                TradeModel.status == "closed"
            ).count()
            winning_trades = session.query(TradeModel).filter(
                TradeModel.status == "closed",
                TradeModel.pnl_absolute > 0
            ).count()
            
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            message = f"""
💰 <b>P&L Summary</b>

Total P&L: ${total_pnl:,.2f}
Today's P&L: ${today_pnl:,.2f}

Win Rate: {win_rate:.1f}% ({winning_trades}/{total_trades})
            """
            
            session.close()
            await update.message.reply_text(message, parse_mode="HTML")
            
        except Exception as e:
            await update.message.reply_text(f"Error calculating P&L: {e}")
    
    async def _cmd_risk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /risk command"""
        from src.risk.risk_manager import risk_manager
        report = risk_manager.get_risk_report()
        
        portfolio = report.get('portfolio', {})
        limits = report.get('limits', {})
        
        message = f"""
🛡️ <b>Risk Management Status</b>

Portfolio:
• Equity: ${portfolio.get('total_equity', 0):,.2f}
• Daily P&L: ${portfolio.get('daily_pnl', 0):,.2f}
• Max Drawdown: {portfolio.get('max_drawdown', 0):.2f}%

Limits:
• Risk/Trade: {limits.get('max_risk_per_trade', 0)}%
• Daily Loss: {limits.get('max_daily_loss', 0)}%
• Max Positions: {limits.get('max_open_positions', 0)}

Trading: {'✅ Enabled' if limits.get('trading_enabled') else '🚫 Disabled'}
Emergency Stop: {'⛔ ACTIVE' if limits.get('emergency_stop') else '✅ Inactive'}
        """
        
        await update.message.reply_text(message, parse_mode="HTML")
    
    async def _cmd_stop(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stopbot command (admin only)"""
        user_id = str(update.effective_user.id)
        
        if user_id not in self.admin_ids:
            await update.message.reply_text("⛔ Admin access required")
            return
        
        keyboard = [
            [InlineKeyboardButton("✅ Confirm Stop", callback_data="confirm_stop")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_stop")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ <b>WARNING</b>\n\n"
            "Are you sure you want to stop all trading?\n"
            "All open positions will remain open.",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        message = """
🤖 <b>CryptoTradeGenius Commands</b>

<b>Status Commands:</b>
/status - Bot status
/portfolio - Portfolio overview
/trades - Recent trades
/pnl - Profit/Loss summary
/risk - Risk management status

<b>Control Commands (Admin):</b>
/stopbot - Emergency stop trading

Use the buttons for quick navigation!
        """
        await update.message.reply_text(message, parse_mode="HTML")
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "portfolio":
            await self._cmd_portfolio(update, context)
        elif query.data == "trades":
            await self._cmd_trades(update, context)
        elif query.data == "risk":
            await self._cmd_risk(update, context)
        elif query.data == "confirm_stop":
            from src.risk.risk_manager import risk_manager
            risk_manager.disable_trading()
            await query.edit_message_text("🚫 Trading stopped by user command")
        elif query.data == "cancel_stop":
            await query.edit_message_text("✅ Stop command cancelled")
    
    async def stop(self):
        """Stop the bot"""
        if self.application:
            await self.application.stop()
            await self.application.shutdown()
            self.is_running = False
            logger.info("Telegram Bot stopped")


# Global Telegram notifier instance
telegram_notifier = TelegramNotifier()
