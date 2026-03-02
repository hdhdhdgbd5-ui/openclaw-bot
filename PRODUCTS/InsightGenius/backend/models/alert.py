"""
Alert Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Source
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    
    # Status
    is_active = Column(Boolean, default=True)
    severity = Column(String, default="medium")  # low, medium, high, critical
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="alerts")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rules = relationship("AlertRule", back_populates="alert", cascade="all, delete-orphan")
    notifications = relationship("AlertNotification", back_populates="alert")

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    alert = relationship("Alert", back_populates="rules")
    
    # Condition
    condition_type = Column(String, nullable=False)  # threshold, anomaly, trend, custom
    
    # For threshold conditions
    metric_column = Column(String)
    aggregation = Column(String, default="value")  # value, sum, avg, count, min, max
    operator = Column(String)  # >, <, >=, <=, ==, !=, between
    threshold_value = Column(Float)
    threshold_value_max = Column(Float)  # For between operator
    
    # For anomaly detection
    anomaly_sensitivity = Column(String, default="medium")  # low, medium, high
    
    # For trend detection
    trend_direction = Column(String)  # increasing, decreasing
    trend_period = Column(String, default="7d")  # 1d, 7d, 30d
    trend_percentage = Column(Float)  # % change threshold
    
    # Custom condition (SQL or expression)
    custom_condition = Column(Text)
    
    # Time window
    lookback_window = Column(String, default="1h")  # 1h, 1d, 7d
    min_occurrences = Column(Integer, default=1)
    
    # Cooldown
    cooldown_minutes = Column(Integer, default=60)

class AlertNotification(Base):
    __tablename__ = "alert_notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    alert = relationship("Alert", back_populates="notifications")
    
    # Trigger info
    triggered_at = Column(DateTime, default=datetime.utcnow)
    triggered_value = Column(Float)
    message = Column(Text)
    
    # Data snapshot
    snapshot_data = Column(JSON)
    
    # Status
    status = Column(String, default="pending")  # pending, sent, acknowledged, resolved
    resolved_at = Column(DateTime)
    
    # Delivery
    channels_sent = Column(JSON, default=[])
    delivery_errors = Column(JSON, default=[])
