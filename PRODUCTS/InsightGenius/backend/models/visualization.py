"""
Visualization Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base

class Visualization(Base):
    __tablename__ = "visualizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Source
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", back_populates="visualizations")
    
    # Chart configuration
    chart_type = Column(String, nullable=False)  # line, bar, pie, scatter, area, heatmap, funnel, gauge, combo, custom
    config = Column(JSON, nullable=False)
    
    # AI-generated
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)
    
    # Cache
    last_rendered_at = Column(DateTime)
    render_cache = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chart_config = relationship("ChartConfig", back_populates="visualization", uselist=False)

class ChartConfig(Base):
    __tablename__ = "chart_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    visualization_id = Column(Integer, ForeignKey("visualizations.id"))
    visualization = relationship("Visualization", back_populates="chart_config")
    
    # Dimensions
    x_axis = Column(JSON)  # {column, type, format}
    y_axis = Column(JSON)  # [{column, aggregation, type, format}]
    
    # Series
    series = Column(JSON, default=[])  # For multi-series charts
    color_by = Column(String)  # Column for color encoding
    size_by = Column(String)  # Column for size encoding (bubble charts)
    
    # Filters
    filters = Column(JSON, default=[])
    
    # Styling
    colors = Column(JSON, default=[])
    show_legend = Column(String, default="auto")  # yes, no, auto
    legend_position = Column(String, default="right")
    
    # Axes configuration
    x_axis_label = Column(String)
    y_axis_label = Column(String)
    x_axis_format = Column(String)
    y_axis_format = Column(String)
    
    # Interactions
    enable_zoom = Column(String, default="yes")  # yes, no
    enable_tooltip = Column(String, default="yes")
    enable_brush = Column(String, default="no")
    
    # Annotations
    annotations = Column(JSON, default=[])
    reference_lines = Column(JSON, default=[])
    
    # Advanced
    custom_d3_config = Column(JSON)
