"""
Real-time API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from models.user import User
from services.realtime import RealTimeManager

router = APIRouter()
realtime_manager = RealTimeManager()

@router.get("/status")
async def get_realtime_status(
    current_user: User = Depends(get_current_user)
):
    """Get real-time service status"""
    return {
        "connected_clients": len(realtime_manager.active_connections),
        "streaming_datasets": realtime_manager.streaming_datasets,
        "active_alerts": realtime_manager.active_alerts
    }

@router.post("/subscribe/{dataset_id}")
async def subscribe_to_dataset(
    dataset_id: int,
    current_user: User = Depends(get_current_user)
):
    """Subscribe to real-time updates for a dataset"""
    # WebSocket clients call this to register interest
    return {
        "message": "Use WebSocket connection at /ws/realtime",
        "subscription_key": f"dataset:{dataset_id}"
    }

@router.post("/alert/test")
async def test_realtime_alert(
    alert_config: dict,
    current_user: User = Depends(get_current_user)
):
    """Test real-time alert delivery"""
    await realtime_manager.test_alert(alert_config, current_user.id)
    return {"message": "Test alert sent"}
