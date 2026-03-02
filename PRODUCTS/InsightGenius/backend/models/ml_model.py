"""
ML Model and Prediction Models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from core.database import Base

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Model type
    model_type = Column(String, nullable=False)  # timeseries_forecast, classification, regression, clustering, anomaly_detection
    
    # Dataset
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", back_populates="ml_models")
    
    # Features
    feature_columns = Column(JSON, nullable=False)
    target_column = Column(String)
    time_column = Column(String)  # For time series
    
    # Configuration
    hyperparameters = Column(JSON, default={})
    training_config = Column(JSON, default={
        "test_size": 0.2,
        "validation_size": 0.1,
        "epochs": 100,
        "early_stopping": True
    })
    
    # Model artifact
    model_path = Column(String)
    preprocessing_pipeline_path = Column(String)
    
    # Metrics
    training_metrics = Column(JSON)
    validation_metrics = Column(JSON)
    feature_importance = Column(JSON)
    
    # Status
    status = Column(String, default="pending")  # pending, training, ready, failed
    training_error = Column(Text)
    
    # Auto-train settings
    auto_retrain = Column(Boolean, default=False)
    retrain_schedule = Column(String)  # daily, weekly
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_trained_at = Column(DateTime)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="model")
    anomalies = relationship("AnomalyDetectionResult", back_populates="model")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"))
    model = relationship("MLModel", back_populates="predictions")
    
    # Input
    input_data = Column(JSON)
    
    # Output
    prediction_value = Column(Float)
    prediction_confidence = Column(Float)
    prediction_interval_lower = Column(Float)
    prediction_interval_upper = Column(Float)
    
    # For classification
    predicted_class = Column(String)
    class_probabilities = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Feedback (for model improvement)
    actual_value = Column(Float)
    feedback_submitted = Column(Boolean, default=False)

class AnomalyDetectionResult(Base):
    __tablename__ = "anomaly_detection_results"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml_models.id"))
    model = relationship("MLModel", back_populates="anomalies")
    
    # Data point info
    timestamp = Column(DateTime, default=datetime.utcnow)
    data_point_id = Column(String)  # Row identifier
    
    # Anomaly score
    anomaly_score = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, nullable=False)
    severity = Column(String)  # low, medium, high, critical
    
    # Affected columns
    affected_columns = Column(JSON)
    column_scores = Column(JSON)
    
    # Explanation
    explanation = Column(Text)
    suggested_action = Column(Text)
    
    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"))
    acknowledged_at = Column(DateTime)
    
    # Raw data snapshot
    data_snapshot = Column(JSON)
