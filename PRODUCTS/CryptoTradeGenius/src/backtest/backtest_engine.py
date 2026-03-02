"""
Backtesting Engine - Test strategies against historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from loguru import logger
import json

from config.settings import settings
from src.ai.prediction_engine import ai_engine, PredictionResult
from src.risk.risk_manager import risk_manager
from src.exchanges.exchange_manager import OrderSide, OrderType


@dataclass
class BacktestTrade:
    """Simulated trade record"""
    entry_time: datetime
    exit_time: Optional[datetime]
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    exit_reason: str  # stop_loss, take_profit, signal_reverse, end_of_data


@dataclass
class BacktestResult:
    """Backtest performance results"""
    # Basic stats
    start_date: datetime
    end_date: datetime
    initial_balance: float
    final_balance: float
    total_return: float
    total_return_percent: float
    
    # Trade stats
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_trade: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    
    # Risk metrics
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    
    # Monthly returns
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    
    # Trade history
    trades: List[BacktestTrade] = field(default_factory=list)
    equity_curve: List[Tuple[datetime, float]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "period": f"{self.start_date.date()} to {self.end_date.date()}",
            "initial_balance": round(self.initial_balance, 2),
            "final_balance": round(self.final_balance, 2),
            "total_return": round(self.total_return, 2),
            "total_return_percent": round(self.total_return_percent, 2),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": round(self.win_rate, 2),
            "profit_factor": round(self.profit_factor, 2),
            "max_drawdown": round(self.max_drawdown, 2),
            "max_drawdown_percent": round(self.max_drawdown_percent, 2),
            "sharpe_ratio": round(self.sharpe_ratio, 2) if self.sharpe_ratio else None,
            "avg_trade": round(self.avg_trade, 2),
            "avg_win": round(self.avg_win, 2),
            "avg_loss": round(self.avg_loss, 2),
        }


class BacktestEngine:
    """Backtesting engine for strategy validation"""
    
    def __init__(self):
        self.initial_balance = 10000.0
        self.balance = self.initial_balance
        self.positions: Dict[str, Dict] = {}
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []
        self.current_time: Optional[datetime] = None
        
    def reset(self):
        """Reset backtest state"""
        self.balance = self.initial_balance
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.current_time = None
        
    def run_backtest(
        self,
        data: Dict[str, pd.DataFrame],
        strategy_func: Callable,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        initial_balance: float = 10000.0
    ) -> BacktestResult:
        """
        Run backtest on historical data
        
        Args:
            data: Dict of symbol -> OHLCV DataFrame
            strategy_func: Function that takes (symbol, data) and returns signal
            start_date: Backtest start date
            end_date: Backtest end date
            initial_balance: Starting balance
        """
        logger.info(f"🔬 Starting backtest with ${initial_balance:,.2f}")
        
        self.reset()
        self.initial_balance = initial_balance
        self.balance = initial_balance
        
        # Get common date range
        all_dates = set()
        for df in data.values():
            all_dates.update(df.index)
        
        dates = sorted(all_dates)
        if start_date:
            dates = [d for d in dates if d >= start_date]
        if end_date:
            dates = [d for d in dates if d <= end_date]
        
        if not dates:
            logger.error("No data in specified date range")
            return self._generate_empty_result()
        
        # Run simulation
        for i, current_time in enumerate(dates):
            self.current_time = current_time
            
            # Update positions with current prices
            self._update_positions(data, current_time)
            
            # Check stop losses and take profits
            self._check_exit_conditions(data, current_time)
            
            # Get signals and execute trades
            for symbol, df in data.items():
                if current_time not in df.index:
                    continue
                
                # Get data up to current time
                hist_data = df.loc[:current_time]
                if len(hist_data) < 50:  # Need minimum history
                    continue
                
                # Get signal from strategy
                signal = strategy_func(symbol, hist_data)
                
                if signal and signal.signal in ['buy', 'sell']:
                    self._execute_signal(symbol, signal, hist_data, current_time)
            
            # Record equity
            equity = self._calculate_equity(data, current_time)
            self.equity_curve.append((current_time, equity))
            
            # Progress logging
            if i % 100 == 0:
                logger.debug(f"Backtest progress: {i}/{len(dates)} bars")
        
        # Close all remaining positions at end
        self._close_all_positions(data, dates[-1])
        
        # Generate results
        return self._generate_result(dates[0], dates[-1])
    
    def _update_positions(self, data: Dict[str, pd.DataFrame], current_time: datetime):
        """Update position values with current prices"""
        for symbol, position in self.positions.items():
            if symbol in data and current_time in data[symbol].index:
                position['current_price'] = data[symbol].loc[current_time, 'close']
                position['unrealized_pnl'] = (
                    position['quantity'] * (position['current_price'] - position['entry_price'])
                    if position['side'] == 'buy'
                    else position['quantity'] * (position['entry_price'] - position['current_price'])
                )
    
    def _check_exit_conditions(self, data: Dict[str, pd.DataFrame], current_time: datetime):
        """Check stop loss and take profit conditions"""
        for symbol in list(self.positions.keys()):
            position = self.positions[symbol]
            current_price = position['current_price']
            
            # Check stop loss
            if position['side'] == 'buy' and current_price <= position['stop_loss']:
                self._close_position(symbol, current_price, current_time, 'stop_loss')
            elif position['side'] == 'sell' and current_price >= position['stop_loss']:
                self._close_position(symbol, current_price, current_time, 'stop_loss')
            
            # Check take profit
            elif position['side'] == 'buy' and current_price >= position['take_profit']:
                self._close_position(symbol, current_price, current_time, 'take_profit')
            elif position['side'] == 'sell' and current_price <= position['take_profit']:
                self._close_position(symbol, current_price, current_time, 'take_profit')
    
    def _execute_signal(self, symbol: str, signal: PredictionResult, 
                       hist_data: pd.DataFrame, current_time: datetime):
        """Execute trade based on signal"""
        current_price = hist_data['close'].iloc[-1]
        
        # Check if position already exists
        if symbol in self.positions:
            position = self.positions[symbol]
            
            # Close if signal reverses
            if (position['side'] == 'buy' and signal.signal == 'sell') or \
               (position['side'] == 'sell' and signal.signal == 'buy'):
                self._close_position(symbol, current_price, current_time, 'signal_reverse')
            else:
                return  # Already in position in same direction
        
        # Calculate position size based on risk
        risk_percent = settings.max_risk_per_trade / 100
        risk_amount = self.balance * risk_percent
        
        # Default stop loss distance (2%)
        stop_distance = current_price * 0.02
        
        if signal.signal == 'buy':
            stop_loss = current_price - stop_distance
            take_profit = current_price + (stop_distance * 2)  # 1:2 risk reward
            side = 'buy'
        else:
            stop_loss = current_price + stop_distance
            take_profit = current_price - (stop_distance * 2)
            side = 'sell'
        
        # Calculate quantity
        if stop_distance > 0:
            quantity = risk_amount / stop_distance
        else:
            quantity = (self.balance * 0.02) / current_price  # 2% of balance
        
        # Check balance
        position_value = quantity * current_price
        if position_value > self.balance * 0.95:  # Max 95% of balance
            quantity = (self.balance * 0.95) / current_price
            position_value = quantity * current_price
        
        if position_value < 10:  # Minimum $10 trade
            return
        
        # Open position
        self.positions[symbol] = {
            'side': side,
            'entry_price': current_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'entry_time': current_time,
            'current_price': current_price,
            'unrealized_pnl': 0
        }
        
        logger.debug(f"Opened {side} position: {quantity:.6f} {symbol} @ ${current_price:.2f}")
    
    def _close_position(self, symbol: str, exit_price: float, 
                       exit_time: datetime, reason: str):
        """Close a position"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        
        # Calculate P&L
        if position['side'] == 'buy':
            pnl = position['quantity'] * (exit_price - position['entry_price'])
        else:
            pnl = position['quantity'] * (position['entry_price'] - exit_price)
        
        pnl_percent = (pnl / (position['quantity'] * position['entry_price'])) * 100
        
        # Update balance
        self.balance += pnl
        
        # Record trade
        trade = BacktestTrade(
            entry_time=position['entry_time'],
            exit_time=exit_time,
            symbol=symbol,
            side=position['side'],
            entry_price=position['entry_price'],
            exit_price=exit_price,
            quantity=position['quantity'],
            pnl=pnl,
            pnl_percent=pnl_percent,
            exit_reason=reason
        )
        self.trades.append(trade)
        
        # Remove position
        del self.positions[symbol]
        
        emoji = "🟢" if pnl >= 0 else "🔴"
        logger.debug(f"{emoji} Closed {symbol}: ${pnl:.2f} ({reason})")
    
    def _close_all_positions(self, data: Dict[str, pd.DataFrame], final_time: datetime):
        """Close all open positions at end of backtest"""
        for symbol in list(self.positions.keys()):
            if symbol in data and final_time in data[symbol].index:
                exit_price = data[symbol].loc[final_time, 'close']
            else:
                exit_price = self.positions[symbol]['current_price']
            
            self._close_position(symbol, exit_price, final_time, 'end_of_data')
    
    def _calculate_equity(self, data: Dict[str, pd.DataFrame], current_time: datetime) -> float:
        """Calculate total equity including open positions"""
        equity = self.balance
        
        for symbol, position in self.positions.items():
            equity += position['entry_price'] * position['quantity'] + position.get('unrealized_pnl', 0)
        
        return equity
    
    def _generate_result(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """Generate backtest results"""
        final_balance = self.balance
        total_return = final_balance - self.initial_balance
        total_return_percent = (total_return / self.initial_balance) * 100
        
        # Trade statistics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        profits = sum(t.pnl for t in self.trades if t.pnl > 0)
        losses = sum(t.pnl for t in self.trades if t.pnl < 0)
        profit_factor = abs(profits / losses) if losses != 0 else float('inf')
        
        avg_trade = total_return / total_trades if total_trades > 0 else 0
        avg_win = profits / winning_trades if winning_trades > 0 else 0
        avg_loss = losses / losing_trades if losing_trades > 0 else 0
        
        # Calculate max drawdown
        max_drawdown = 0
        max_drawdown_percent = 0
        peak = self.initial_balance
        
        for date, equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = peak - equity
            drawdown_pct = (drawdown / peak) * 100 if peak > 0 else 0
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_drawdown_percent = drawdown_pct
        
        # Calculate Sharpe ratio (simplified)
        if len(self.equity_curve) > 1:
            returns = []
            for i in range(1, len(self.equity_curve)):
                ret = (self.equity_curve[i][1] - self.equity_curve[i-1][1]) / self.equity_curve[i-1][1]
                returns.append(ret)
            
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = (avg_return / std_return) * np.sqrt(365) if std_return > 0 else 0
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        logger.info(f"✅ Backtest complete: {total_trades} trades, {win_rate:.1f}% win rate, ${total_return:.2f} return")
        
        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_balance=self.initial_balance,
            final_balance=final_balance,
            total_return=total_return,
            total_return_percent=total_return_percent,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_trade=avg_trade,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            trades=self.trades,
            equity_curve=self.equity_curve
        )
    
    def _generate_empty_result(self) -> BacktestResult:
        """Generate empty result for failed backtest"""
        return BacktestResult(
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow(),
            initial_balance=self.initial_balance,
            final_balance=self.initial_balance,
            total_return=0,
            total_return_percent=0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0,
            avg_trade=0,
            avg_win=0,
            avg_loss=0,
            profit_factor=0,
            max_drawdown=0,
            max_drawdown_percent=0,
            sharpe_ratio=0
        )
    
    def save_results(self, result: BacktestResult, filepath: str):
        """Save backtest results to file"""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2, default=str)
        logger.info(f"Backtest results saved to {filepath}")


# Global backtest engine instance
backtest_engine = BacktestEngine()
