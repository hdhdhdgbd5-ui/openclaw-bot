"""
Visualizations API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.visualization import Visualization, ChartConfig
from models.dataset import Dataset
from services.visualization import VisualizationService
from services.ai_chart_recommender import AIChartRecommender
from schemas.visualization import (
    VisualizationCreate,
    VisualizationUpdate,
    VisualizationResponse,
    AutoVizRequest,
    AIChartRecommendation
)

router = APIRouter()
viz_service = VisualizationService()
ai_recommender = AIChartRecommender()

@router.post("/auto-generate")
async def auto_generate_visualizations(
    request: AutoVizRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-generate visualizations for a dataset"""
    # Get dataset
    result = await db.execute(
        select(Dataset).where(Dataset.id == request.dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Generate recommendations
    recommendations = await ai_recommender.recommend_charts(dataset)
    
    # Create visualizations
    created_vizs = []
    for rec in recommendations[:request.max_charts or 6]:
        viz = Visualization(
            name=rec.title,
            description=rec.description,
            dataset_id=dataset.id,
            chart_type=rec.chart_type,
            config=rec.config,
            ai_generated=True,
            ai_prompt=request.context
        )
        db.add(viz)
        created_vizs.append(viz)
    
    await db.commit()
    
    return {
        "message": f"Generated {len(created_vizs)} visualizations",
        "visualizations": created_vizs
    }

@router.post("/ai-recommend")
async def ai_recommend_chart(
    dataset_id: int,
    natural_language_request: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI chart recommendation from natural language"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    recommendation = await ai_recommender.recommend_from_nlp(
        dataset, 
        natural_language_request
    )
    
    return recommendation

@router.get("/dataset/{dataset_id}", response_model=List[VisualizationResponse])
async def list_dataset_visualizations(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List visualizations for a dataset"""
    result = await db.execute(
        select(Visualization).where(Visualization.dataset_id == dataset_id)
    )
    return result.scalars().all()

@router.post("/", response_model=VisualizationResponse)
async def create_visualization(
    viz: VisualizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new visualization"""
    db_viz = Visualization(
        name=viz.name,
        description=viz.description,
        dataset_id=viz.dataset_id,
        chart_type=viz.chart_type,
        config=viz.config,
        ai_generated=False
    )
    db.add(db_viz)
    await db.commit()
    await db.refresh(db_viz)
    return db_viz

@router.get("/{viz_id}/render")
async def render_visualization(
    viz_id: int,
    format: str = "json",  # json, html, png, svg
    width: int = 800,
    height: int = 600,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Render visualization data"""
    result = await db.execute(
        select(Visualization).where(Visualization.id == viz_id)
    )
    viz = result.scalar_one_or_none()
    if not viz:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    render_result = await viz_service.render(viz, format, width, height)
    return render_result

@router.get("/{viz_id}/d3-config")
async def get_d3_configuration(
    viz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get D3.js configuration for frontend rendering"""
    result = await db.execute(
        select(Visualization).where(Visualization.id == viz_id)
    )
    viz = result.scalar_one_or_none()
    if not viz:
        raise HTTPException(status_code=404, detail="Visualization not found")
    
    d3_config = await viz_service.generate_d3_config(viz)
    return d3_config
