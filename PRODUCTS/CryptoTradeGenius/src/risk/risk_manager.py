"""
Risk Management System - Institutional-grade risk controls
Never lose more than 2% per trade, with portfolio-level safeguards
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from loguru import logger
import numpy as np

from config.settings import settings
from src.core.database import RiskEvent, get_session


@dataclass
class PositionRisk:
    """Risk metrics for an individual position"""
    symbol: str
    entry_price: float
    current_price: float
    quantity: float
    stop_loss: float
    take_profit: float
    
    @property
    def position_value(self) -> float:
        return self.quantity * self.current_price
    
    @property
    def unrealized_pnl(self) -> float:
        return self.quantity * (self.current_price - self.entry_price)
    
    @property
    def unrealized_pnl_percent(self) -> float:
        return (self.current_price / self.entry_price - 1) * 100
    
    @property
    def risk_amount(self) -> float:
        """Maximum loss if stop loss is hit"""
        if self.stop_loss > 0:
            return abs(self.entry_price - self.stop_loss) * self.quantity
        return self.position_value * 0.02  # Assume 2% risk if no stop
    
    @property
    def risk_percent(self) -> float:
        """Risk as percentage of position value"""
        if self.position_value > 0:
            return (self.risk_amount / self.position_value) * 100
        return 0


@dataclass
class PortfolioRisk:
    """Portfolio-level risk metrics"""
    total_equity: float = 0
    available_balance: float = 0
    allocated_balance: float = 0
    open_positions: int = 0
    
    daily_pnl: float = 0
    daily_pnl_percent: float = 0
    
    max_drawdown: float = 0
    current_drawdown: float = 0
    peak_equity: float = 0
    
    var_95: float = 0  # Value at Risk (95% confidence)
    portfolio_volatility: float = 0
    
    risk_events: List[Dict] = field(default_factory=list)


class RiskManager:
    """Centralized risk management system"""
    
    def __init__(self):
        self.daily_stats = {
            "date": datetime.utcnow().date(),
            "starting_equity": 0,
            "current_equity": 0,
            "total_pnl": 0,
            "trades_today": 0,
            "risk_events": []
        }
        self.position_risks: Dict[str, PositionRisk] = {}
        self.portfolio_risk = PortfolioRisk()
        self.trading_enabled = True
        self.emergency_stop = False
        
    async def initialize(self):
        """Initialize risk manager"""
        logger.info("🛡️ Risk Manager initialized")
        logger.info(f"   Max risk per trade: {settings.max_risk_per_trade}%")
        logger.info(f"   Max daily loss: {settings.max_daily_loss}%")
        logger.info(f"   Max open positions: {settings.max_open_positions}")
    
    def can_open_position(self, symbol: str, position_value: float, 
                          portfolio_value: float) -> Tuple[bool, str]:
        """
        Check if new position can be opened
        Returns (allowed, reason)
        """
        if self.emergency_stop:
            return False, "EMERGENCY STOP ACTIVE - Trading halted"
        
        if not self.trading_enabled:
            return False, "Trading manually disabled"
        
        # Check max positions
        if len(self.position_risks) >= settings.max_open_positions:
            return False, f"Max positions reached ({settings.max_open_positions})"
        
        # Check daily loss limit
        if self.daily_stats["total_pnl"] < 0:
            daily_loss_percent = abs(self.daily_stats["total_pnl"]) / self.daily_stats["starting_equity"] * 100
            if daily_loss_percent >= settings.max_daily_loss:
                self._trigger_risk_event("max_daily_loss", "high", 
                    f"Daily loss limit ({settings.max_daily_loss}%) reached")
                return False, f"Daily loss limit ({settings.max_daily_loss}%) reached"
        
        # Check position sizing (max 10% per position)
        max_position_size = portfolio_value * 0.10
        if position_value > max_position_size:
            return False, f"Position size exceeds 10% of portfolio (${max_position_size:.2f})"
        
        # Check if symbol already has open position
        if symbol in self.position_risks:
            return False, f"Position already open for {symbol}"
        
        return True, "OK"
    
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                                portfolio_value: float) -> Tuple[float, float]:
        """
        Calculate optimal position size based on risk
        Returns (quantity, risk_percent)
        """
        if stop_loss <= 0 or entry_price <= 0:
            return 0, 0
        
        # Risk per trade in USD
        risk_amount = portfolio_value * (settings.max_risk_per_trade / 100)
        
        # Distance to stop loss
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0, 0
        
        # Calculate quantity
        quantity = risk_amount / price_risk
        position_value = quantity * entry_price
        
        # Limit by max order size
        max_order_value = min(settings.max_order_size, portfolio_value * 0.10)
        if position_value > max_order_value:
            quantity = max_order_value / entry_price
            position_value = max_order_value
            risk_amount = quantity * price_risk
        
        # Limit by min order size
        min_value = quantity * entry_price
        if min_value < settings.min_order_size:
            quantity = settings.min_order_size / entry_price
        
        risk_percent = (risk_amount / portfolio_value) * 100
        
        return quantity, risk_percent
    
    def calculate_stop_loss(self, entry_price: float, side: str, 
                           atr: Optional[float] = None,
                           method: str = "percent") -> float:
        """
        Calculate optimal stop loss price
        Methods: percent, atr, support_resistance
        """
        if method == "percent":
            stop_percent = settings.default_stop_loss / 100
            if side == "buy":
                return entry_price * (1 - stop_percent)
            else:  # sell/short
                return entry_price * (1 + stop_percent)
        
        elif method == "atr" and atr:
            # 2x ATR stop
            if side == "buy":
                return entry_price - (2 * atr)
            else:
                return entry_price + (2 * atr)
        
        return entry_price * (1 - settings.default_stop_loss / 100)
    
    def calculate_take_profit(self, entry_price: float, stop_loss: float, 
                              side: str, risk_reward: float = 2.0) -> float:
        """
        Calculate take profit based on risk:reward ratio
        Default 1:2 risk reward (risk $1 to make $2)
        """
        stop_distance = abs(entry_price - stop_loss)
        profit_distance = stop_distance * risk_reward
        
        if side == "buy":
            return entry_price + profit_distance
        else:
            return entry_price - profit_distance
    
    def update_position_risk(self, symbol: str, entry_price: float, 
                            current_price: float, quantity: float,
                            stop_loss: float, take_profit: float):
        """Update risk tracking for a position"""
        self.position_risks[symbol] = PositionRisk(
            symbol=symbol,
            entry_price=entry_price,
            current_price=current_price,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    def remove_position_risk(self, symbol: str):
        """Remove position from risk tracking"""
        if symbol in self.position_risks:
            del self.position_risks[symbol]
    
    def check_position_limits(self, symbol: str, current_price: float) -> Optional[str]:
        """
        Check if position hit stop loss or take profit
        Returns: 'stop_loss', 'take_profit', or None
        """
        if symbol not in self.position_risks:
            return None
        
        position = self.position_risks[symbol]
        position.current_price = current_price
        
        # Assume long position for now
        if current_price <= position.stop_loss:
            logger.warning(f"🛑 Stop loss triggered for {symbol} @ {current_price}")
            return "stop_loss"
        
        if current_price >= position.take_profit:
            logger.info(f"🎯 Take profit triggered for {symbol} @ {current_price}")
            return "take_profit"
        
        return None
    
    def update_portfolio_risk(self, equity: float, positions: Dict):
        """Update portfolio-level risk metrics"""
        self.portfolio_risk.total_equity = equity
        
        # Track peak equity and drawdown
        if equity > self.portfolio_risk.peak_equity:
            self.portfolio_risk.peak_equity = equity
        
        if self.portfolio_risk.peak_equity > 0:
            self.portfolio_risk.current_drawdown = (
                (self.portfolio_risk.peak_equity - equity) / self.portfolio_risk.peak_equity
            ) * 100
        
        if self.portfolio_risk.current_drawdown > self.portfolio_risk.max_drawdown:
            self.portfolio_risk.max_drawdown = self.portfolio_risk.current_drawdown
        
        # Check max drawdown limit
        if self.portfolio_risk.max_drawdown > 20:  # 20% max drawdown
            self._trigger_risk_event("max_drawdown", "critical",
                f"Maximum drawdown ({self.portfolio_risk.max_drawdown:.2f}%) exceeded")
            self.emergency_stop = True
        
        # Daily P&L tracking
        if self.daily_stats["starting_equity"] == 0:
            self.daily_stats["starting_equity"] = equity
        
        self.daily_stats["current_equity"] = equity
        self.daily_stats["total_pnl"] = equity - self.daily_stats["starting_equity"]
    
    def _trigger_risk_event(self, event_type: str, severity: str, description: str):
        """Log a risk management event"""
        event = {
            "timestamp": datetime.utcnow(),
            "type": event_type,
            "severity": severity,
            "description": description
        }
        self.daily_stats["risk_events"].append(event)
        self.portfolio_risk.risk_events.append(event)
        
        logger.warning(f"⚠️ RISK EVENT [{severity.upper()}]: {description}")
        
        # Persist to database
        try:
            session = get_session(settings.database_url)
            risk_event = RiskEvent(
                event_type=event_type,
                severity=severity,
                description=description
            )
            session.add(risk_event)
            session.commit()
            session.close()
        except Exception as e:
            logger.error(f"Failed to log risk event: {e}")
    
    def get_risk_report(self) -> Dict:
        """Generate comprehensive risk report"""
        total_risk = sum(p.risk_amount for p in self.position_risks.values())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "portfolio": {
                "total_equity": self.portfolio_risk.total_equity,
                "available_balance": self.portfolio_risk.available_balance,
                "max_drawdown": self.portfolio_risk.max_drawdown,
                "current_drawdown": self.portfolio_risk.current_drawdown,
                "daily_pnl": self.daily_stats["total_pnl"],
                "daily_pnl_percent": (
                    self.daily_stats["total_pnl"] / self.daily_stats["starting_equity"] * 100
                    if self.daily_stats["starting_equity"] > 0 else 0
                ),
            },
            "positions": {
                "open_count": len(self.position_risks),
                "total_risk_amount": total_risk,
                "total_risk_percent": (
                    (total_risk / self.portfolio_risk.total_equity) * 100
                    if self.portfolio_risk.total_equity > 0 else 0
                ),
            },
            "limits": {
                "max_risk_per_trade": settings.max_risk_per_trade,
                "max_daily_loss": settings.max_daily_loss,
                "max_open_positions": settings.max_open_positions,
                "trading_enabled": self.trading_enabled,
                "emergency_stop": self.emergency_stop,
            },
            "risk_events_today": len(self.daily_stats["risk_events"]),
        }
    
    def reset_daily_stats(self):
        """Reset daily statistics (call at midnight UTC)"""
        logger.info("🔄 Resetting daily risk statistics")
        self.daily_stats = {
            "date": datetime.utcnow().date(),
            "starting_equity": self.portfolio_risk.total_equity,
            "current_equity": self.portfolio_risk.total_equity,
            "total_pnl": 0,
            "trades_today": 0,
            "risk_events": []
        }
    
    def enable_trading(self):
        """Re-enable trading"""
        self.trading_enabled = True
        self.emergency_stop = False
        logger.info("✅ Trading re-enabled")
    
    def disable_trading(self):
        """Disable trading"""
        self.trading_enabled = False
        logger.info("🚫 Trading disabled")


# Global risk manager instance
risk_manager = RiskManager()
