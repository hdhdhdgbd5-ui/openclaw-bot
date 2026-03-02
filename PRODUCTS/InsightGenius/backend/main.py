"""
InsightGenius - Real-Time Business Intelligence Dashboard with ML Predictions
Main FastAPI Application Entry Point
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.config import settings
from core.database import init_db, engine
from api.routes import router as api_router
from services.realtime import RealTimeManager
from services.nlp_query import NLPQueryEngine
from core.logging import logger

# Global managers
realtime_manager = RealTimeManager()
nlp_engine = NLPQueryEngine()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting InsightGenius BI Dashboard...")
    await init_db()
    await realtime_manager.start()
    await nlp_engine.initialize()
    logger.info("✅ InsightGenius ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down InsightGenius...")
    await realtime_manager.stop()
    await engine.dispose()
    logger.info("✅ Shutdown complete")

app = FastAPI(
    title="InsightGenius API",
    description="Real-Time Business Intelligence Dashboard with ML Predictions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket for real-time updates
@app.websocket("/ws/realtime")
async def realtime_websocket(websocket: WebSocket):
    await realtime_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await realtime_manager.handle_message(websocket, data)
    except WebSocketDisconnect:
        await realtime_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await realtime_manager.disconnect(websocket)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "InsightGenius",
        "version": "1.0.0",
        "features": [
            "data_connectors",
            "auto_visualization",
            "ml_predictions",
            "anomaly_detection",
            "automated_reports",
            "realtime_alerts",
            "nlp_queries",
            "export_pdf_pptx"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )
