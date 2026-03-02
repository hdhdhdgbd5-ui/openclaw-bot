"""
Predictions API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.ml_model import MLModel, Prediction

router = APIRouter()

@router.get("/model/{model_id}")
async def get_model_predictions(
    model_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prediction history for a model"""
    result = await db.execute(
        select(Prediction)
        .join(MLModel)
        .where(Prediction.model_id == model_id)
        .order_by(Prediction.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/{prediction_id}/feedback")
async def submit_feedback(
    prediction_id: int,
    actual_value: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback on prediction accuracy"""
    result = await db.execute(
        select(Prediction).where(Prediction.id == prediction_id)
    )
    prediction = result.scalar_one_or_none()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    prediction.actual_value = actual_value
    prediction.feedback_submitted = True
    await db.commit()
    
    return {"message": "Feedback recorded"}

@router.get("/model/{model_id}/accuracy")
async def get_model_accuracy(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get model accuracy metrics based on feedback"""
    result = await db.execute(
        select(Prediction)
        .where(
            Prediction.model_id == model_id,
            Prediction.feedback_submitted == True
        )
    )
    predictions = result.scalars().all()
    
    if not predictions:
        return {"message": "No feedback data available"}
    
    # Calculate accuracy metrics
    errors = []
    for p in predictions:
        if p.actual_value is not None:
            errors.append(abs(p.prediction_value - p.actual_value))
    
    if not errors:
        return {"message": "No feedback data available"}
    
    import numpy as np
    
    return {
        "mae": float(np.mean(errors)),
        "rmse": float(np.sqrt(np.mean([e**2 for e in errors]))),
        "feedback_count": len(errors)
    }
