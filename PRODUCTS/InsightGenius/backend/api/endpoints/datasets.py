"""
Datasets API Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.dataset import Dataset, DatasetColumn
from services.dataset_service import DatasetService
from schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    ColumnStats
)

router = APIRouter()
dataset_service = DatasetService()

@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    data_source_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List datasets"""
    query = select(Dataset)
    if data_source_id:
        query = query.where(Dataset.data_source_id == data_source_id)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset details"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.get("/{dataset_id}/data")
async def get_dataset_data(
    dataset_id: int,
    limit: int = Query(1000, le=10000),
    offset: int = 0,
    columns: Optional[List[str]] = Query(None),
    filters: Optional[str] = None,
    sort: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get actual data from dataset"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    data = await dataset_service.get_data(
        dataset, limit, offset, columns, filters, sort
    )
    return data

@router.get("/{dataset_id}/stats")
async def get_dataset_stats(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset statistics"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    stats = await dataset_service.compute_stats(dataset)
    return stats

@router.get("/{dataset_id}/columns/{column_name}/stats")
async def get_column_stats(
    dataset_id: int,
    column_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific column"""
    result = await db.execute(
        select(DatasetColumn)
        .where(DatasetColumn.dataset_id == dataset_id, DatasetColumn.name == column_name)
    )
    column = result.scalar_one_or_none()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    
    return column.statistics

@router.post("/{dataset_id}/refresh")
async def refresh_dataset(
    dataset_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refresh dataset from source"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    refresh_result = await dataset_service.refresh(dataset)
    return refresh_result

@router.get("/{dataset_id}/query")
async def query_dataset(
    dataset_id: int,
    sql: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute SQL query on dataset"""
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    query_result = await dataset_service.execute_query(dataset, sql)
    return query_result
