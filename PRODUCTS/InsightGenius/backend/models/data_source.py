"""
Data Source Model
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from core.database import Base

class DataSourceType(str, PyEnum):
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    API_REST = "api_rest"
    API_GRAPHQL = "api_graphql"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"
    SALESFORCE = "salesforce"
    GOOGLE_SHEETS = "google_sheets"

class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_type = Column(Enum(DataSourceType), nullable=False)
    
    # Connection details (encrypted)
    connection_config = Column(JSON, nullable=False)
    
    # Sync settings
    sync_enabled = Column(String, default="manual")  # manual, hourly, daily, realtime
    last_sync_at = Column(DateTime)
    sync_status = Column(String, default="pending")  # pending, syncing, success, error
    sync_error = Column(Text)
    
    # Schema cache
    schema_cache = Column(JSON)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="data_sources")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    datasets = relationship("Dataset", back_populates="data_source")
