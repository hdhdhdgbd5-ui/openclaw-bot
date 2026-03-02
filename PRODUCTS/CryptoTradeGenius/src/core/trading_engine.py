"""
Trading Engine - Main orchestrator for the Crypto Trading Bot
Coordinates AI predictions, risk management, portfolio management, and execution
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import schedule

from config.settings import settings
from src.exchanges.exchange_manager import exchange_manager, OrderSide, OrderType
from src.ai.prediction_engine import ai_engine, PredictionResult
from src.risk.risk_manager import risk_manager
from src.portfolio.portfolio_manager import portfolio_manager
from src.notifications.telegram_bot import telegram_notifier
from src.core.database import Trade, Signal, get_session, init_database


class TradingEngine:
    """Main trading bot orchestrator"""
    
    def __init__(self):
        self.is_running = False
        self.trading_pairs = [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "ADA/USDT",
            "DOT/USDT",
            "LINK/USDT",
            "MATIC/USDT",
            "UNI/USDT"
        ]
        self.active_positions: Dict[str, Dict] = {}
        self.last_analysis: Dict[str, datetime] = {}
        self.analysis_interval = timedelta(minutes=15)  # Analyze every 15 minutes
        
    async def initialize(self):
        """Initialize all trading components"""
        logger.info("🚀 Initializing CryptoTradeGenius Trading Engine...")
        
        # Initialize database
        init_database(settings.database_url)
        logger.info("✅ Database initialized")
        
        # Initialize exchanges
        await exchange_manager.initialize()
        logger.info("✅ Exchange manager ready")
        
        # Initialize AI engine
        await ai_engine.initialize()
        logger.info("✅ AI engine ready")
        
        # Initialize risk manager
        await risk_manager.initialize()
        logger.info("✅ Risk manager ready")
        
        # Initialize portfolio manager
        await portfolio_manager.initialize()
        logger.info("✅ Portfolio manager ready")
        
        # Initialize Telegram notifications
        await telegram_notifier.initialize()
        logger.info("✅ Telegram notifier ready")
        
        logger.info("🎯 Trading Engine fully initialized and ready!")
        
    async def start(self):
        """Start the trading engine"""
        if self.is_running:
            logger.warning("Trading engine already running")
            return
        
        self.is_running = True
        logger.info("▶️ Trading engine started")
        
        # Schedule tasks
        schedule.every(15).minutes.do(lambda: asyncio.create_task(self._analyze_markets()))
        schedule.every(1).minutes.do(lambda: asyncio.create_task(self._check_positions()))
        schedule.every(settings.rebalance_interval).hours.do(lambda: asyncio.create_task(self._rebalance_portfolio()))
        schedule.every().day.at("00:00").do(lambda: asyncio.create_task(self._daily_report()))
        
        # Initial analysis
        await self._analyze_markets()
        
        # Main loop
        while self.is_running:
            schedule.run_pending()
            await asyncio.sleep(1)
    
    def stop(self):
        """Stop the trading engine"""
        self.is_running = False
        logger.info("⏹️ Trading engine stopped")
    
    async def _analyze_markets(self):
        """Analyze all trading pairs for signals"""
        logger.info("🔍 Analyzing markets...")
        
        for symbol in self.trading_pairs:
            try:
                # Check if we already have a position
                if symbol in self.active_positions:
                    continue
                
                # Check last analysis time
                last_time = self.last_analysis.get(symbol)
                if last_time and (datetime.utcnow() - last_time) < self.analysis_interval:
                    continue
                
                # Get market data
                ohlcv = await exchange_manager.get_ohlcv(symbol, "1h", limit=100)
                if not ohlcv or len(ohlcv) < 50:
                    continue
                
                # Get AI prediction
                prediction = await ai_engine.predict(symbol, ohlcv)
                if not prediction:
                    continue
                
                self.last_analysis[symbol] = datetime.utcnow()
                
                # Store signal in database
                await self._store_signal(symbol, prediction, ohlcv[-1][4])  # Close price
                
                # Execute if signal is strong
                if prediction.signal in ['buy', 'sell'] and prediction.confidence >= settings.ai_prediction_threshold:
                    await self._execute_signal(symbol, prediction, ohlcv)
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
    
    async def _store_signal(self, symbol: str, prediction: PredictionResult, current_price: float):
        """Store AI signal in database"""
        try:
            session = get_session(settings.database_url)
            
            signal = Signal(
                signal_id=f"{symbol}_{int(datetime.utcnow().timestamp())}",
                symbol=symbol,
                signal_type=prediction.signal,
                confidence=prediction.confidence,
                timeframe="1h",
                current_price=current_price,
                predicted_price=prediction.predicted_price,
                model_version="1.0.0",
                features_used=prediction.features_used
            )
            
            session.add(signal)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error storing signal: {e}")
    
    async def _execute_signal(self, symbol: str, prediction: PredictionResult, ohlcv: List):
        """Execute trade based on AI signal"""
        try:
            current_price = ohlcv[-1][4]  # Close price
            
            # Get portfolio value
            await portfolio_manager.update_portfolio_state()
            portfolio_value = portfolio_manager.current_state.total_value if portfolio_manager.current_state else 10000
            
            # Check risk limits
            can_trade, reason = risk_manager.can_open_position(symbol, 0, portfolio_value)
            if not can_trade:
                logger.info(f"Cannot trade {symbol}: {reason}")
                return
            
            # Calculate stop loss and take profit
            side = OrderSide.BUY if prediction.signal == 'buy' else OrderSide.SELL
            
            stop_loss = risk_manager.calculate_stop_loss(
                current_price, prediction.signal
            )
            take_profit = risk_manager.calculate_take_profit(
                current_price, stop_loss, prediction.signal
            )
            
            # Calculate position size
            quantity, risk_percent = risk_manager.calculate_position_size(
                current_price, stop_loss, portfolio_value
            )
            
            if quantity <= 0:
                logger.warning(f"Invalid position size for {symbol}")
                return
            
            # Execute order
            order = await exchange_manager.create_order(
                symbol=symbol,
                side=side,
                order_type=OrderType.MARKET,
                quantity=quantity
            )
            
            if not order:
                logger.error(f"Failed to execute order for {symbol}")
                return
            
            # Store in database
            trade_id = f"{symbol}_{int(datetime.utcnow().timestamp())}"
            
            session = get_session(settings.database_url)
            trade = Trade(
                trade_id=trade_id,
                symbol=symbol,
                side=prediction.signal,
                entry_price=order.price,
                quantity=quantity,
                order_type="market",
                status="open",
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_percent=risk_percent,
                exchange="binance",  # Default exchange
                strategy="AI_Ensemble",
                ai_confidence=prediction.confidence,
                signal_data={
                    "prediction": prediction.signal,
                    "confidence": prediction.confidence,
                    "features": prediction.features_used
                }
            )
            session.add(trade)
            session.commit()
            session.close()
            
            # Track position
            self.active_positions[symbol] = {
                "trade_id": trade_id,
                "entry_price": order.price,
                "quantity": quantity,
                "side": prediction.signal,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "entry_time": datetime.utcnow()
            }
            
            # Update risk manager
            risk_manager.update_position_risk(
                symbol, order.price, order.price, quantity, stop_loss, take_profit
            )
            
            # Send notification
            await telegram_notifier.send_trade_alert({
                "symbol": symbol,
                "side": prediction.signal,
                "entry_price": order.price,
                "quantity": quantity,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "risk_percent": risk_percent,
                "ai_confidence": prediction.confidence,
                "strategy": "AI_Ensemble"
            })
            
            logger.info(f"✅ Executed {prediction.signal.upper()} {symbol}: {quantity:.6f} @ ${order.price:.2f}")
            
        except Exception as e:
            logger.error(f"Error executing signal for {symbol}: {e}")
    
    async def _check_positions(self):
        """Check and manage open positions"""
        for symbol in list(self.active_positions.keys()):
            try:
                position = self.active_positions[symbol]
                
                # Get current price
                ticker = await exchange_manager.get_ticker(symbol)
                if not ticker:
                    continue
                
                current_price = ticker.last
                
                # Update risk tracking
                risk_manager.update_position_risk(
                    symbol,
                    position["entry_price"],
                    current_price,
                    position["quantity"],
                    position["stop_loss"],
                    position["take_profit"]
                )
                
                # Check exit conditions
                exit_signal = risk_manager.check_position_limits(symbol, current_price)
                
                if exit_signal:
                    await self._close_position(symbol, current_price, exit_signal)
                    
            except Exception as e:
                logger.error(f"Error checking position {symbol}: {e}")
    
    async def _close_position(self, symbol: str, exit_price: float, reason: str):
        """Close an open position"""
        try:
            if symbol not in self.active_positions:
                return
            
            position = self.active_positions[symbol]
            
            # Determine side for closing
            close_side = OrderSide.SELL if position["side"] == "buy" else OrderSide.BUY
            
            # Execute close order
            order = await exchange_manager.create_order(
                symbol=symbol,
                side=close_side,
                order_type=OrderType.MARKET,
                quantity=position["quantity"]
            )
            
            # Calculate P&L
            if position["side"] == "buy":
                pnl = position["quantity"] * (exit_price - position["entry_price"])
            else:
                pnl = position["quantity"] * (position["entry_price"] - exit_price)
            
            pnl_percent = (pnl / (position["quantity"] * position["entry_price"])) * 100
            
            # Update database
            session = get_session(settings.database_url)
            trade = session.query(Trade).filter_by(trade_id=position["trade_id"]).first()
            if trade:
                trade.status = "closed"
                trade.exit_price = exit_price
                trade.closed_at = datetime.utcnow()
                trade.pnl_absolute = pnl
                trade.pnl_percent = pnl_percent
                session.commit()
            session.close()
            
            # Remove from tracking
            del self.active_positions[symbol]
            risk_manager.remove_position_risk(symbol)
            
            # Send notification
            await telegram_notifier.send_trade_alert({
                "symbol": symbol,
                "side": position["side"],
                "entry_price": position["entry_price"],
                "exit_price": exit_price,
                "quantity": position["quantity"],
                "pnl_percent": pnl_percent,
                "strategy": "AI_Ensemble"
            }, pnl=pnl)
            
            emoji = "🟢" if pnl >= 0 else "🔴"
            logger.info(f"{emoji} Closed {symbol}: ${pnl:.2f} ({reason})")
            
        except Exception as e:
            logger.error(f"Error closing position {symbol}: {e}")
    
    async def _rebalance_portfolio(self):
        """Execute portfolio rebalancing"""
        logger.info("🔄 Checking portfolio rebalancing...")
        trades = await portfolio_manager.check_and_rebalance()
        if trades:
            logger.info(f"Rebalancing executed: {len(trades)} trades")
    
    async def _daily_report(self):
        """Generate and send daily report"""
        try:
            session = get_session(settings.database_url)
            from sqlalchemy import func
            from datetime import date
            
            today = date.today()
            
            # Get today's trades
            trades_today = session.query(Trade).filter(
                Trade.status == "closed",
                func.date(Trade.closed_at) == today
            ).all()
            
            total_pnl = sum(t.pnl_absolute for t in trades_today)
            winning = sum(1 for t in trades_today if t.pnl_absolute > 0)
            losing = len(trades_today) - winning
            win_rate = (winning / len(trades_today) * 100) if trades_today else 0
            
            # Get portfolio value
            await portfolio_manager.update_portfolio_state()
            portfolio_value = portfolio_manager.current_state.total_value if portfolio_manager.current_state else 0
            
            report = {
                "total_pnl": total_pnl,
                "total_trades": len(trades_today),
                "winning_trades": winning,
                "losing_trades": losing,
                "win_rate": win_rate,
                "portfolio_value": portfolio_value,
                "max_drawdown": risk_manager.portfolio_risk.max_drawdown
            }
            
            await telegram_notifier.send_daily_report(report)
            
            # Reset daily stats
            risk_manager.reset_daily_stats()
            
            session.close()
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    def get_status(self) -> Dict:
        """Get current engine status"""
        return {
            "is_running": self.is_running,
            "trading_mode": settings.trading_mode,
            "active_positions": len(self.active_positions),
            "open_positions_detail": self.active_positions,
            "portfolio_summary": portfolio_manager.get_portfolio_summary() if portfolio_manager.current_state else None,
            "risk_report": risk_manager.get_risk_report(),
        }


# Global trading engine instance
trading_engine = TradingEngine()
