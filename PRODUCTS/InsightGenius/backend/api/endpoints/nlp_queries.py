"""
NLP Queries API Endpoints
Natural Language to SQL/Analytics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.dataset import Dataset
from models.dashboard import Dashboard
from services.nlp_query import NLPQueryEngine

router = APIRouter()
nlp_engine = NLPQueryEngine()

@router.post("/ask")
async def natural_language_query(
    query: str,
    dataset_id: int = None,
    dashboard_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process natural language query
    Examples:
    - "Show me sales by region last quarter"
    - "What's the trend of revenue over time?"
    - "Compare this month vs last month"
    - "Which products have declining sales?"
    """
    context = None
    
    if dataset_id:
        result = await db.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        context = result.scalar_one_or_none()
    elif dashboard_id:
        result = await db.execute(
            select(Dashboard).where(Dashboard.id == dashboard_id)
        )
        context = result.scalar_one_or_none()
    
    response = await nlp_engine.process_query(query, context, current_user)
    return response

@router.post("/suggest")
async def suggest_queries(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suggest natural language queries based on dataset"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    suggestions = await nlp_engine.generate_suggestions(dataset)
    return {"suggestions": suggestions}

@router.post("/explain")
async def explain_data(
    dataset_id: int,
    question: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI explanation of data insights"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    explanation = await nlp_engine.explain_dataset(dataset, question)
    return explanation

@router.post("/insights/auto")
async def auto_insights(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Automatically generate insights from dataset"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    insights = await nlp_engine.generate_auto_insights(dataset)
    return {
        "insights": insights,
        "generated_at": datetime.utcnow().isoformat()
    }
