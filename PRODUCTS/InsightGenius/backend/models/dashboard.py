"""
Dashboard Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from core.database import Base

class Dashboard(Base):
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Layout
    layout = Column(JSON, default={
        "type": "grid",
        "columns": 12,
        "rowHeight": 80,
        "padding": 16
    })
    
    # Style
    theme = Column(String, default="dark")
    background_color = Column(String, default="#0f172a")
    
    # Filters
    global_filters = Column(JSON, default=[])
    
    # Sharing
    is_public = Column(Boolean, default=False)
    public_share_id = Column(String, unique=True)
    allowed_emails = Column(JSON, default=[])
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="dashboards")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_viewed_at = Column(DateTime)
    
    # Relationships
    widgets = relationship("DashboardWidget", back_populates="dashboard", cascade="all, delete-orphan")

class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"
    
    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"))
    dashboard = relationship("Dashboard", back_populates="widgets")
    
    # Position
    x = Column(Integer, default=0)
    y = Column(Integer, default=0)
    w = Column(Integer, default=4)
    h = Column(Integer, default=4)
    
    # Content
    widget_type = Column(String, nullable=False)  # chart, metric, table, text, filter, ai_insight
    title = Column(String)
    
    # Configuration
    config = Column(JSON, default={})
    
    # Data source
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    visualization_id = Column(Integer, ForeignKey("visualizations.id"))
    
    # Real-time
    refresh_interval = Column(Integer, default=0)  # seconds, 0 = manual
    last_refresh = Column(DateTime)
    
    # AI features
    ai_insights_enabled = Column(Boolean, default=False)
    ai_insights_config = Column(JSON, default={})
    
    order = Column(Integer, default=0)
