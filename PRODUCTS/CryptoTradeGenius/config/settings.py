"""
CryptoTradeGenius Configuration
Centralized settings management using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import List, Optional
from enum import Enum


class TradingMode(str, Enum):
    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Trading Mode
    trading_mode: TradingMode = Field(default=TradingMode.PAPER)
    log_level: str = Field(default="INFO")
    
    # Exchange API Keys - Testnet/Sandbox
    binance_testnet_api_key: Optional[str] = None
    binance_testnet_secret: Optional[str] = None
    coinbase_sandbox_api_key: Optional[str] = None
    coinbase_sandbox_secret: Optional[str] = None
    
    # Exchange API Keys - Live
    binance_api_key: Optional[str] = None
    binance_secret: Optional[str] = None
    coinbase_api_key: Optional[str] = None
    coinbase_secret: Optional[str] = None
    
    # Telegram
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_admin_ids: List[str] = Field(default_factory=list)
    
    # Database
    database_url: str = Field(default="sqlite:///data/trading.db")
    redis_url: Optional[str] = None
    
    # Risk Management
    max_risk_per_trade: float = Field(default=2.0, ge=0.1, le=100)
    max_daily_loss: float = Field(default=5.0, ge=0.1, le=100)
    max_portfolio_risk: float = Field(default=10.0, ge=0.1, le=100)
    max_open_positions: int = Field(default=10, ge=1, le=100)
    default_stop_loss: float = Field(default=3.0, ge=0.1, le=100)
    default_take_profit: float = Field(default=6.0, ge=0.1, le=1000)
    
    # AI Configuration
    ai_prediction_threshold: float = Field(default=0.65, ge=0.5, le=1.0)
    ml_model_path: str = Field(default="models/trading_model.pkl")
    enable_deep_learning: bool = True
    enable_ensemble_models: bool = True
    
    # Portfolio Management
    rebalance_interval: int = Field(default=24, ge=1)  # hours
    min_order_size: float = Field(default=10.0, ge=1)
    max_order_size: float = Field(default=10000.0, ge=10)
    
    # Monitoring
    health_check_interval: int = Field(default=60)  # seconds
    performance_report_hour: int = Field(default=0)  # UTC hour
    
    # API Server
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_secret_key: str = Field(default="change-this-in-production")
    
    @validator("telegram_admin_ids", pre=True)
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v
    
    @property
    def is_paper_trading(self) -> bool:
        return self.trading_mode == TradingMode.PAPER
    
    @property
    def is_live_trading(self) -> bool:
        return self.trading_mode == TradingMode.LIVE
    
    def get_exchange_credentials(self, exchange: str) -> dict:
        """Get credentials for specific exchange based on trading mode"""
        if self.is_paper_trading:
            if exchange.lower() == "binance":
                return {
                    "apiKey": self.binance_testnet_api_key,
                    "secret": self.binance_testnet_secret,
                    "sandbox": True,
                    "enableRateLimit": True
                }
            elif exchange.lower() == "coinbase":
                return {
                    "apiKey": self.coinbase_sandbox_api_key,
                    "secret": self.coinbase_sandbox_secret,
                    "sandbox": True
                }
        else:
            if exchange.lower() == "binance":
                return {
                    "apiKey": self.binance_api_key,
                    "secret": self.binance_secret,
                    "enableRateLimit": True
                }
            elif exchange.lower() == "coinbase":
                return {
                    "apiKey": self.coinbase_api_key,
                    "secret": self.coinbase_secret
                }
        return {}


# Global settings instance
settings = Settings()
