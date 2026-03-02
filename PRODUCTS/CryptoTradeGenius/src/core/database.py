"""
Database models and connection management
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import json

Base = declarative_base()


class Trade(Base):
    """Trade execution records"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String(50), unique=True, index=True)
    symbol = Column(String(20), index=True)
    side = Column(String(10))  # buy/sell
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    order_type = Column(String(20))  # market/limit/stop
    status = Column(String(20), default="open")  # open/closed/cancelled
    
    # Risk management
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    risk_percent = Column(Float)
    
    # P&L tracking
    pnl_absolute = Column(Float, default=0)
    pnl_percent = Column(Float, default=0)
    fees = Column(Float, default=0)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Metadata
    exchange = Column(String(20))
    strategy = Column(String(50))
    ai_confidence = Column(Float, nullable=True)
    signal_data = Column(JSON)
    notes = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "order_type": self.order_type,
            "status": self.status,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_percent": self.risk_percent,
            "pnl_absolute": self.pnl_absolute,
            "pnl_percent": self.pnl_percent,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "exchange": self.exchange,
            "strategy": self.strategy,
            "ai_confidence": self.ai_confidence,
        }


class Balance(Base):
    """Portfolio balance snapshots"""
    __tablename__ = "balances"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    total_usd = Column(Float)
    available_usd = Column(Float)
    allocated_usd = Column(Float)
    
    # Asset breakdown stored as JSON
    assets = Column(JSON)
    
    # Metrics
    daily_pnl = Column(Float)
    daily_pnl_percent = Column(Float)
    total_pnl = Column(Float)
    total_pnl_percent = Column(Float)
    
    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "total_usd": self.total_usd,
            "available_usd": self.available_usd,
            "allocated_usd": self.allocated_usd,
            "assets": self.assets,
            "daily_pnl": self.daily_pnl,
            "daily_pnl_percent": self.daily_pnl_percent,
            "total_pnl": self.total_pnl,
            "total_pnl_percent": self.total_pnl_percent,
        }


class Signal(Base):
    """AI trading signals"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True)
    signal_id = Column(String(50), unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    symbol = Column(String(20), index=True)
    signal_type = Column(String(10))  # buy/sell/hold
    confidence = Column(Float)
    timeframe = Column(String(10))
    
    # Technical indicators
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    macd_signal = Column(Float, nullable=True)
    bb_upper = Column(Float, nullable=True)
    bb_lower = Column(Float, nullable=True)
    ema_20 = Column(Float, nullable=True)
    ema_50 = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    
    # Price data
    current_price = Column(Float)
    predicted_price = Column(Float, nullable=True)
    prediction_horizon = Column(Integer, nullable=True)  # hours
    
    # Execution
    executed = Column(Boolean, default=False)
    trade_id = Column(String(50), nullable=True)
    
    # Model metadata
    model_version = Column(String(20))
    features_used = Column(JSON)
    
    def to_dict(self):
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "symbol": self.symbol,
            "signal_type": self.signal_type,
            "confidence": self.confidence,
            "timeframe": self.timeframe,
            "rsi": self.rsi,
            "macd": self.macd,
            "current_price": self.current_price,
            "predicted_price": self.predicted_price,
            "executed": self.executed,
            "model_version": self.model_version,
        }


class RiskEvent(Base):
    """Risk management events and alerts"""
    __tablename__ = "risk_events"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String(50))  # stop_loss_triggered, max_drawdown, etc.
    severity = Column(String(20))  # low/medium/high/critical
    
    symbol = Column(String(20), nullable=True)
    trade_id = Column(String(50), nullable=True)
    
    description = Column(Text)
    action_taken = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)


class PerformanceMetrics(Base):
    """Daily/weekly performance metrics"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    
    # Trade statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0)
    
    # P&L
    gross_profit = Column(Float, default=0)
    gross_loss = Column(Float, default=0)
    net_pnl = Column(Float, default=0)
    
    # Risk metrics
    max_drawdown = Column(Float, default=0)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    
    # Per symbol performance
    symbol_performance = Column(JSON)


def init_database(database_url: str):
    """Initialize database with all tables"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(database_url: str):
    """Get database session"""
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    return Session()
