"""
NLP Query Engine
Natural Language to SQL/Analytics conversion
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from core.logging import logger
from core.config import settings

class NLPQueryEngine:
    """Natural Language Query Processing Engine"""
    
    def __init__(self):
        self.initialized = False
        self.query_patterns = self._initialize_patterns()
    
    async def initialize(self):
        """Initialize NLP components"""
        try:
            # TODO: Load LLM or transformer models if configured
            self.initialized = True
            logger.info("NLP Query Engine initialized")
        except Exception as e:
            logger.error(f"NLP initialization failed: {e}")
    
    def _initialize_patterns(self) -> Dict:
        """Initialize query pattern matchers"""
        return {
            "aggregation": {
                "patterns": [
                    r"(?:show|get|what is|calculate)\s+(?:the\s+)?(total|sum|average|avg|mean|count|min|max|median)\s+(?:of\s+)?(\w+)",
                    r"(total|sum|average|avg|count|min|max)\s+(?:of\s+)?(\w+)"
                ],
                "operations": {
                    "total": "sum",
                    "sum": "sum", 
                    "average": "avg",
                    "avg": "avg",
                    "mean": "avg",
                    "count": "count",
                    "min": "min",
                    "max": "max",
                    "median": "median"
                }
            },
            "time_filter": {
                "patterns": [
                    r"(?:in|during|for)\s+(?:the\s+)?(last|past)\s+(\d+)?\s*(day|week|month|quarter|year|days|weeks|months|years)",
                    r"(?:in|during|for)\s+(?:the\s+)?(this|current)\s+(day|week|month|quarter|year)",
                    r"(?:from|between)\s+(.+?)\s+(?:to|and)\s+(.+)$"
                ],
                "relative_dates": {
                    "last month": lambda: (datetime.now() - timedelta(days=30), datetime.now()),
                    "last week": lambda: (datetime.now() - timedelta(days=7), datetime.now()),
                    "last quarter": lambda: (datetime.now() - timedelta(days=90), datetime.now()),
                    "last year": lambda: (datetime.now() - timedelta(days=365), datetime.now()),
                    "this month": lambda: (datetime.now().replace(day=1), datetime.now()),
                    "today": lambda: (datetime.now().replace(hour=0, minute=0, second=0), datetime.now())
                }
            },
            "grouping": {
                "patterns": [
                    r"(?:grouped?\s+)?by\s+(\w+)",
                    r"(?:for\s+)?each\s+(\w+)",
                    r"per\s+(\w+)",
                    r"broken?\s+(?:down\s+)?by\s+(\w+)"
                ]
            },
            "comparison": {
                "patterns": [
                    r"compare\s+(.+?)\s+(?:to|with|versus|vs)\s+(.+)",
                    r"difference\s+between\s+(.+?)\s+and\s+(.+)"
                ]
            },
            "top_bottom": {
                "patterns": [
                    r"(top|bottom)\s+(\d+)\s+(\w+)",
                    r"(highest|lowest)\s+(\d+)\s+(\w+)"
                ],
                "mapping": {
                    "top": "desc",
                    "highest": "desc",
                    "bottom": "asc",
                    "lowest": "asc"
                }
            },
            "trend": {
                "patterns": [
                    r"trend\s+(?:of\s+)?(\w+)",
                    r"(?:how\s+does|show)\s+(\w+)\s+(?:change|vary|trend)\s+over\s+time",
                    r"(?:time\s+series|time\s+chart)\s+(?:of\s+)?(\w+)"
                ]
            }
        }
    
    async def process_query(self, query: str, context=None, user=None) -> Dict:
        """Process natural language query and return results"""
        try:
            query_lower = query.lower().strip()
            
            # Parse query intent
            parsed = self._parse_query(query_lower)
            
            # Generate SQL or data operation
            if context and hasattr(context, 'sample_data'):
                result = await self._execute_on_dataset(query_lower, parsed, context)
            else:
                result = await self._generate_query_plan(query_lower, parsed)
            
            return {
                "query": query,
                "parsed_intent": parsed,
                "result": result,
                "suggested_visualization": self._suggest_visualization(parsed),
                "natural_response": self._generate_natural_response(parsed, result)
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "suggestion": "Try rephrasing your question with specific column names"
            }
    
    def _parse_query(self, query: str) -> Dict:
        """Parse query intent and extract parameters"""
        parsed = {
            "operation": None,
            "columns": [],
            "filters": [],
            "group_by": None,
            "sort": None,
            "limit": None,
            "time_range": None,
            "comparison": None
        }
        
        # Check for aggregations
        agg_match = re.search(
            r"(?:show|get|what is|calculate)?\s*(?:the\s+)?(total|sum|average|avg|mean|count|min|max|median)\s+(?:of\s+)?(\w+)",
            query
        )
        if agg_match:
            op = agg_match.group(1)
            col = agg_match.group(2)
            parsed["operation"] = self.query_patterns["aggregation"]["operations"].get(op, "sum")
            parsed["columns"].append(col)
        
        # Check for time filters
        for pattern in self.query_patterns["time_filter"]["patterns"]:
            match = re.search(pattern, query)
            if match:
                parsed["time_range"] = self._extract_time_range(match, query)
                break
        
        # Check for grouping
        for pattern in self.query_patterns["grouping"]["patterns"]:
            match = re.search(pattern, query)
            if match:
                parsed["group_by"] = match.group(1)
                break
        
        # Check for top/bottom
        top_match = re.search(r"(top|bottom)\s+(\d+)\s+(\w+)", query)
        if top_match:
            direction = self.query_patterns["top_bottom"]["mapping"][top_match.group(1)]
            parsed["sort"] = {"column": top_match.group(3), "direction": direction}
            parsed["limit"] = int(top_match.group(2))
        
        # Check for trend
        if any(w in query for w in ["trend", "over time", "time series"]):
            parsed["operation"] = "trend"
        
        # Check for comparison
        compare_match = re.search(r"compare\s+(.+?)\s+(?:to|with|versus|vs)\s+(.+)", query)
        if compare_match:
            parsed["comparison"] = {
                "left": compare_match.group(1).strip(),
                "right": compare_match.group(2).strip()
            }
        
        return parsed
    
    def _extract_time_range(self, match, query: str) -> Dict:
        """Extract time range from query"""
        query_lower = query.lower()
        
        for key, func in self.query_patterns["time_filter"]["relative_dates"].items():
            if key in query_lower:
                start, end = func()
                return {
                    "type": "relative",
                    "label": key,
                    "start": start.isoformat(),
                    "end": end.isoformat()
                }
        
        return None
    
    async def _execute_on_dataset(self, query: str, parsed: Dict, dataset) -> Dict:
        """Execute parsed query on dataset"""
        df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
        
        if df.empty:
            return {"error": "Dataset is empty"}
        
        # Apply operations
        result_df = df.copy()
        
        # Apply time filter if applicable
        if parsed.get("time_range"):
            # TODO: Implement time filtering
            pass
        
        # Apply aggregation
        if parsed.get("operation") == "trend" and parsed["columns"]:
            # Return time series data
            col = parsed["columns"][0]
            if col in df.columns:
                result = {
                    "type": "time_series",
                    "column": col,
                    "data": df[col].tolist()
                }
                return result
        
        elif parsed.get("operation") and parsed["columns"]:
            col = parsed["columns"][0]
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                op = parsed["operation"]
                if op == "sum":
                    value = df[col].sum()
                elif op == "avg":
                    value = df[col].mean()
                elif op == "count":
                    value = len(df)
                elif op == "min":
                    value = df[col].min()
                elif op == "max":
                    value = df[col].max()
                else:
                    value = df[col].sum()
                
                return {
                    "type": "aggregation",
                    "operation": op,
                    "column": col,
                    "value": float(value)
                }
        
        # Apply grouping
        if parsed.get("group_by") and parsed["group_by"] in df.columns:
            group_col = parsed["group_by"]
            
            if parsed.get("columns"):
                value_col = parsed["columns"][0]
                if value_col in df.columns:
                    grouped = df.groupby(group_col)[value_col].sum().reset_index()
                    return {
                        "type": "grouped",
                        "group_by": group_col,
                        "values": grouped.to_dict(orient="records")
                    }
        
        # Return filtered/preview data
        limit = parsed.get("limit", 100)
        return {
            "type": "preview",
            "columns": df.columns.tolist(),
            "data": df.head(limit).to_dict(orient="records"),
            "total_rows": len(df)
        }
    
    async def _generate_query_plan(self, query: str, parsed: Dict) -> Dict:
        """Generate query plan without executing"""
        # Generate pseudo-SQL for demonstration
        sql_parts = ["SELECT"]
        
        if parsed.get("operation"):
            op = parsed["operation"].upper()
            col = parsed["columns"][0] if parsed["columns"] else "*"
            sql_parts.append(f"{op}({col})")
        else:
            sql_parts.append("*")
        
        sql_parts.append("FROM dataset")
        
        if parsed.get("time_range"):
            sql_parts.append(f"WHERE date BETWEEN '{parsed['time_range']['start']}' AND '{parsed['time_range']['end']}'")
        
        if parsed.get("group_by"):
            sql_parts.append(f"GROUP BY {parsed['group_by']}")
        
        if parsed.get("sort"):
            direction = "DESC" if parsed["sort"]["direction"] == "desc" else "ASC"
            sql_parts.append(f"ORDER BY {parsed['sort']['column']} {direction}")
        
        if parsed.get("limit"):
            sql_parts.append(f"LIMIT {parsed['limit']}")
        
        return {
            "type": "query_plan",
            "suggested_sql": " ".join(sql_parts),
            "parsed": parsed
        }
    
    def _suggest_visualization(self, parsed: Dict) -> str:
        """Suggest visualization type based on query"""
        if parsed.get("operation") == "trend":
            return "line"
        elif parsed.get("group_by"):
            return "bar"
        elif parsed.get("comparison"):
            return "bar"
        elif parsed.get("operation") in ["sum", "avg", "count"]:
            return "metric_card"
        else:
            return "table"
    
    def _generate_natural_response(self, parsed: Dict, result: Dict) -> str:
        """Generate natural language response"""
        if result.get("type") == "aggregation":
            op = result["operation"]
            col = result["column"]
            value = result["value"]
            
            if op == "sum":
                return f"The total {col} is {value:,.2f}"
            elif op == "avg":
                return f"The average {col} is {value:,.2f}"
            elif op == "count":
                return f"There are {int(value):,} records"
            elif op == "max":
                return f"The maximum {col} is {value:,.2f}"
            elif op == "min":
                return f"The minimum {col} is {value:,.2f}"
        
        elif result.get("type") == "grouped":
            return f"Showing data grouped by {result['group_by']}"
        
        elif result.get("type") == "preview":
            return f"Showing {len(result.get('data', []))} of {result.get('total_rows', 0)} records"
        
        return "Query executed successfully"
    
    async def generate_suggestions(self, dataset) -> List[str]:
        """Generate natural language query suggestions"""
        df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
        
        suggestions = [
            "Show me the total sales",
            "What is the average revenue by region?",
            "Show me trends over time",
            "Compare this month vs last month",
            "What are the top 10 products by sales?",
            "Show me a breakdown by category"
        ]
        
        # Customize based on available columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
        
        if numeric_cols and cat_cols:
            suggestions.append(f"What is the average {numeric_cols[0]} by {cat_cols[0]}?")
        
        return suggestions[:8]
    
    async def explain_dataset(self, dataset, question: str = None) -> Dict:
        """Generate AI explanation of dataset"""
        df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
        
        if df.empty:
            return {"explanation": "Dataset is empty"}
        
        # Generate basic stats
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        insights = []
        
        for col in numeric_cols[:3]:
            stats = df[col].describe()
            insights.append(f"{col}: average {stats['mean']:.2f}, ranges from {stats['min']:.2f} to {stats['max']:.2f}")
        
        explanation = f"This dataset contains {len(df)} records with {len(df.columns)} columns. "
        explanation += "Key metrics: " + "; ".join(insights)
        
        return {
            "explanation": explanation,
            "statistics": {col: df[col].describe().to_dict() for col in numeric_cols[:5]},
            "column_info": [{"name": col, "type": str(df[col].dtype)} for col in df.columns]
        }
    
    async def generate_auto_insights(self, dataset) -> List[Dict]:
        """Automatically generate insights from dataset"""
        df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
        
        if df.empty:
            return []
        
        insights = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Trend insight
        if len(df) > 10 and numeric_cols:
            col = numeric_cols[0]
            trend = "increasing" if df[col].iloc[-1] > df[col].iloc[0] else "decreasing"
            change = ((df[col].iloc[-1] - df[col].iloc[0]) / df[col].iloc[0] * 100) if df[col].iloc[0] != 0 else 0
            insights.append({
                "type": "trend",
                "title": f"{col} is {trend}",
                "description": f"{col} has {trend} by {abs(change):.1f}% over the period",
                "severity": "info"
            })
        
        # Outlier insight
        for col in numeric_cols[:2]:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = df[(df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)]
            if len(outliers) > 0:
                insights.append({
                    "type": "outlier",
                    "title": f"Outliers detected in {col}",
                    "description": f"Found {len(outliers)} outlier values in {col}",
                    "severity": "warning"
                })
        
        # Correlation insight
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols[:2]].corr().iloc[0, 1]
            if abs(corr) > 0.7:
                insights.append({
                    "type": "correlation",
                    "title": f"Strong correlation detected",
                    "description": f"{numeric_cols[0]} and {numeric_cols[1]} have a correlation of {corr:.2f}",
                    "severity": "info"
                })
        
        return insights
