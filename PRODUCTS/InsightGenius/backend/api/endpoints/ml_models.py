"""
ML Models API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.ml_model import MLModel
from models.dataset import Dataset
from services.ml_training import MLTrainingService
from services.anomaly_detection import AnomalyDetectionService
from schemas.ml_model import (
    MLModelCreate,
    MLModelResponse,
    TrainingRequest,
    AnomalyDetectionRequest
)

router = APIRouter()
ml_service = MLTrainingService()
anomaly_service = AnomalyDetectionService()

@router.get("/types")
async def get_model_types():
    """Get available ML model types"""
    return [
        {
            "type": "timeseries_forecast",
            "name": "Time Series Forecasting",
            "description": "Predict future values based on historical time-series data",
            "use_cases": ["Sales forecasting", "Demand prediction", "Stock price prediction"],
            "required_columns": ["timestamp", "target_value"],
            "algorithms": ["LSTM", "Prophet", "ARIMA", "Transformer"]
        },
        {
            "type": "classification",
            "name": "Classification",
            "description": "Categorize data into predefined classes",
            "use_cases": ["Churn prediction", "Fraud detection", "Sentiment analysis"],
            "required_columns": ["features", "target_class"],
            "algorithms": ["Random Forest", "XGBoost", "Neural Network", "SVM"]
        },
        {
            "type": "regression",
            "name": "Regression",
            "description": "Predict continuous numerical values",
            "use_cases": ["Price prediction", "Risk scoring", "Performance estimation"],
            "required_columns": ["features", "target_value"],
            "algorithms": ["Linear Regression", "XGBoost", "Neural Network", "Random Forest"]
        },
        {
            "type": "anomaly_detection",
            "name": "Anomaly Detection",
            "description": "Identify unusual patterns and outliers",
            "use_cases": ["Fraud detection", "System monitoring", "Quality control"],
            "required_columns": ["features"],
            "algorithms": ["Isolation Forest", "One-Class SVM", "Autoencoder", "LOF"]
        },
        {
            "type": "clustering",
            "name": "Clustering",
            "description": "Group similar data points together",
            "use_cases": ["Customer segmentation", "Market basket analysis", "Document clustering"],
            "required_columns": ["features"],
            "algorithms": ["K-Means", "DBSCAN", "Hierarchical", "Gaussian Mixture"]
        }
    ]

@router.post("/auto-recommend")
async def auto_recommend_model(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-recommend ML models based on dataset characteristics"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    recommendations = await ml_service.recommend_models(dataset)
    return recommendations

@router.post("/", response_model=MLModelResponse)
async def create_model(
    model: MLModelCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create and train a new ML model"""
    # Validate dataset
    result = await db.execute(
        select(Dataset).where(Dataset.id == model.dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Create model
    db_model = MLModel(
        name=model.name,
        description=model.description,
        model_type=model.model_type,
        dataset_id=model.dataset_id,
        feature_columns=model.feature_columns,
        target_column=model.target_column,
        time_column=model.time_column,
        hyperparameters=model.hyperparameters or {},
        training_config=model.training_config or {},
        status="pending"
    )
    db.add(db_model)
    await db.commit()
    await db.refresh(db_model)
    
    # Start training in background
    background_tasks.add_task(ml_service.train_model, db_model.id)
    
    return db_model

@router.post("/{model_id}/train")
async def train_model(
    model_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrain an existing model"""
    result = await db.execute(
        select(MLModel).where(MLModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model.status = "pending"
    await db.commit()
    
    background_tasks.add_task(ml_service.train_model, model.id)
    
    return {"message": "Training started", "model_id": model_id}

@router.get("/{model_id}/status")
async def get_training_status(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get model training status and metrics"""
    result = await db.execute(
        select(MLModel).where(MLModel.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return {
        "status": model.status,
        "training_metrics": model.training_metrics,
        "validation_metrics": model.validation_metrics,
        "feature_importance": model.feature_importance,
        "last_trained_at": model.last_trained_at
    }

@router.post("/{model_id}/predict")
async def make_prediction(
    model_id: int,
    input_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Make prediction using trained model"""
    result = await db.execute(
        select(MLModel).where(MLModel.id == model_id, MLModel.status == "ready")
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found or not ready")
    
    prediction = await ml_service.predict(model, input_data)
    return prediction

@router.post("/{model_id}/batch-predict")
async def batch_predict(
    model_id: int,
    input_data: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Batch predictions"""
    result = await db.execute(
        select(MLModel).where(MLModel.id == model_id, MLModel.status == "ready")
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found or not ready")
    
    predictions = await ml_service.batch_predict(model, input_data)
    return {"predictions": predictions}

@router.post("/anomaly/detect")
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run anomaly detection on dataset"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == request.dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    anomalies = await anomaly_service.detect_anomalies(
        dataset,
        request.columns,
        request.sensitivity,
        request.time_window
    )
    
    return {
        "anomaly_count": len(anomalies),
        "anomalies": anomalies[:100],  # Limit results
        "summary": {
            "total_points": len(dataset.sample_data) if dataset.sample_data else 0,
            "anomaly_rate": len(anomalies) / len(dataset.sample_data) if dataset.sample_data else 0
        }
    }

@router.get("/anomaly/history/{dataset_id}")
async def get_anomaly_history(
    dataset_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical anomaly detection results"""
    from models.ml_model import AnomalyDetectionResult
    
    result = await db.execute(
        select(AnomalyDetectionResult)
        .where(AnomalyDetectionResult.dataset_id == dataset_id)
        .order_by(AnomalyDetectionResult.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()
