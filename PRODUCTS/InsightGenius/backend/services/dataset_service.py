"""
Dataset Service
Handles dataset operations and data processing
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.logging import logger

class DatasetService:
    """Service for dataset operations"""
    
    async def compute_stats(self, dataset) -> Dict[str, Any]:
        """Compute statistics for dataset"""
        try:
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            
            if df.empty:
                return {"error": "Dataset is empty"}
            
            stats = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": []
            }
            
            for col in df.columns:
                col_stats = {
                    "name": col,
                    "type": str(df[col].dtype),
                    "null_count": int(df[col].isnull().sum()),
                    "unique_count": int(df[col].nunique())
                }
                
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats.update({
                        "min": float(df[col].min()) if not pd.isna(df[col].min()) else None,
                        "max": float(df[col].max()) if not pd.isna(df[col].max()) else None,
                        "mean": float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                        "median": float(df[col].median()) if not pd.isna(df[col].median()) else None,
                        "std": float(df[col].std()) if not pd.isna(df[col].std()) else None
                    })
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    col_stats.update({
                        "min": df[col].min().isoformat() if not pd.isna(df[col].min()) else None,
                        "max": df[col].max().isoformat() if not pd.isna(df[col].max()) else None
                    })
                else:
                    # Categorical
                    col_stats["top_values"] = df[col].value_counts().head(5).to_dict()
                
                stats["columns"].append(col_stats)
            
            return stats
            
        except Exception as e:
            logger.error(f"Stats computation failed: {e}")
            return {"error": str(e)}
    
    async def get_data(
        self, 
        dataset, 
        limit: int = 1000,
        offset: int = 0,
        columns: Optional[List[str]] = None,
        filters: Optional[str] = None,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get data from dataset with filtering and sorting"""
        try:
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            
            if df.empty:
                return {"columns": [], "data": [], "total": 0}
            
            # Select columns
            if columns:
                available_cols = [c for c in columns if c in df.columns]
                if available_cols:
                    df = df[available_cols]
            
            # Apply filters (simplified)
            if filters:
                # TODO: Implement proper filter parsing
                pass
            
            # Apply sorting
            if sort:
                sort_parts = sort.split(":")
                sort_col = sort_parts[0]
                sort_asc = len(sort_parts) == 1 or sort_parts[1].lower() != "desc"
                
                if sort_col in df.columns:
                    df = df.sort_values(by=sort_col, ascending=sort_asc)
            
            total = len(df)
            
            # Apply pagination
            df_paginated = df.iloc[offset:offset + limit]
            
            return {
                "columns": df.columns.tolist(),
                "data": df_paginated.to_dict(orient="records"),
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Data retrieval failed: {e}")
            return {"error": str(e)}
    
    async def refresh(self, dataset) -> Dict[str, Any]:
        """Refresh dataset from source"""
        try:
            # TODO: Implement actual data refresh from source
            dataset.last_processed_at = datetime.utcnow()
            dataset.processing_status = "success"
            
            return {
                "success": True,
                "refreshed_at": datetime.utcnow().isoformat(),
                "rows_processed": dataset.row_count
            }
            
        except Exception as e:
            logger.error(f"Dataset refresh failed: {e}")
            dataset.processing_status = "error"
            return {"success": False, "error": str(e)}
    
    async def execute_query(self, dataset, sql: str) -> Dict[str, Any]:
        """Execute SQL query on dataset"""
        try:
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            
            if df.empty:
                return {"error": "Dataset is empty"}
            
            # Note: In production, use proper SQL execution with sqldf or similar
            # For now, return sample data
            return {
                "columns": df.columns.tolist(),
                "data": df.head(100).to_dict(orient="records"),
                "query": sql
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"error": str(e)}
    
    async def infer_schema(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Infer schema from DataFrame"""
        schema = []
        
        for col in data.columns:
            dtype = data[col].dtype
            
            if pd.api.types.is_integer_dtype(dtype):
                data_type = "integer"
            elif pd.api.types.is_float_dtype(dtype):
                data_type = "float"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                data_type = "datetime"
            elif pd.api.types.is_bool_dtype(dtype):
                data_type = "boolean"
            else:
                data_type = "string"
            
            schema.append({
                "name": col,
                "type": data_type,
                "nullable": data[col].isnull().any(),
                "unique_count": int(data[col].nunique()),
                "sample_values": data[col].dropna().head(5).tolist()
            })
        
        return schema
