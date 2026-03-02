"""
Alerts API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.alert import Alert, AlertRule, AlertNotification
from models.dataset import Dataset
from services.alert_service import AlertService
from schemas.alert import (
    AlertCreate,
    AlertRuleCreate,
    AlertResponse,
    AlertUpdate
)

router = APIRouter()
alert_service = AlertService()

@router.get("/types")
async def get_alert_types():
    """Get available alert condition types"""
    return [
        {
            "type": "threshold",
            "name": "Threshold Alert",
            "description": "Trigger when metric crosses a threshold",
            "config": {
                "metric_column": "string",
                "aggregation": "value|sum|avg|count|min|max",
                "operator": ">|<|>=|<=|==|!=|between",
                "threshold_value": "number",
                "threshold_value_max": "number (for between)"
            }
        },
        {
            "type": "anomaly",
            "name": "Anomaly Detection",
            "description": "AI-powered anomaly detection",
            "config": {
                "columns": "list of columns to monitor",
                "sensitivity": "low|medium|high",
                "lookback_window": "1h|1d|7d|30d"
            }
        },
        {
            "type": "trend",
            "name": "Trend Alert",
            "description": "Alert on increasing or decreasing trends",
            "config": {
                "metric_column": "string",
                "trend_direction": "increasing|decreasing",
                "trend_period": "1d|7d|30d",
                "trend_percentage": "number (%)"
            }
        },
        {
            "type": "custom",
            "name": "Custom Condition",
            "description": "Define custom SQL or expression",
            "config": {
                "custom_condition": "SQL expression or formula"
            }
        }
    ]

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new alert"""
    db_alert = Alert(
        name=alert.name,
        description=alert.description,
        dataset_id=alert.dataset_id,
        dashboard_id=alert.dashboard_id,
        severity=alert.severity,
        is_active=True,
        owner_id=current_user.id
    )
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    
    # Create rules
    for rule in alert.rules:
        db_rule = AlertRule(
            alert_id=db_alert.id,
            condition_type=rule.condition_type,
            metric_column=rule.metric_column,
            aggregation=rule.aggregation,
            operator=rule.operator,
            threshold_value=rule.threshold_value,
            anomaly_sensitivity=rule.anomaly_sensitivity,
            trend_direction=rule.trend_direction,
            custom_condition=rule.custom_condition,
            lookback_window=rule.lookback_window,
            cooldown_minutes=rule.cooldown_minutes
        )
        db.add(db_rule)
    
    await db.commit()
    return db_alert

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List alerts for current user"""
    query = select(Alert).where(Alert.owner_id == current_user.id)
    if active_only:
        query = query.where(Alert.is_active == True)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{alert_id}/history")
async def get_alert_history(
    alert_id: int,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alert notification history"""
    result = await db.execute(
        select(AlertNotification)
        .join(Alert)
        .where(AlertNotification.alert_id == alert_id, Alert.owner_id == current_user.id)
        .order_by(AlertNotification.triggered_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{alert_id}/test")
async def test_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test alert conditions"""
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id, Alert.owner_id == current_user.id)
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    test_result = await alert_service.test_alert(alert)
    return test_result

@router.post("/{alert_id}/acknowledge/{notification_id}")
async def acknowledge_alert(
    alert_id: int,
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge an alert notification"""
    result = await db.execute(
        select(AlertNotification)
        .join(Alert)
        .where(
            AlertNotification.id == notification_id,
            Alert.id == alert_id,
            Alert.owner_id == current_user.id
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.status = "acknowledged"
    notification.acknowledged_by = current_user.id
    notification.acknowledged_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Alert acknowledged"}

@router.get("/notifications/unread")
async def get_unread_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get unread alert notifications"""
    result = await db.execute(
        select(AlertNotification)
        .join(Alert)
        .where(
            Alert.owner_id == current_user.id,
            AlertNotification.status.in_(["pending", "sent"])
        )
        .order_by(AlertNotification.triggered_at.desc())
    )
    return result.scalars().all()
