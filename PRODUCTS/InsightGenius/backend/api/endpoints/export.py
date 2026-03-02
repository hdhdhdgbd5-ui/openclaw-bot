"""
Export API Endpoints
PDF, PowerPoint, Excel, CSV exports
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.dashboard import Dashboard
from models.dataset import Dataset
from services.export_service import ExportService

router = APIRouter()
export_service = ExportService()

@router.post("/dashboard/{dashboard_id}/pdf")
async def export_dashboard_pdf(
    dashboard_id: int,
    include_raw_data: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export dashboard to PDF"""
    result = await db.execute(
        select(Dashboard).where(
            (Dashboard.id == dashboard_id) & 
            ((Dashboard.owner_id == current_user.id) | (Dashboard.is_public == True))
        )
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    file_path = await export_service.export_dashboard_to_pdf(dashboard, include_raw_data)
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"{dashboard.name.replace(' ', '_')}_report.pdf"
    )

@router.post("/dashboard/{dashboard_id}/pptx")
async def export_dashboard_pptx(
    dashboard_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export dashboard to PowerPoint"""
    result = await db.execute(
        select(Dashboard).where(
            (Dashboard.id == dashboard_id) & 
            ((Dashboard.owner_id == current_user.id) | (Dashboard.is_public == True))
        )
    )
    dashboard = result.scalar_one_or_none()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    file_path = await export_service.export_dashboard_to_pptx(dashboard)
    
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"{dashboard.name.replace(' ', '_')}_presentation.pptx"
    )

@router.post("/dataset/{dataset_id}/excel")
async def export_dataset_excel(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export dataset to Excel"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = await export_service.export_dataset_to_excel(dataset)
    
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{dataset.name.replace(' ', '_')}_data.xlsx"
    )

@router.post("/dataset/{dataset_id}/csv")
async def export_dataset_csv(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export dataset to CSV"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    file_path = await export_service.export_dataset_to_csv(dataset)
    
    return FileResponse(
        file_path,
        media_type="text/csv",
        filename=f"{dataset.name.replace(' ', '_')}_data.csv"
    )

@router.post("/visualization/{viz_id}/image")
async def export_visualization_image(
    viz_id: int,
    format: str = "png",  # png, svg, jpg
    width: int = 1200,
    height: int = 800,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export visualization as image"""
    from models.visualization import Visualization
    
    result = await db.execute(
        select(Visualization).where(Visualization.id == viz_id)
    )
    viz = result.scalar_one_or_none()
    if not viz:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    file_path = await export_service.export_visualization_to_image(viz, format, width, height)
    
    media_types = {
        "png": "image/png",
        "svg": "image/svg+xml",
        "jpg": "image/jpeg"
    }
    
    return FileResponse(
        file_path,
        media_type=media_types.get(format, "image/png"),
        filename=f"{viz.name.replace(' ', '_')}.{format}"
    )
