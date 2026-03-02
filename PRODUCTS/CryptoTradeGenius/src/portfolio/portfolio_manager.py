"""
Portfolio Management System - Automated rebalancing and allocation
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

from config.settings import settings
from src.exchanges.exchange_manager import exchange_manager, OrderSide, OrderType
from src.risk.risk_manager import risk_manager
from src.core.database import Balance, get_session


@dataclass
class AssetAllocation:
    """Target allocation for an asset"""
    symbol: str
    target_percent: float
    current_percent: float
    current_value: float
    rebalance_threshold: float = 5.0  # Rebalance if drift > 5%
    
    @property
    def drift_percent(self) -> float:
        return self.current_percent - self.target_percent
    
    @property
    def needs_rebalance(self) -> bool:
        return abs(self.drift_percent) > self.rebalance_threshold


@dataclass
class PortfolioState:
    """Current portfolio state"""
    total_value: float
    available_usd: float
    allocations: Dict[str, AssetAllocation]
    last_rebalanced: Optional[datetime]
    
    def get_allocation_drift(self) -> Dict[str, float]:
        """Get allocation drift for all assets"""
        return {sym: alloc.drift_percent for sym, alloc in self.allocations.items()}


class PortfolioManager:
    """Manages portfolio allocation and rebalancing"""
    
    def __init__(self):
        self.target_allocations: Dict[str, float] = {}
        self.current_state: Optional[PortfolioState] = None
        self.rebalance_interval = timedelta(hours=settings.rebalance_interval)
        self.last_rebalance: Optional[datetime] = None
        self.min_rebalance_amount = 50  # Minimum USD amount to rebalance
        
    async def initialize(self):
        """Initialize portfolio manager"""
        logger.info("💼 Portfolio Manager initialized")
        
        # Default allocation: 50% BTC, 30% ETH, 20% cash
        self.target_allocations = {
            "BTC/USDT": 40.0,
            "ETH/USDT": 30.0,
            "SOL/USDT": 15.0,
            "USDT": 15.0,  # Cash reserve
        }
        
        await self.update_portfolio_state()
    
    async def update_portfolio_state(self):
        """Update current portfolio state from exchange"""
        try:
            # Get balances
            balances = await exchange_manager.get_balance()
            
            # Get prices for valuation
            total_value = 0
            asset_values = {}
            
            for asset, balance in balances.items():
                if balance.total > 0:
                    if asset in ["USDT", "USD", "USDC"]:
                        value = balance.total
                    else:
                        # Get price in USDT
                        symbol = f"{asset}/USDT"
                        ticker = await exchange_manager.get_ticker(symbol)
                        price = ticker.last if ticker else 0
                        value = balance.total * price
                    
                    asset_values[asset] = {
                        "balance": balance.total,
                        "value_usd": value
                    }
                    total_value += value
            
            # Calculate allocations
            allocations = {}
            for symbol, target_pct in self.target_allocations.items():
                base_asset = symbol.split("/")[0] if "/" in symbol else symbol
                current_value = asset_values.get(base_asset, {}).get("value_usd", 0)
                current_pct = (current_value / total_value * 100) if total_value > 0 else 0
                
                allocations[symbol] = AssetAllocation(
                    symbol=symbol,
                    target_percent=target_pct,
                    current_percent=current_pct,
                    current_value=current_value
                )
            
            available_usd = asset_values.get("USDT", {}).get("value_usd", 0)
            
            self.current_state = PortfolioState(
                total_value=total_value,
                available_usd=available_usd,
                allocations=allocations,
                last_rebalanced=self.last_rebalance
            )
            
            # Persist to database
            self._save_balance_snapshot(total_value, asset_values)
            
            logger.debug(f"Portfolio value: ${total_value:,.2f}")
            
        except Exception as e:
            logger.error(f"Error updating portfolio state: {e}")
    
    def _save_balance_snapshot(self, total_value: float, asset_values: Dict):
        """Save portfolio snapshot to database"""
        try:
            session = get_session(settings.database_url)
            
            snapshot = Balance(
                total_usd=total_value,
                available_usd=asset_values.get("USDT", {}).get("value_usd", 0),
                allocated_usd=total_value - asset_values.get("USDT", {}).get("value_usd", 0),
                assets=asset_values,
                daily_pnl=0,  # Calculate from previous
                total_pnl=0
            )
            
            session.add(snapshot)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Error saving balance snapshot: {e}")
    
    async def check_and_rebalance(self) -> List[Dict]:
        """Check if rebalancing is needed and execute"""
        if not self.current_state:
            await self.update_portfolio_state()
        
        # Check time since last rebalance
        if self.last_rebalance:
            time_since = datetime.utcnow() - self.last_rebalance
            if time_since < self.rebalance_interval:
                return []
        
        # Check if any allocation has drifted
        rebalance_needed = False
        for allocation in self.current_state.allocations.values():
            if allocation.needs_rebalance:
                rebalance_needed = True
                break
        
        if not rebalance_needed:
            logger.debug("No rebalancing needed")
            return []
        
        # Execute rebalancing
        return await self.execute_rebalance()
    
    async def execute_rebalance(self) -> List[Dict]:
        """Execute rebalancing trades"""
        logger.info("🔄 Executing portfolio rebalance...")
        
        executed_trades = []
        
        for symbol, allocation in self.current_state.allocations.items():
            if symbol == "USDT" or not allocation.needs_rebalance:
                continue
            
            # Calculate target value
            target_value = self.current_state.total_value * (allocation.target_percent / 100)
            value_diff = target_value - allocation.current_value
            
            # Skip if difference is too small
            if abs(value_diff) < self.min_rebalance_amount:
                continue
            
            # Get current price
            ticker = await exchange_manager.get_ticker(symbol)
            if not ticker:
                continue
            
            # Calculate quantity
            quantity = abs(value_diff) / ticker.last
            
            # Determine side
            if value_diff > 0:  # Need to buy more
                side = OrderSide.BUY
            else:  # Need to sell
                side = OrderSide.SELL
            
            # Check risk limits
            can_trade, reason = risk_manager.can_open_position(
                symbol, abs(value_diff), self.current_state.total_value
            )
            
            if not can_trade:
                logger.warning(f"Cannot rebalance {symbol}: {reason}")
                continue
            
            # Execute trade
            try:
                order = await exchange_manager.create_order(
                    symbol=symbol,
                    side=side,
                    order_type=OrderType.MARKET,
                    quantity=quantity
                )
                
                if order:
                    executed_trades.append({
                        "symbol": symbol,
                        "side": side.value,
                        "quantity": quantity,
                        "value_usd": abs(value_diff),
                        "order_id": order.order_id,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    logger.info(f"Rebalance trade: {side.value.upper()} {quantity:.6f} {symbol}")
                    
            except Exception as e:
                logger.error(f"Error executing rebalance trade for {symbol}: {e}")
        
        if executed_trades:
            self.last_rebalance = datetime.utcnow()
            self.current_state.last_rebalanced = self.last_rebalance
            logger.info(f"✅ Rebalancing complete: {len(executed_trades)} trades executed")
        
        return executed_trades
    
    def set_target_allocation(self, allocations: Dict[str, float]):
        """Update target allocations (must sum to 100%)"""
        total = sum(allocations.values())
        if abs(total - 100.0) > 0.01:
            logger.error(f"Allocations must sum to 100%, got {total}%")
            return False
        
        self.target_allocations = allocations
        logger.info(f"Target allocations updated: {allocations}")
        return True
    
    def get_portfolio_summary(self) -> Dict:
        """Get portfolio summary"""
        if not self.current_state:
            return {"error": "Portfolio state not initialized"}
        
        allocations_list = []
        for symbol, alloc in self.current_state.allocations.items():
            allocations_list.append({
                "symbol": symbol,
                "target_percent": alloc.target_percent,
                "current_percent": round(alloc.current_percent, 2),
                "current_value": round(alloc.current_value, 2),
                "drift_percent": round(alloc.drift_percent, 2),
                "needs_rebalance": alloc.needs_rebalance
            })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_value": round(self.current_state.total_value, 2),
            "available_usd": round(self.current_state.available_usd, 2),
            "allocations": allocations_list,
            "last_rebalanced": (
                self.current_state.last_rebalanced.isoformat() 
                if self.current_state.last_rebalanced else None
            ),
            "rebalance_interval_hours": settings.rebalance_interval,
        }
    
    async def get_performance_metrics(self) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            session = get_session(settings.database_url)
            
            # Get recent balance history
            from sqlalchemy import desc
            from src.core.database import Balance as BalanceModel
            
            recent_balances = session.query(BalanceModel).order_by(
                desc(BalanceModel.timestamp)
            ).limit(30).all()
            
            if len(recent_balances) < 2:
                return {"error": "Insufficient history"}
            
            # Calculate returns
            values = [b.total_usd for b in recent_balances]
            returns = [(values[i] - values[i+1]) / values[i+1] 
                      for i in range(len(values)-1)]
            
            metrics = {
                "current_value": round(values[0], 2),
                "value_7d_ago": round(values[min(7, len(values)-1)], 2),
                "value_30d_ago": round(values[-1], 2),
                "return_7d": round((values[0] / values[min(7, len(values)-1)] - 1) * 100, 2),
                "return_30d": round((values[0] / values[-1] - 1) * 100, 2),
                "volatility": round(np.std(returns) * np.sqrt(365) * 100, 2) if returns else 0,
                "sharpe_ratio": None,  # Calculate if benchmark available
            }
            
            session.close()
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {"error": str(e)}


# Global portfolio manager instance
portfolio_manager = PortfolioManager()
