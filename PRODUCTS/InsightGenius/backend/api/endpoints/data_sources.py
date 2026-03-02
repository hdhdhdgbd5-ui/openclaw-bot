"""
Data Sources API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
import io

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.data_source import DataSource, DataSourceType
from services.data_connector import DataConnectorService
from schemas.data_source import (
    DataSourceCreate,
    DataSourceUpdate,
    DataSourceResponse,
    DataSourceTest,
    DataPreview
)

router = APIRouter()
data_service = DataConnectorService()

@router.get("/types", response_model=List[dict])
async def get_source_types():
    """Get available data source types with configuration schemas"""
    return [
        {
            "type": "csv",
            "name": "CSV File",
            "icon": "file-csv",
            "config_schema": {
                "file_path": "string",
                "delimiter": "string (default: ,)",
                "encoding": "string (default: utf-8)",
                "has_header": "boolean (default: true)"
            }
        },
        {
            "type": "excel",
            "name": "Excel File",
            "icon": "file-excel",
            "config_schema": {
                "file_path": "string",
                "sheet_name": "string (default: first sheet)",
                "header_row": "integer (default: 0)"
            }
        },
        {
            "type": "postgresql",
            "name": "PostgreSQL",
            "icon": "database",
            "config_schema": {
                "host": "string",
                "port": "integer (default: 5432)",
                "database": "string",
                "username": "string",
                "password": "string",
                "ssl_mode": "string (default: prefer)"
            }
        },
        {
            "type": "mysql",
            "name": "MySQL",
            "icon": "database",
            "config_schema": {
                "host": "string",
                "port": "integer (default: 3306)",
                "database": "string",
                "username": "string",
                "password": "string"
            }
        },
        {
            "type": "api_rest",
            "name": "REST API",
            "icon": "cloud",
            "config_schema": {
                "base_url": "string",
                "headers": "object",
                "auth_type": "string (none, bearer, basic, api_key)",
                "auth_config": "object"
            }
        },
        {
            "type": "snowflake",
            "name": "Snowflake",
            "icon": "snowflake",
            "config_schema": {
                "account": "string",
                "warehouse": "string",
                "database": "string",
                "schema": "string",
                "username": "string",
                "password": "string",
                "role": "string"
            }
        },
        {
            "type": "bigquery",
            "name": "Google BigQuery",
            "icon": "google",
            "config_schema": {
                "project_id": "string",
                "dataset": "string",
                "credentials_json": "string (service account JSON)"
            }
        }
    ]

@router.get("/", response_model=List[DataSourceResponse])
async def list_data_sources(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all data sources for current user"""
    result = await db.execute(
        select(DataSource)
        .where(DataSource.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=DataSourceResponse)
async def create_data_source(
    source: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new data source"""
    # Test connection first
    test_result = await data_service.test_connection(source.source_type, source.connection_config)
    if not test_result["success"]:
        raise HTTPException(status_code=400, detail=f"Connection failed: {test_result['message']}")
    
    # Create data source
    db_source = DataSource(
        name=source.name,
        description=source.description,
        source_type=source.source_type,
        connection_config=source.connection_config,
        sync_enabled=source.sync_enabled,
        owner_id=current_user.id
    )
    db.add(db_source)
    await db.commit()
    await db.refresh(db_source)
    
    # Auto-detect schema
    schema = await data_service.discover_schema(db_source)
    db_source.schema_cache = schema
    await db.commit()
    
    return db_source

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and create data source from file (CSV/Excel)"""
    content = await file.read()
    
    # Determine file type
    if file.filename.endswith('.csv'):
        source_type = DataSourceType.CSV
        # Parse to validate
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
    elif file.filename.endswith(('.xlsx', '.xls')):
        source_type = DataSourceType.EXCEL
        df = pd.read_excel(io.BytesIO(content))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV or Excel.")
    
    # Save file
    file_path = f"uploads/{current_user.id}/{file.filename}"
    # TODO: Save to storage
    
    # Create data source
    db_source = DataSource(
        name=name,
        description=description,
        source_type=source_type,
        connection_config={
            "file_path": file_path,
            "original_filename": file.filename,
            "size": len(content),
            "columns": df.columns.tolist(),
            "row_count": len(df)
        },
        schema_cache={
            "columns": [
                {"name": col, "type": str(df[col].dtype), "sample": df[col].head(5).tolist()}
                for col in df.columns
            ],
            "row_count": len(df)
        },
        sync_enabled="manual",
        owner_id=current_user.id
    )
    db.add(db_source)
    await db.commit()
    await db.refresh(db_source)
    
    return db_source

@router.post("/{source_id}/test")
async def test_data_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test data source connection"""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id, DataSource.owner_id == current_user.id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    test_result = await data_service.test_connection(source.source_type, source.connection_config)
    return test_result

@router.get("/{source_id}/preview", response_model=DataPreview)
async def preview_data(
    source_id: int,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Preview data from source"""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id, DataSource.owner_id == current_user.id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    preview = await data_service.get_preview(source, limit)
    return preview

@router.post("/{source_id}/sync")
async def sync_data_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually sync data source"""
    result = await db.execute(
        select(DataSource).where(DataSource.id == source_id, DataSource.owner_id == current_user.id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Trigger sync
    sync_result = await data_service.sync_source(source)
    
    # Update status
    source.sync_status = "success" if sync_result["success"] else "error"
    source.last_sync_at = datetime.utcnow()
    if not sync_result["success"]:
        source.sync_error = sync_result.get("error")
    
    await db.commit()
    return sync_result
