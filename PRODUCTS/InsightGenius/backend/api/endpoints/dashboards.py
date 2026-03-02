"""
Dashboards API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.dashboard import Dashboard, DashboardWidget
from services.dashboard import DashboardService
from schemas.dashboard import (
    DashboardCreate,
    DashboardUpdate,
    DashboardResponse,
    WidgetCreate,
    WidgetUpdate,
    ShareDashboardRequest
)

router = APIRouter()
dashboard_service = DashboardService()

@router.get("/", response_model=List[DashboardResponse])
async def list_dashboards(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List dashboards for current user"""
    result = await db.execute(
        select(Dashboard)
        .where(Dashboard.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=DashboardResponse)
async def create_dashboard(
    dashboard: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dashboard"""
    db_dashboard = Dashboard(
        name=dashboard.name,
        description=dashboard.description,
        layout=dashboard.layout,
        theme=dashboard.theme,
        owner_id=current_user.id
    )
    db.add(db_dashboard)
    await db.commit()
    await db.refresh(db_dashboard)
    return db_dashboard

@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard with all widgets"""
    result = await db.execute(
        select(Dashboard).where(
            (Dashboard.id == dashboard_id) & 
            ((Dashboard.owner_id == current_user.id) | (Dashboard.is_public == True))
        )
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Update last viewed
    dashboard.last_viewed_at = datetime.utcnow()
    await db.commit()
    
    return dashboard

@router.post("/{dashboard_id}/widgets")
async def add_widget(
    dashboard_id: int,
    widget: WidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add widget to dashboard"""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id)
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    db_widget = DashboardWidget(
        dashboard_id=dashboard_id,
        widget_type=widget.widget_type,
        title=widget.title,
        x=widget.x,
        y=widget.y,
        w=widget.w,
        h=widget.h,
        config=widget.config,
        dataset_id=widget.dataset_id,
        visualization_id=widget.visualization_id,
        refresh_interval=widget.refresh_interval,
        ai_insights_enabled=widget.ai_insights_enabled
    )
    db.add(db_widget)
    await db.commit()
    await db.refresh(db_widget)
    return db_widget

@router.post("/{dashboard_id}/share")
async def share_dashboard(
    dashboard_id: int,
    share_request: ShareDashboardRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Share dashboard publicly or with specific emails"""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id)
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    dashboard.is_public = share_request.is_public
    dashboard.allowed_emails = share_request.allowed_emails
    
    if share_request.is_public and not dashboard.public_share_id:
        import uuid
        dashboard.public_share_id = str(uuid.uuid4())
    
    await db.commit()
    
    return {
        "message": "Dashboard sharing updated",
        "public_url": f"/share/{dashboard.public_share_id}" if dashboard.is_public else None,
        "share_id": dashboard.public_share_id
    }

@router.get("/share/{share_id}")
async def get_shared_dashboard(
    share_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public/shared dashboard"""
    result = await db.execute(
        select(Dashboard).where(Dashboard.public_share_id == share_id, Dashboard.is_public == True)
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found or not public")
    
    return dashboard

@router.post("/{dashboard_id}/ai-layout")
async def ai_optimize_layout(
    dashboard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI-optimize dashboard layout"""
    result = await db.execute(
        select(Dashboard).where(Dashboard.id == dashboard_id, Dashboard.owner_id == current_user.id)
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    optimized_layout = await dashboard_service.ai_optimize_layout(dashboard)
    dashboard.layout = optimized_layout
    await db.commit()
    
    return {"message": "Layout optimized", "layout": optimized_layout}
