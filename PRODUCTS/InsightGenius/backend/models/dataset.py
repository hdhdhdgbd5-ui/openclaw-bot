"""
Dataset Model
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # Source reference
    data_source_id = Column(Integer, ForeignKey("data_sources.id"))
    data_source = relationship("DataSource", back_populates="datasets")
    source_table_or_query = Column(String)  # Table name or SQL query
    
    # Data storage
    storage_type = Column(String, default="cache")  # cache, materialized, virtual
    row_count = Column(BigInteger, default=0)
    size_bytes = Column(BigInteger, default=0)
    
    # Schema
    columns = relationship("DatasetColumn", back_populates="dataset")
    schema_version = Column(String, default="1.0")
    
    # Data sample (for preview)
    sample_data = Column(JSON)
    
    # Metadata
    tags = Column(JSON, default=[])
    category = Column(String)
    
    # Processing status
    processing_status = Column(String, default="pending")
    last_processed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    visualizations = relationship("Visualization", back_populates="dataset")
    ml_models = relationship("MLModel", back_populates="dataset")

class DatasetColumn(Base):
    __tablename__ = "dataset_columns"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    dataset = relationship("Dataset", back_populates="columns")
    
    name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # string, integer, float, date, datetime, boolean
    
    # Statistics (computed)
    statistics = Column(JSON)  # min, max, mean, unique_count, null_count, etc.
    
    # ML features
    is_feature = Column(String, default="auto")  # yes, no, auto
    is_target = Column(Boolean, default=False)
    
    # UI
    display_name = Column(String)
    description = Column(Text)
    order = Column(Integer, default=0)
