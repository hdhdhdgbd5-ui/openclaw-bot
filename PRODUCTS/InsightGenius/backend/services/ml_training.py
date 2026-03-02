"""
ML Training Service
Handles model training, prediction, and management
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

from core.logging import logger
from core.config import settings

class MLTrainingService:
    """Service for training and managing ML models"""
    
    def __init__(self):
        self.models_dir = settings.MODEL_CACHE_DIR
        os.makedirs(self.models_dir, exist_ok=True)
        
        self.algorithms = {
            "regression": {
                "linear": LinearRegression,
                "random_forest": RandomForestRegressor,
            },
            "classification": {
                "logistic": LogisticRegression,
                "random_forest": RandomForestClassifier,
            },
            "clustering": {
                "kmeans": KMeans,
            }
        }
    
    async def recommend_models(self, dataset) -> List[Dict]:
        """Recommend ML models based on dataset characteristics"""
        try:
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            if df.empty:
                return []
            
            recommendations = []
            
            # Analyze columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
            dt_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()
            
            # Time series recommendation
            if dt_cols and numeric_cols:
                recommendations.append({
                    "type": "timeseries_forecast",
                    "name": "Time Series Forecasting",
                    "confidence": 0.9 if len(df) > 100 else 0.7,
                    "reason": f"Detected datetime column '{dt_cols[0]}' and numeric columns suitable for forecasting",
                    "target_column": numeric_cols[0],
                    "time_column": dt_cols[0]
                })
            
            # Classification recommendation
            if cat_cols:
                for col in cat_cols:
                    unique_count = df[col].nunique()
                    if 2 <= unique_count <= 20:
                        recommendations.append({
                            "type": "classification",
                            "name": f"Classification - Predict {col}",
                            "confidence": 0.85 if unique_count <= 10 else 0.7,
                            "reason": f"'{col}' has {unique_count} categories, suitable for classification",
                            "target_column": col,
                            "feature_columns": [c for c in numeric_cols if c != col][:10]
                        })
            
            # Regression recommendation
            if len(numeric_cols) >= 2:
                recommendations.append({
                    "type": "regression",
                    "name": f"Regression - Predict {numeric_cols[0]}",
                    "confidence": 0.8,
                    "reason": f"Multiple numeric columns detected, can predict '{numeric_cols[0]}' from others",
                    "target_column": numeric_cols[0],
                    "feature_columns": numeric_cols[1:11]
                })
            
            # Clustering recommendation
            if len(numeric_cols) >= 2:
                recommendations.append({
                    "type": "clustering",
                    "name": "Customer/Pattern Segmentation",
                    "confidence": 0.75,
                    "reason": f"{len(numeric_cols)} numeric features available for clustering analysis",
                    "feature_columns": numeric_cols[:10]
                })
            
            # Anomaly detection
            if numeric_cols:
                recommendations.append({
                    "type": "anomaly_detection",
                    "name": "Anomaly Detection",
                    "confidence": 0.8,
                    "reason": "Numeric data suitable for outlier detection",
                    "feature_columns": numeric_cols[:5]
                })
            
            return sorted(recommendations, key=lambda x: x["confidence"], reverse=True)
            
        except Exception as e:
            logger.error(f"Model recommendation failed: {e}")
            return []
    
    async def train_model(self, model_id: int):
        """Train an ML model"""
        try:
            # This runs in background task
            from core.database import AsyncSessionLocal
            from models.ml_model import MLModel
            from sqlalchemy import select
            
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(MLModel).where(MLModel.id == model_id)
                )
                model = result.scalar_one_or_none()
                
                if not model:
                    return
                
                # Update status
                model.status = "training"
                await db.commit()
                
                # Get dataset data
                # TODO: Load actual dataset
                # For now, create synthetic data for demonstration
                np.random.seed(42)
                n_samples = 1000
                
                feature_cols = model.feature_columns
                target_col = model.target_column
                
                # Create synthetic data
                X = np.random.randn(n_samples, len(feature_cols))
                
                if model.model_type == "regression":
                    y = X[:, 0] * 2 + X[:, 1] * 0.5 + np.random.randn(n_samples) * 0.1
                elif model.model_type == "classification":
                    y = (X[:, 0] + X[:, 1] > 0).astype(int)
                elif model.model_type == "timeseries_forecast":
                    # Time series data
                    dates = pd.date_range("2024-01-01", periods=n_samples, freq="H")
                    trend = np.linspace(100, 200, n_samples)
                    seasonal = 20 * np.sin(2 * np.pi * np.arange(n_samples) / 24)
                    y = trend + seasonal + np.random.randn(n_samples) * 5
                else:
                    y = np.random.randn(n_samples)
                
                # Train/test split
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model based on type
                if model.model_type == "regression":
                    clf = RandomForestRegressor(n_estimators=100, random_state=42)
                    clf.fit(X_train_scaled, y_train)
                    
                    # Evaluate
                    y_pred = clf.predict(X_test_scaled)
                    metrics = {
                        "mse": float(mean_squared_error(y_test, y_pred)),
                        "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
                        "r2": float(r2_score(y_test, y_pred)),
                        "mae": float(np.mean(np.abs(y_test - y_pred)))
                    }
                
                elif model.model_type == "classification":
                    clf = RandomForestClassifier(n_estimators=100, random_state=42)
                    clf.fit(X_train_scaled, y_train)
                    
                    y_pred = clf.predict(X_test_scaled)
                    metrics = {
                        "accuracy": float(accuracy_score(y_test, y_pred)),
                        "classification_report": classification_report(y_test, y_pred, output_dict=True)
                    }
                
                elif model.model_type == "clustering":
                    clf = KMeans(n_clusters=3, random_state=42)
                    clf.fit(X_train_scaled)
                    metrics = {
                        "inertia": float(clf.inertia_),
                        "n_clusters": 3
                    }
                
                else:
                    # Default to regression
                    clf = RandomForestRegressor(n_estimators=100, random_state=42)
                    clf.fit(X_train_scaled, y_train)
                    y_pred = clf.predict(X_test_scaled)
                    metrics = {
                        "mse": float(mean_squared_error(y_test, y_pred)),
                        "r2": float(r2_score(y_test, y_pred))
                    }
                
                # Save model
                model_path = f"{self.models_dir}/model_{model_id}.joblib"
                scaler_path = f"{self.models_dir}/scaler_{model_id}.joblib"
                
                joblib.dump(clf, model_path)
                joblib.dump(scaler, scaler_path)
                
                # Feature importance
                if hasattr(clf, 'feature_importances_'):
                    feature_importance = {
                        feature_cols[i]: float(clf.feature_importances_[i])
                        for i in range(len(feature_cols))
                    }
                else:
                    feature_importance = {}
                
                # Update model record
                model.status = "ready"
                model.model_path = model_path
                model.preprocessing_pipeline_path = scaler_path
                model.training_metrics = metrics
                model.validation_metrics = metrics
                model.feature_importance = feature_importance
                model.last_trained_at = datetime.utcnow()
                
                await db.commit()
                
                logger.info(f"Model {model_id} training completed")
                
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            
            # Update status to failed
            from core.database import AsyncSessionLocal
            from models.ml_model import MLModel
            from sqlalchemy import select
            
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(MLModel).where(MLModel.id == model_id)
                )
                model = result.scalar_one_or_none()
                if model:
                    model.status = "failed"
                    model.training_error = str(e)
                    await db.commit()
    
    async def predict(self, model, input_data: Dict) -> Dict:
        """Make prediction using trained model"""
        try:
            if model.status != "ready":
                return {"error": "Model not ready"}
            
            # Load model
            clf = joblib.load(model.model_path)
            scaler = joblib.load(model.preprocessing_pipeline_path)
            
            # Prepare input
            features = []
            for col in model.feature_columns:
                features.append(input_data.get(col, 0))
            
            X = np.array([features])
            X_scaled = scaler.transform(X)
            
            # Predict
            if model.model_type == "classification":
                prediction = clf.predict(X_scaled)[0]
                probabilities = clf.predict_proba(X_scaled)[0]
                
                return {
                    "predicted_class": str(prediction),
                    "class_probabilities": {
                        str(i): float(p) for i, p in enumerate(probabilities)
                    },
                    "confidence": float(max(probabilities))
                }
            else:
                prediction = clf.predict(X_scaled)[0]
                
                # Calculate confidence interval (simplified)
                if hasattr(clf, 'estimators_'):
                    predictions = [est.predict(X_scaled)[0] for est in clf.estimators_]
                    std = np.std(predictions)
                else:
                    std = 0
                
                return {
                    "prediction": float(prediction),
                    "confidence": None,
                    "prediction_interval": {
                        "lower": float(prediction - 1.96 * std),
                        "upper": float(prediction + 1.96 * std)
                    }
                }
                
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {"error": str(e)}
    
    async def batch_predict(self, model, input_data_list: List[Dict]) -> List[Dict]:
        """Batch predictions"""
        results = []
        for input_data in input_data_list:
            result = await self.predict(model, input_data)
            results.append(result)
        return results
