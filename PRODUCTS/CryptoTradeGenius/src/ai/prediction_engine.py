"""
AI Prediction Engine - Machine Learning for Crypto Trading
Combines multiple models: LSTM, XGBoost, Technical Indicators
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from loguru import logger
import pickle
import os

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb

# Technical Analysis
try:
    import talib
    TA_LIB_AVAILABLE = True
except ImportError:
    TA_LIB_AVAILABLE = False
    logger.warning("TA-Lib not available, using pandas-ta fallback")

from config.settings import settings


@dataclass
class PredictionResult:
    """AI Prediction Result"""
    signal: str  # buy, sell, hold
    confidence: float  # 0-1
    predicted_price: Optional[float]
    prediction_horizon: int  # hours
    model_confidence: Dict[str, float]
    features_used: Dict[str, float]
    timestamp: datetime


class FeatureEngineer:
    """Technical indicator feature engineering"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        
    def calculate_features(self, ohlcv_data: List[List]) -> pd.DataFrame:
        """
        Calculate technical indicators from OHLCV data
        OHLCV format: [timestamp, open, high, low, close, volume]
        """
        df = pd.DataFrame(
            ohlcv_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Basic price features
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        # Volatility
        df['volatility'] = df['returns'].rolling(window=20).std()
        df['atr'] = self._calculate_atr(df)
        
        # Moving Averages
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'], 14)
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        df['obv'] = self._calculate_obv(df)
        
        # Price patterns
        df['higher_high'] = (df['high'] > df['high'].shift(1)).astype(int)
        df['lower_low'] = (df['low'] < df['low'].shift(1)).astype(int)
        df['higher_close'] = (df['close'] > df['close'].shift(1)).astype(int)
        
        # Price momentum
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        df['momentum_20'] = df['close'] / df['close'].shift(20) - 1
        
        # Support/Resistance distance
        df['dist_from_high_20'] = (df['close'] - df['high'].rolling(20).max()) / df['close']
        df['dist_from_low_20'] = (df['close'] - df['low'].rolling(20).min()) / df['close']
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI manually if TA-Lib not available"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        return true_range.rolling(period).mean()
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On Balance Volume"""
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)
    
    def get_feature_columns(self) -> List[str]:
        """Return list of feature column names"""
        return [
            'returns', 'log_returns', 'volatility', 'atr',
            'sma_10', 'sma_20', 'sma_50', 'ema_12', 'ema_26',
            'macd', 'macd_signal', 'macd_hist', 'rsi',
            'bb_position', 'bb_width', 'volume_ratio', 'obv',
            'momentum_10', 'momentum_20',
            'dist_from_high_20', 'dist_from_low_20'
        ]


class EnsemblePredictor:
    """Ensemble of ML models for price prediction"""
    
    def __init__(self):
        self.models = {}
        self.feature_engineer = FeatureEngineer()
        self.is_trained = False
        self.model_version = "1.0.0"
        
    def train(self, historical_data: pd.DataFrame, symbol: str):
        """Train models on historical data"""
        logger.info(f"Training models for {symbol}...")
        
        # Calculate features
        df = self.feature_engineer.calculate_features(historical_data.values.tolist())
        
        if len(df) < 100:
            logger.warning(f"Insufficient data for training: {len(df)} rows")
            return False
        
        # Create labels (future price direction)
        df['future_return'] = df['close'].shift(-1) / df['close'] - 1
        df['label'] = pd.cut(df['future_return'], 
                            bins=[-np.inf, -0.005, 0.005, np.inf],
                            labels=['sell', 'hold', 'buy'])
        
        df = df.dropna()
        
        feature_cols = self.feature_engineer.get_feature_columns()
        X = df[feature_cols]
        y = df['label']
        
        # Scale features
        X_scaled = self.feature_engineer.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, shuffle=False
        )
        
        # Train Random Forest
        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf.fit(X_train, y_train)
        rf_pred = rf.predict(X_test)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        
        # Train XGBoost
        xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            objective='multi:softprob',
            num_class=3,
            random_state=42
        )
        xgb_model.fit(X_train, y_train)
        xgb_pred = xgb_model.predict(X_test)
        xgb_accuracy = accuracy_score(y_test, xgb_pred)
        
        # Store models
        self.models[symbol] = {
            'random_forest': rf,
            'xgboost': xgb_model,
            'rf_accuracy': rf_accuracy,
            'xgb_accuracy': xgb_accuracy
        }
        
        logger.info(f"✅ Models trained - RF: {rf_accuracy:.2%}, XGB: {xgb_accuracy:.2%}")
        self.is_trained = True
        return True
    
    def predict(self, ohlcv_data: List[List], symbol: str) -> PredictionResult:
        """Generate prediction for given market data"""
        
        # Calculate features
        df = self.feature_engineer.calculate_features(ohlcv_data)
        
        if len(df) == 0:
            return PredictionResult(
                signal="hold",
                confidence=0.5,
                predicted_price=None,
                prediction_horizon=1,
                model_confidence={},
                features_used={},
                timestamp=datetime.utcnow()
            )
        
        # Get latest features
        feature_cols = self.feature_engineer.get_feature_columns()
        latest_features = df[feature_cols].iloc[-1:]
        X = self.feature_engineer.scaler.transform(latest_features)
        
        # Get current price
        current_price = df['close'].iloc[-1]
        
        # If no trained models, use rule-based approach
        if symbol not in self.models:
            return self._rule_based_prediction(df, current_price)
        
        # Get model predictions
        models = self.models[symbol]
        rf = models['random_forest']
        xgb_model = models['xgboost']
        
        # Random Forest prediction
        rf_pred = rf.predict(X)[0]
        rf_proba = rf.predict_proba(X)[0]
        rf_confidence = max(rf_proba)
        
        # XGBoost prediction
        xgb_pred = xgb_model.predict(X)[0]
        xgb_proba = xgb_model.predict_proba(X)[0]
        xgb_confidence = max(xgb_proba)
        
        # Map numeric predictions to labels
        label_map = {0: 'sell', 1: 'hold', 2: 'buy'}
        rf_signal = label_map.get(rf_pred, 'hold')
        xgb_signal = label_map.get(xgb_pred, 'hold')
        
        # Ensemble decision
        signals = [rf_signal, xgb_signal]
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        if buy_count > sell_count:
            final_signal = 'buy'
            avg_confidence = (rf_confidence + xgb_confidence) / 2
        elif sell_count > buy_count:
            final_signal = 'sell'
            avg_confidence = (rf_confidence + xgb_confidence) / 2
        else:
            final_signal = 'hold'
            avg_confidence = 0.5
        
        # Weight by model accuracy
        rf_weight = models['rf_accuracy']
        xgb_weight = models['xgb_accuracy']
        total_weight = rf_weight + xgb_weight
        
        weighted_confidence = (
            (rf_confidence * rf_weight + xgb_confidence * xgb_weight) / total_weight
        )
        
        # Predict price movement
        predicted_return = self._predict_return(df, final_signal)
        predicted_price = current_price * (1 + predicted_return)
        
        # Extract key features for transparency
        key_features = {
            'rsi': float(latest_features['rsi'].iloc[0]),
            'macd': float(latest_features['macd'].iloc[0]),
            'rsi_signal': float(latest_features['macd_signal'].iloc[0]),
            'bb_position': float(latest_features['bb_position'].iloc[0]),
            'volume_ratio': float(latest_features['volume_ratio'].iloc[0]),
            'momentum_10': float(latest_features['momentum_10'].iloc[0]),
        }
        
        return PredictionResult(
            signal=final_signal,
            confidence=weighted_confidence,
            predicted_price=predicted_price,
            prediction_horizon=1,  # Next candle
            model_confidence={
                'random_forest': rf_confidence,
                'xgboost': xgb_confidence,
                'weighted_average': weighted_confidence
            },
            features_used=key_features,
            timestamp=datetime.utcnow()
        )
    
    def _rule_based_prediction(self, df: pd.DataFrame, current_price: float) -> PredictionResult:
        """Fallback rule-based prediction when models aren't trained"""
        latest = df.iloc[-1]
        
        # RSI signal
        rsi = latest['rsi']
        if rsi < 30:
            rsi_signal = 'buy'
        elif rsi > 70:
            rsi_signal = 'sell'
        else:
            rsi_signal = 'hold'
        
        # MACD signal
        macd = latest['macd']
        macd_signal_line = latest['macd_signal']
        if macd > macd_signal_line and macd > 0:
            macd_signal = 'buy'
        elif macd < macd_signal_line and macd < 0:
            macd_signal = 'sell'
        else:
            macd_signal = 'hold'
        
        # Bollinger Bands
        bb_pos = latest['bb_position']
        if bb_pos < 0.1:
            bb_signal = 'buy'
        elif bb_pos > 0.9:
            bb_signal = 'sell'
        else:
            bb_signal = 'hold'
        
        # Combine signals
        signals = [rsi_signal, macd_signal, bb_signal]
        buy_count = signals.count('buy')
        sell_count = signals.count('sell')
        
        if buy_count >= 2:
            final_signal = 'buy'
            confidence = 0.6 + (buy_count - 2) * 0.15
        elif sell_count >= 2:
            final_signal = 'sell'
            confidence = 0.6 + (sell_count - 2) * 0.15
        else:
            final_signal = 'hold'
            confidence = 0.5
        
        return PredictionResult(
            signal=final_signal,
            confidence=min(confidence, 0.95),
            predicted_price=None,
            prediction_horizon=1,
            model_confidence={'rule_based': confidence},
            features_used={
                'rsi': float(rsi),
                'macd': float(macd),
                'bb_position': float(bb_pos),
            },
            timestamp=datetime.utcnow()
        )
    
    def _predict_return(self, df: pd.DataFrame, signal: str) -> float:
        """Predict expected return based on historical patterns"""
        # Simple heuristic based on recent volatility
        volatility = df['returns'].std() * np.sqrt(24)  # Daily vol
        
        if signal == 'buy':
            return volatility * 0.5  # Conservative profit target
        elif signal == 'sell':
            return -volatility * 0.5
        return 0
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'models': self.models,
                'scaler': self.feature_engineer.scaler,
                'version': self.model_version
            }, f)
        logger.info(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        if not os.path.exists(filepath):
            logger.warning(f"Model file not found: {filepath}")
            return False
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.models = data['models']
            self.feature_engineer.scaler = data['scaler']
            self.model_version = data.get('version', '1.0.0')
        
        self.is_trained = True
        logger.info(f"Models loaded from {filepath} (v{self.model_version})")
        return True


class AIPredictionEngine:
    """Main AI engine for crypto trading predictions"""
    
    def __init__(self):
        self.predictor = EnsemblePredictor()
        self.trained_symbols = set()
        
    async def initialize(self):
        """Initialize AI engine"""
        logger.info("🤖 Initializing AI Prediction Engine...")
        
        # Try to load existing models
        model_path = settings.ml_model_path
        if os.path.exists(model_path):
            self.predictor.load_models(model_path)
        else:
            logger.info("No existing models found, will train on first data")
    
    async def predict(self, symbol: str, ohlcv_data: List[List]) -> Optional[PredictionResult]:
        """Generate AI prediction for symbol"""
        try:
            # Train if needed
            if symbol not in self.trained_symbols and len(ohlcv_data) > 100:
                success = self.predictor.train(
                    pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']),
                    symbol
                )
                if success:
                    self.trained_symbols.add(symbol)
            
            # Generate prediction
            result = self.predictor.predict(ohlcv_data, symbol)
            
            # Filter by confidence threshold
            if result.confidence < settings.ai_prediction_threshold:
                result.signal = 'hold'
                logger.debug(f"Low confidence ({result.confidence:.2f}), signal changed to HOLD")
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating prediction for {symbol}: {e}")
            return None
    
    async def batch_predict(self, symbols_data: Dict[str, List[List]]) -> Dict[str, PredictionResult]:
        """Generate predictions for multiple symbols"""
        results = {}
        for symbol, data in symbols_data.items():
            result = await self.predict(symbol, data)
            if result:
                results[symbol] = result
        return results
    
    def save_models(self):
        """Persist trained models"""
        os.makedirs(os.path.dirname(settings.ml_model_path), exist_ok=True)
        self.predictor.save_models(settings.ml_model_path)


# Global AI engine instance
ai_engine = AIPredictionEngine()
