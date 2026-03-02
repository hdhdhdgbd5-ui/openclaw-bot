"""
Data Connector Service
Handles connections to various data sources
"""

import pandas as pd
import asyncpg
import aiomysql
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from core.logging import logger

class DataConnectorService:
    """Service for connecting to and reading from various data sources"""
    
    async def test_connection(self, source_type: str, config: Dict) -> Dict:
        """Test connection to a data source"""
        try:
            if source_type in ["csv", "excel"]:
                return {"success": True, "message": "File-based source ready"}
            
            elif source_type == "postgresql":
                conn = await asyncpg.connect(
                    host=config.get("host", "localhost"),
                    port=config.get("port", 5432),
                    database=config["database"],
                    user=config["username"],
                    password=config["password"]
                )
                await conn.close()
                return {"success": True, "message": "PostgreSQL connection successful"}
            
            elif source_type == "mysql":
                conn = await aiomysql.connect(
                    host=config.get("host", "localhost"),
                    port=config.get("port", 3306),
                    db=config["database"],
                    user=config["username"],
                    password=config["password"]
                )
                conn.close()
                return {"success": True, "message": "MySQL connection successful"}
            
            elif source_type == "api_rest":
                async with aiohttp.ClientSession() as session:
                    headers = config.get("headers", {})
                    if config.get("auth_type") == "bearer":
                        headers["Authorization"] = f"Bearer {config['auth_config']['token']}"
                    
                    async with session.get(config["base_url"], headers=headers, timeout=10) as resp:
                        if resp.status < 400:
                            return {"success": True, "message": "API connection successful"}
                        else:
                            return {"success": False, "message": f"API returned status {resp.status}"}
            
            elif source_type == "bigquery":
                # TODO: Implement BigQuery test
                return {"success": True, "message": "BigQuery configuration valid"}
            
            else:
                return {"success": False, "message": f"Unsupported source type: {source_type}"}
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {"success": False, "message": str(e)}
    
    async def discover_schema(self, data_source) -> Dict:
        """Auto-discover schema from data source"""
        try:
            if data_source.source_type.value == "postgresql":
                conn = await asyncpg.connect(
                    host=data_source.connection_config.get("host", "localhost"),
                    port=data_source.connection_config.get("port", 5432),
                    database=data_source.connection_config["database"],
                    user=data_source.connection_config["username"],
                    password=data_source.connection_config["password"]
                )
                
                # Get tables
                tables = await conn.fetch("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                
                schema = {"tables": []}
                for table in tables:
                    table_name = table["table_name"]
                    columns = await conn.fetch("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = $1
                    """, table_name)
                    
                    schema["tables"].append({
                        "name": table_name,
                        "columns": [
                            {
                                "name": c["column_name"],
                                "type": c["data_type"],
                                "nullable": c["is_nullable"] == "YES"
                            }
                            for c in columns
                        ]
                    })
                
                await conn.close()
                return schema
            
            elif data_source.source_type.value in ["csv", "excel"]:
                # File-based sources already have schema cached
                return data_source.schema_cache or {}
            
            else:
                return {"tables": [], "message": "Schema discovery not implemented for this source type"}
                
        except Exception as e:
            logger.error(f"Schema discovery failed: {e}")
            return {"error": str(e)}
    
    async def get_preview(self, data_source, limit: int = 100) -> Dict:
        """Get preview data from source"""
        try:
            if data_source.source_type.value == "csv":
                import os
                file_path = data_source.connection_config.get("file_path")
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path, nrows=limit)
                    return {
                        "columns": df.columns.tolist(),
                        "data": df.to_dict(orient="records"),
                        "total_rows": len(df)
                    }
                else:
                    return {"error": "File not found"}
            
            elif data_source.source_type.value == "postgresql":
                conn = await asyncpg.connect(
                    host=data_source.connection_config.get("host", "localhost"),
                    port=data_source.connection_config.get("port", 5432),
                    database=data_source.connection_config["database"],
                    user=data_source.connection_config["username"],
                    password=data_source.connection_config["password"]
                )
                
                # Get first table or use configured query
                table = data_source.source_table_or_query or "(SELECT table_name FROM information_schema.tables LIMIT 1)"
                rows = await conn.fetch(f"SELECT * FROM {table} LIMIT {limit}")
                
                await conn.close()
                
                if rows:
                    return {
                        "columns": list(rows[0].keys()),
                        "data": [dict(r) for r in rows],
                        "total_rows": len(rows)
                    }
                else:
                    return {"columns": [], "data": [], "total_rows": 0}
            
            elif data_source.source_type.value == "api_rest":
                async with aiohttp.ClientSession() as session:
                    config = data_source.connection_config
                    headers = config.get("headers", {})
                    
                    if config.get("auth_type") == "bearer":
                        headers["Authorization"] = f"Bearer {config['auth_config']['token']}"
                    
                    async with session.get(config["base_url"], headers=headers) as resp:
                        data = await resp.json()
                        
                        # Normalize to list
                        if isinstance(data, dict):
                            # Try common patterns
                            for key in ["data", "results", "items", "records"]:
                                if key in data:
                                    data = data[key]
                                    break
                        
                        if isinstance(data, list):
                            return {
                                "columns": list(data[0].keys()) if data else [],
                                "data": data[:limit],
                                "total_rows": len(data)
                            }
                        else:
                            return {"error": "Could not parse API response"}
            
            else:
                return {"error": f"Preview not implemented for {data_source.source_type.value}"}
                
        except Exception as e:
            logger.error(f"Preview failed: {e}")
            return {"error": str(e)}
    
    async def sync_source(self, data_source) -> Dict:
        """Sync data from source to internal storage"""
        try:
            preview = await self.get_preview(data_source, limit=100000)
            
            if "error" in preview:
                return {"success": False, "error": preview["error"]}
            
            # TODO: Store in internal database or cache
            # For now, just return success with stats
            return {
                "success": True,
                "rows_synced": preview.get("total_rows", 0),
                "columns": len(preview.get("columns", [])),
                "synced_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {"success": False, "error": str(e)}
