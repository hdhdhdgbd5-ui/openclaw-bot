"""
Market Data Utilities
Helper functions for fetching and processing market data
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

from src.exchanges.exchange_manager import exchange_manager


class MarketDataFetcher:
    """Fetch and cache market data"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # seconds
        
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        days: int = 30,
        exchange: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            days: Number of days of history
            exchange: Specific exchange or None for default
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Calculate required candles
            candles_per_day = {
                "1m": 1440, "5m": 288, "15m": 96, 
                "1h": 24, "4h": 6, "1d": 1
            }
            limit = candles_per_day.get(timeframe, 24) * days
            
            # Fetch from exchange
            ohlcv = await exchange_manager.get_ohlcv(symbol, timeframe, limit, exchange)
            
            if not ohlcv:
                logger.warning(f"No data returned for {symbol}")
                return pd.DataFrame()
            
            # Create DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            # Convert types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def get_multiple_symbols(
        self,
        symbols: List[str],
        timeframe: str = "1h",
        days: int = 7
    ) -> Dict[str, pd.DataFrame]:
        """Fetch data for multiple symbols concurrently"""
        tasks = [self.get_historical_data(sym, timeframe, days) for sym in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        data = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, pd.DataFrame) and not result.empty:
                data[symbol] = result
            else:
                logger.warning(f"Failed to fetch data for {symbol}")
        
        return data
    
    def calculate_correlation_matrix(
        self,
        data: Dict[str, pd.DataFrame],
        field: str = "close"
    ) -> pd.DataFrame:
        """Calculate correlation matrix between symbols"""
        # Extract price series
        prices = {}
        for symbol, df in data.items():
            if field in df.columns:
                prices[symbol] = df[field]
        
        if not prices:
            return pd.DataFrame()
        
        # Create combined DataFrame
        price_df = pd.DataFrame(prices)
        
        # Calculate returns
        returns_df = price_df.pct_change().dropna()
        
        # Calculate correlation
        correlation = returns_df.corr()
        
        return correlation
    
    def detect_market_regime(self, df: pd.DataFrame, lookback: int = 20) -> str:
        """
        Detect current market regime
        Returns: 'trending_up', 'trending_down', 'ranging', 'volatile'
        """
        if len(df) < lookback:
            return "unknown"
        
        recent = df.tail(lookback)
        
        # Calculate metrics
        returns = recent['close'].pct_change().dropna()
        volatility = returns.std() * np.sqrt(24)  # Daily vol
        total_return = (recent['close'].iloc[-1] / recent['close'].iloc[0] - 1)
        
        # ADX for trend strength (simplified)
        adx = self._calculate_adx(recent)
        
        # Classify regime
        if adx > 25:
            if total_return > 0.02:
                return "trending_up"
            elif total_return < -0.02:
                return "trending_down"
        
        if volatility > 0.05:  # 5% daily vol
            return "volatile"
        
        return "ranging"
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """Simplified ADX calculation"""
        if len(df) < period + 1:
            return 0
        
        # True Range
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        
        # Directional Movement
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff(-1).abs()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        # Smoothed averages
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # DX and ADX
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0
    
    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate support and resistance levels"""
        if len(df) < window:
            return {}
        
        recent = df.tail(window)
        
        # Find local minima/maxima
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Simple method: use rolling max/min
        resistance = recent['high'].max()
        support = recent['low'].min()
        
        # More sophisticated: cluster analysis (simplified)
        current_price = df['close'].iloc[-1]
        
        return {
            "resistance": float(resistance),
            "support": float(support),
            "current_price": float(current_price),
            "position_pct": (current_price - support) / (resistance - support) if resistance != support else 0.5
        }


# Global market data fetcher
market_data = MarketDataFetcher()
