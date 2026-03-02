"""
User Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company = Column(String)
    role = Column(String, default="user")  # user, admin, viewer
    
    # Preferences
    preferences = Column(JSON, default={
        "theme": "dark",
        "default_dashboard": None,
        "email_notifications": True,
        "alert_channels": ["email"]
    })
    
    # Subscription
    plan = Column(String, default="free")  # free, pro, enterprise
    subscription_expires_at = Column(DateTime)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    data_sources = relationship("DataSource", back_populates="owner")
    dashboards = relationship("Dashboard", back_populates="owner")
    reports = relationship("Report", back_populates="owner")
    alerts = relationship("Alert", back_populates="owner")
