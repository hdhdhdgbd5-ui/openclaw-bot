"""
FastAPI Server - REST API and WebSocket for CryptoTradeGenius
Provides endpoints for monitoring, control, and integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import asyncio

from config.settings import settings
from src.core.trading_engine import trading_engine
from src.portfolio.portfolio_manager import portfolio_manager
from src.risk.risk_manager import risk_manager
from src.backtest.backtest_engine import backtest_engine
from src.core.database import get_session, Trade, Balance, Signal, PerformanceMetrics

# API Models
class TradeRequest(BaseModel):
    symbol: str
    side: str = Field(..., regex="^(buy|sell)$")
    quantity: float = Field(..., gt=0)
    order_type: str = Field(default="market", regex="^(market|limit)$")
    price: Optional[float] = None


class BacktestRequest(BaseModel):
    symbols: List[str]
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    initial_balance: float = Field(default=10000.0, gt=0)
    timeframe: str = Field(default="1h")


class AllocationUpdate(BaseModel):
    allocations: Dict[str, float]


class RiskSettings(BaseModel):
    max_risk_per_trade: Optional[float] = Field(None, ge=0.1, le=100)
    max_daily_loss: Optional[float] = Field(None, ge=0.1, le=100)
    max_open_positions: Optional[int] = Field(None, ge=1, le=100)


# Create FastAPI app
app = FastAPI(
    title="CryptoTradeGenius API",
    description="Institutional-grade AI Crypto Trading Bot API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token"""
    if credentials.credentials != settings.api_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return credentials.credentials


# Health check
@app.get("/")
async def root():
    return {
        "name": "CryptoTradeGenius",
        "version": "1.0.0",
        "status": "running",
        "trading_mode": settings.trading_mode,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "engine_running": trading_engine.is_running,
        "trading_mode": settings.trading_mode,
        "timestamp": datetime.utcnow().isoformat()
    }


# Trading Engine Control
@app.post("/engine/start")
async def start_engine(token: str = Depends(verify_token)):
    """Start the trading engine"""
    if trading_engine.is_running:
        return {"message": "Engine already running"}
    
    asyncio.create_task(trading_engine.start())
    return {"message": "Trading engine started", "timestamp": datetime.utcnow().isoformat()}


@app.post("/engine/stop")
async def stop_engine(token: str = Depends(verify_token)):
    """Stop the trading engine"""
    trading_engine.stop()
    return {"message": "Trading engine stopped", "timestamp": datetime.utcnow().isoformat()}


@app.get("/engine/status")
async def engine_status():
    """Get trading engine status"""
    return trading_engine.get_status()


# Portfolio Endpoints
@app.get("/portfolio/summary")
async def portfolio_summary():
    """Get portfolio summary"""
    await portfolio_manager.update_portfolio_state()
    return portfolio_manager.get_portfolio_summary()


@app.get("/portfolio/performance")
async def portfolio_performance():
    """Get portfolio performance metrics"""
    return await portfolio_manager.get_performance_metrics()


@app.post("/portfolio/allocations")
async def update_allocations(
    allocation_update: AllocationUpdate,
    token: str = Depends(verify_token)
):
    """Update target allocations"""
    success = portfolio_manager.set_target_allocation(allocation_update.allocations)
    if success:
        return {"message": "Allocations updated", "allocations": allocation_update.allocations}
    raise HTTPException(status_code=400, detail="Allocations must sum to 100%")


@app.post("/portfolio/rebalance")
async def trigger_rebalance(token: str = Depends(verify_token)):
    """Trigger portfolio rebalancing"""
    trades = await portfolio_manager.check_and_rebalance()
    return {
        "message": "Rebalancing complete",
        "trades_executed": len(trades),
        "trades": trades
    }


