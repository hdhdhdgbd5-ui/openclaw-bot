"""
Pydantic Schemas
Request and Response models
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

# Auth Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    company: Optional[str]
    plan: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

# Data Source Schemas
class DataSourceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: str
    connection_config: Dict[str, Any]
    sync_enabled: str = "manual"

class DataSourceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    connection_config: Optional[Dict[str, Any]] = None
    sync_enabled: Optional[str] = None

class DataSourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_type: str
    sync_enabled: str
    last_sync_at: Optional[datetime]
    sync_status: str
    created_at: datetime

class DataSourceTest(BaseModel):
    success: bool
    message: str

class DataPreview(BaseModel):
    columns: List[str]
    data: List[Dict]
    total_rows: int

# Dataset Schemas
class DatasetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data_source_id: int
    source_table_or_query: Optional[str] = None

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None

class DatasetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    data_source_id: int
    row_count: int
    processing_status: str
    created_at: datetime

class ColumnStats(BaseModel):
    name: str
    data_type: str
    statistics: Dict[str, Any]

# Visualization Schemas
class VisualizationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dataset_id: int
    chart_type: str
    config: Dict[str, Any]

class VisualizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class VisualizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    dataset_id: int
    chart_type: str
    config: Dict[str, Any]
    ai_generated: bool
    created_at: datetime

class AutoVizRequest(BaseModel):
    dataset_id: int
    max_charts: int = 6
    context: Optional[str] = None

class AIChartRecommendation(BaseModel):
    chart_type: str
    title: str
    description: str
    confidence: float
    suggested_columns: Dict[str, Any]

# Dashboard Schemas
class DashboardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    theme: str = "dark"

class DashboardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None
    global_filters: Optional[List[Dict]] = None

class DashboardResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    layout: Dict[str, Any]
    theme: str
    is_public: bool
    created_at: datetime
    updated_at: datetime

class WidgetCreate(BaseModel):
    widget_type: str
    title: Optional[str] = None
    x: int = 0
    y: int = 0
    w: int = 4
    h: int = 4
    config: Dict[str, Any] = {}
    dataset_id: Optional[int] = None
    visualization_id: Optional[int] = None
    refresh_interval: int = 0
    ai_insights_enabled: bool = False

class WidgetUpdate(BaseModel):
    title: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    w: Optional[int] = None
    h: Optional[int] = None
    config: Optional[Dict[str, Any]] = None

class ShareDashboardRequest(BaseModel):
    is_public: bool = False
    allowed_emails: List[str] = []

# ML Model Schemas
class MLModelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    model_type: str
    dataset_id: int
    feature_columns: List[str]
    target_column: Optional[str] = None
    time_column: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    training_config: Optional[Dict[str, Any]] = None

class MLModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    model_type: str
    dataset_id: int
    status: str
    created_at: datetime
    last_trained_at: Optional[datetime]

class TrainingRequest(BaseModel):
    epochs: Optional[int] = None
    validation_split: Optional[float] = None

class AnomalyDetectionRequest(BaseModel):
    dataset_id: int
    columns: List[str]
    sensitivity: str = "medium"
    time_window: str = "1d"

# Alert Schemas
class AlertRuleCreate(BaseModel):
    condition_type: str
    metric_column: Optional[str] = None
    aggregation: Optional[str] = None
    operator: Optional[str] = None
    threshold_value: Optional[float] = None
    anomaly_sensitivity: Optional[str] = None
    trend_direction: Optional[str] = None
    custom_condition: Optional[str] = None
    lookback_window: str = "1h"
    cooldown_minutes: int = 60

class AlertCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dataset_id: Optional[int] = None
    dashboard_id: Optional[int] = None
    severity: str = "medium"
    rules: List[AlertRuleCreate]

class AlertUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    severity: Optional[str] = None

class AlertResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    severity: str
    is_active: bool
    created_at: datetime

# Report Schemas
class ReportCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: str = "dashboard"
    source_id: int
    sections: List[Dict[str, Any]] = []
    formats: List[str] = ["pdf"]
    template: str = "modern"
    include_raw_data: bool = False
    branding: Optional[Dict[str, Any]] = None

class ReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sections: Optional[List[Dict[str, Any]]] = None
    formats: Optional[List[str]] = None

class ReportResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    report_type: str
    formats: List[str]
    created_at: datetime

class ScheduledReportCreate(BaseModel):
    name: str
    frequency: str
    cron_expression: Optional[str] = None
    recipients: List[str]
    subject: Optional[str] = None
    message: Optional[str] = None
