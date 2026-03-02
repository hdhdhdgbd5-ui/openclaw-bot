"""
Exchange Manager - Unified interface for multiple crypto exchanges
Supports Binance and Coinbase with paper trading mode
"""

import ccxt
import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from loguru import logger
from dataclasses import dataclass
from enum import Enum

from config.settings import settings


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    STOP_LOSS_LIMIT = "stop_loss_limit"
    TAKE_PROFIT = "take_profit"


@dataclass
class OrderResult:
    """Standardized order result"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    status: str
    filled: float
    remaining: float
    cost: float
    fee: float
    timestamp: int
    raw_response: Dict


@dataclass
class Balance:
    """Standardized balance info"""
    asset: str
    free: float
    used: float
    total: float
    usd_value: float = 0


@dataclass
class Ticker:
    """Standardized ticker data"""
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float
    change_24h: float
    change_percent_24h: float
    timestamp: int


class ExchangeManager:
    """Manages connections to multiple exchanges"""
    
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self._paper_balances: Dict[str, Dict[str, float]] = {}
        self._paper_orders: List[Dict] = []
        self.trading_mode = settings.trading_mode
        
    async def initialize(self):
        """Initialize all configured exchanges"""
        await self._init_binance()
        await self._init_coinbase()
        
        if settings.is_paper_trading:
            logger.info("📝 PAPER TRADING MODE - No real money at risk")
            await self._init_paper_balances()
        else:
            logger.warning("🔴 LIVE TRADING MODE - Real money at risk!")
        
        logger.info(f"Exchange Manager initialized with {len(self.exchanges)} exchanges")
    
    async def _init_binance(self):
        """Initialize Binance connection"""
        try:
            credentials = settings.get_exchange_credentials("binance")
            if not credentials.get("apiKey"):
                logger.warning("Binance credentials not configured")
                return
            
            exchange_class = ccxt.binance
            if settings.is_paper_trading:
                # Use Binance testnet
                exchange = exchange_class({
                    **credentials,
                    'options': {
                        'defaultType': 'spot',
                        'adjustForTimeDifference': True,
                    },
                    'sandbox': True,
                    'urls': {
                        'api': {
                            'public': 'https://testnet.binance.vision/api',
                            'private': 'https://testnet.binance.vision/api',
                        }
                    }
                })
            else:
                exchange = exchange_class(credentials)
            
            await exchange.load_markets()
            self.exchanges['binance'] = exchange
            logger.info(f"✅ Binance connected (Testnet: {settings.is_paper_trading})")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Binance: {e}")
    
    async def _init_coinbase(self):
        """Initialize Coinbase connection"""
        try:
            credentials = settings.get_exchange_credentials("coinbase")
            if not credentials.get("apiKey"):
                logger.warning("Coinbase credentials not configured")
                return
            
            exchange = ccxt.coinbase(credentials)
            await exchange.load_markets()
            self.exchanges['coinbase'] = exchange
            logger.info(f"✅ Coinbase connected")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Coinbase: {e}")
    
    async def _init_paper_balances(self):
        """Initialize paper trading balances"""
        self._paper_balances = {
            "USDT": {"free": 10000.0, "used": 0.0, "total": 10000.0},
            "USD": {"free": 10000.0, "used": 0.0, "total": 10000.0},
            "BTC": {"free": 0.0, "used": 0.0, "total": 0.0},
            "ETH": {"free": 0.0, "used": 0.0, "total": 0.0},
        }
    
    async def get_balance(self, exchange_name: Optional[str] = None) -> Dict[str, Balance]:
        """Get balance from exchange(s)"""
        balances = {}
        
        if settings.is_paper_trading:
            for asset, data in self._paper_balances.items():
                balances[asset] = Balance(
                    asset=asset,
                    free=data["free"],
                    used=data["used"],
                    total=data["total"]
                )
            return balances
        
        exchanges_to_query = [exchange_name] if exchange_name else self.exchanges.keys()
        
        for ex_name in exchanges_to_query:
            if ex_name not in self.exchanges:
                continue
            
            try:
                ex = self.exchanges[ex_name]
                raw_balance = await ex.fetch_balance()
                
                for asset, data in raw_balance.get("total", {}).items():
                    if data > 0:
                        key = f"{asset}_{ex_name}"
                        balances[key] = Balance(
                            asset=asset,
                            free=raw_balance.get("free", {}).get(asset, 0),
                            used=raw_balance.get("used", {}).get(asset, 0),
                            total=data
                        )
                        
            except Exception as e:
                logger.error(f"Error fetching balance from {ex_name}: {e}")
        
        return balances
    
    async def get_ticker(self, symbol: str, exchange_name: Optional[str] = None) -> Optional[Ticker]:
        """Get ticker data for a symbol"""
        exchanges_to_query = [exchange_name] if exchange_name else self.exchanges.keys()
        
        for ex_name in exchanges_to_query:
            if ex_name not in self.exchanges:
                continue
            
            try:
                ex = self.exchanges[ex_name]
                ticker = await ex.fetch_ticker(symbol)
                
                return Ticker(
                    symbol=symbol,
                    bid=ticker.get("bid", 0),
                    ask=ticker.get("ask", 0),
                    last=ticker.get("last", 0),
                    volume=ticker.get("volume", 0),
                    change_24h=ticker.get("change", 0),
                    change_percent_24h=ticker.get("percentage", 0),
                    timestamp=ticker.get("timestamp", 0)
                )
                
            except Exception as e:
                logger.error(f"Error fetching ticker from {ex_name}: {e}")
        
        return None
    
    async def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100, 
                        exchange_name: Optional[str] = None) -> List[List]:
        """Get OHLCV candlestick data"""
        if exchange_name and exchange_name in self.exchanges:
            ex = self.exchanges[exchange_name]
        else:
            ex = list(self.exchanges.values())[0] if self.exchanges else None
        
        if not ex:
            return []
        
        try:
            ohlcv = await ex.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            return []
    
    async def create_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                          quantity: float, price: Optional[float] = None,
                          stop_price: Optional[float] = None,
                          exchange_name: Optional[str] = None) -> Optional[OrderResult]:
        """Create an order on the exchange"""
        
        # Validate order size
        if quantity * (price or 0) < settings.min_order_size:
            logger.warning(f"Order size too small: {quantity * (price or 0)}")
            return None
        
        if settings.is_paper_trading:
            return await self._create_paper_order(symbol, side, order_type, quantity, price, stop_price)
        
        if exchange_name and exchange_name not in self.exchanges:
            logger.error(f"Exchange {exchange_name} not available")
            return None
        
        ex = self.exchanges.get(exchange_name) or list(self.exchanges.values())[0]
        
        try:
            order_params = {
                "symbol": symbol,
                "type": order_type.value,
                "side": side.value,
                "amount": quantity,
            }
            
            if price and order_type != OrderType.MARKET:
                order_params["price"] = price
            
            if stop_price:
                order_params["stopPrice"] = stop_price
            
            order = await ex.create_order(**order_params)
            
            return OrderResult(
                order_id=order.get("id", ""),
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=order.get("price", price or 0),
                status=order.get("status", "unknown"),
                filled=order.get("filled", 0),
                remaining=order.get("remaining", quantity),
                cost=order.get("cost", 0),
                fee=order.get("fee", {}).get("cost", 0),
                timestamp=order.get("timestamp", 0),
                raw_response=order
            )
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    async def _create_paper_order(self, symbol: str, side: OrderSide, order_type: OrderType,
                                  quantity: float, price: Optional[float] = None,
                                  stop_price: Optional[float] = None) -> OrderResult:
        """Simulate order in paper trading mode"""
        
        # Get current market price
        ticker = await self.get_ticker(symbol)
        market_price = ticker.last if ticker else (price or 0)
        
        base_asset = symbol.split("/")[0]
        quote_asset = symbol.split("/")[1] if "/" in symbol else "USDT"
        
        order_cost = quantity * market_price
        
        # Check sufficient balance
        if side == OrderSide.BUY:
            if self._paper_balances.get(quote_asset, {}).get("free", 0) < order_cost:
                logger.warning(f"Insufficient {quote_asset} balance for paper trade")
                return None
            
            # Update balances
            self._paper_balances[quote_asset]["free"] -= order_cost
            self._paper_balances[quote_asset]["total"] -= order_cost
            self._paper_balances[base_asset]["free"] += quantity
            self._paper_balances[base_asset]["total"] += quantity
            
        else:  # SELL
            if self._paper_balances.get(base_asset, {}).get("free", 0) < quantity:
                logger.warning(f"Insufficient {base_asset} balance for paper trade")
                return None
            
            # Update balances
            self._paper_balances[base_asset]["free"] -= quantity
            self._paper_balances[base_asset]["total"] -= quantity
            self._paper_balances[quote_asset]["free"] += order_cost
            self._paper_balances[quote_asset]["total"] += order_cost
        
        order_id = f"paper_{len(self._paper_orders)}_{asyncio.get_event_loop().time()}"
        
        order = OrderResult(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=market_price,
            status="filled",
            filled=quantity,
            remaining=0,
            cost=order_cost,
            fee=order_cost * 0.001,  # 0.1% fee simulation
            timestamp=int(asyncio.get_event_loop().time() * 1000),
            raw_response={"paper": True}
        )
        
        self._paper_orders.append({
            "order": order,
            "timestamp": datetime.utcnow()
        })
        
        logger.info(f"📝 PAPER ORDER: {side.value.upper()} {quantity} {symbol} @ {market_price}")
        
        return order
    
    async def cancel_order(self, order_id: str, symbol: str, exchange_name: Optional[str] = None) -> bool:
        """Cancel an existing order"""
        if settings.is_paper_trading:
            return True
        
        if exchange_name and exchange_name not in self.exchanges:
            return False
        
        ex = self.exchanges.get(exchange_name) or list(self.exchanges.values())[0]
        
        try:
            await ex.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return False
    
    async def get_order_status(self, order_id: str, symbol: str, 
                               exchange_name: Optional[str] = None) -> Optional[Dict]:
        """Get order status"""
        if settings.is_paper_trading:
            return {"status": "filled", "paper": True}
        
        if exchange_name and exchange_name not in self.exchanges:
            return None
        
        ex = self.exchanges.get(exchange_name) or list(self.exchanges.values())[0]
        
        try:
            order = await ex.fetch_order(order_id, symbol)
            return order
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            return None
    
    async def close(self):
        """Close all exchange connections"""
        for name, exchange in self.exchanges.items():
            try:
                await exchange.close()
                logger.info(f"Closed connection to {name}")
            except Exception as e:
                logger.error(f"Error closing {name}: {e}")


# Global exchange manager instance
exchange_manager = ExchangeManager()