# Trading Endpoints
@app.get("/trades")
async def get_trades(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get trade history"""
    try:
        session = get_session(settings.database_url)
        query = session.query(Trade)
        
        if status:
            query = query.filter(Trade.status == status)
        
        trades = query.order_by(Trade.opened_at.desc()).offset(offset).limit(limit).all()
        
        result = [t.to_dict() for t in trades]
        total = session.query(Trade).count()
        
        session.close()
        
        return {
            "trades": result,
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/trades/manual")
async def manual_trade(
    trade_request: TradeRequest,
    token: str = Depends(verify_token)
):
    """Execute a manual trade"""
    # TODO: Implement manual trade execution
    return {
        "message": "Manual trade submitted",
        "trade": trade_request.dict()
    }


@app.get("/trades/stats")
async def trade_statistics():
    """Get trade statistics"""
    try:
        session = get_session(settings.database_url)
        from sqlalchemy import func
        
        # Overall stats
        total_trades = session.query(Trade).filter(Trade.status == "closed").count()
        winning_trades = session.query(Trade).filter(
            Trade.status == "closed",
            Trade.pnl_absolute > 0
        ).count()
        
        total_pnl = session.query(func.sum(Trade.pnl_absolute)).scalar() or 0
        
        # Today's stats
        from datetime import date
        today = date.today()
        today_pnl = session.query(func.sum(Trade.pnl_absolute)).filter(
            Trade.status == "closed",
            func.date(Trade.closed_at) == today
        ).scalar() or 0
        
        session.close()
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            "total_pnl": round(total_pnl, 2),
            "today_pnl": round(today_pnl, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Risk Management Endpoints
@app.get("/risk/status")
async def risk_status():
    """Get risk management status"""
    return risk_manager.get_risk_report()


@app.post("/risk/settings")
async def update_risk_settings(
    risk_settings: RiskSettings,
    token: str = Depends(verify_token)
):
    """Update risk management settings"""
    if risk_settings.max_risk_per_trade:
        settings.max_risk_per_trade = risk_settings.max_risk_per_trade
    if risk_settings.max_daily_loss:
        settings.max_daily_loss = risk_settings.max_daily_loss
    if risk_settings.max_open_positions:
        settings.max_open_positions = risk_settings.max_open_positions
    
    return {
        "message": "Risk settings updated",
        "settings": {
            "max_risk_per_trade": settings.max_risk_per_trade,
            "max_daily_loss": settings.max_daily_loss,
            "max_open_positions": settings.max_open_positions
        }
    }


@app.post("/risk/enable")
async def enable_trading(token: str = Depends(verify_token)):
    """Enable trading"""
    risk_manager.enable_trading()
    return {"message": "Trading enabled"}


@app.post("/risk/disable")
async def disable_trading(token: str = Depends(verify_token)):
    """Disable trading (emergency stop)"""
    risk_manager.disable_trading()
    return {"message": "Trading disabled - EMERGENCY STOP"}


# Signals Endpoints
@app.get("/signals")
async def get_signals(
    symbol: Optional[str] = None,
    executed_only: bool = False,
    limit: int = 50
):
    """Get AI trading signals"""
    try:
        session = get_session(settings.database_url)
        query = session.query(Signal)
        
        if symbol:
            query = query.filter(Signal.symbol == symbol)
        if executed_only:
            query = query.filter(Signal.executed == True)
        
        signals = query.order_by(Signal.timestamp.desc()).limit(limit).all()
        result = [s.to_dict() for s in signals]
        
        session.close()
        return {"signals": result, "count": len(result)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Backtesting Endpoints
@app.post("/backtest/run")
async def run_backtest(
    backtest_request: BacktestRequest,
    background_tasks: BackgroundTasks,
    token: str = Depends(verify_token)
):
    """Run a backtest (async)"""
    # TODO: Implement full backtest with historical data fetch
    
    return {
        "message": "Backtest started",
        "params": backtest_request.dict(),
        "job_id": f"bt_{int(datetime.utcnow().timestamp())}"
    }


@app.get("/backtest/results/{job_id}")
async def get_backtest_results(job_id: str):
    """Get backtest results"""
    # TODO: Retrieve from storage
    return {"job_id": job_id, "status": "pending", "results": None}


# Market Data Endpoints
@app.get("/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get current ticker data"""
    from src.exchanges.exchange_manager import exchange_manager
    
    ticker = await exchange_manager.get_ticker(symbol)
    if not ticker:
        raise HTTPException(status_code=404, detail=f"Ticker not found for {symbol}")
    
    return {
        "symbol": ticker.symbol,
        "bid": ticker.bid,
        "ask": ticker.ask,
        "last": ticker.last,
        "volume": ticker.volume,
        "change_24h": ticker.change_24h,
        "change_percent_24h": ticker.change_percent_24h,
        "timestamp": ticker.timestamp
    }


@app.get("/market/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 100
):
    """Get OHLCV data"""
    from src.exchanges.exchange_manager import exchange_manager
    
    ohlcv = await exchange_manager.get_ohlcv(symbol, timeframe, limit)
    
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "data": ohlcv,
        "count": len(ohlcv)
    }


@app.get("/market/supported-pairs")
async def get_supported_pairs():
    """Get list of supported trading pairs"""
    return {
        "pairs": trading_engine.trading_pairs,
        "count": len(trading_engine.trading_pairs)
    }


# System Endpoints
@app.get("/system/settings")
async def get_settings():
    """Get current system settings (safe values only)"""
    return {
        "trading_mode": settings.trading_mode,
        "max_risk_per_trade": settings.max_risk_per_trade,
        "max_daily_loss": settings.max_daily_loss,
        "max_open_positions": settings.max_open_positions,
        "ai_prediction_threshold": settings.ai_prediction_threshold,
        "rebalance_interval": settings.rebalance_interval,
        "min_order_size": settings.min_order_size,
        "max_order_size": settings.max_order_size,
    }


@app.get("/system/logs")
async def get_logs(lines: int = 100):
    """Get recent log entries"""
    # TODO: Implement log retrieval
    return {"message": "Log retrieval not yet implemented"}


# WebSocket for real-time updates
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send status update
            status = {
                "type": "status_update",
                "timestamp": datetime.utcnow().isoformat(),
                "engine_running": trading_engine.is_running,
                "active_positions": len(trading_engine.active_positions),
                "portfolio_value": (
                    portfolio_manager.current_state.total_value 
                    if portfolio_manager.current_state else 0
                )
            }
            
            await websocket.send_json(status)
            await asyncio.sleep(5)  # Update every 5 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


def start_server():
    """Start the API server"""
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
