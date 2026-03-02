"""
AI Chart Recommender Service
Uses ML to recommend optimal chart types based on data characteristics
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime

from core.logging import logger

class ChartRecommendation:
    def __init__(self, chart_type: str, title: str, description: str, config: Dict):
        self.chart_type = chart_type
        self.title = title
        self.description = description
        self.config = config
        self.score = 0.0

class AIChartRecommender:
    """AI-powered chart recommendation engine"""
    
    def __init__(self):
        self.chart_rules = self._initialize_rules()
    
    def _initialize_rules(self) -> Dict:
        """Initialize chart recommendation rules"""
        return {
            "line": {
                "requires": ["datetime", "numeric"],
                "good_for": ["trends", "time_series", "continuous_data"],
                "score_boost": 1.0
            },
            "bar": {
                "requires": ["categorical", "numeric"],
                "good_for": ["comparison", "ranking", "discrete_categories"],
                "score_boost": 1.0
            },
            "scatter": {
                "requires": ["numeric", "numeric"],
                "good_for": ["correlation", "distribution", "relationships"],
                "score_boost": 1.0
            },
            "pie": {
                "requires": ["categorical", "numeric"],
                "good_for": ["composition", "part_to_whole", "percentages"],
                "score_boost": 0.7,  # Lower priority
                "max_categories": 8
            },
            "heatmap": {
                "requires": ["categorical", "categorical", "numeric"],
                "good_for": ["correlation_matrix", "density", "patterns"],
                "score_boost": 0.9
            },
            "area": {
                "requires": ["datetime", "numeric"],
                "good_for": ["cumulative", "volume", "stacked_trends"],
                "score_boost": 0.9
            },
            "histogram": {
                "requires": ["numeric"],
                "good_for": ["distribution", "frequency"],
                "score_boost": 0.85
            },
            "box": {
                "requires": ["numeric"],
                "good_for": ["distribution", "outliers", "statistics"],
                "score_boost": 0.8
            }
        }
    
    async def recommend_charts(self, dataset) -> List[ChartRecommendation]:
        """Generate chart recommendations for a dataset"""
        try:
            # Load sample data
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            
            if df.empty:
                return self._get_default_recommendations()
            
            # Analyze columns
            column_types = self._analyze_columns(df)
            
            # Score each chart type
            recommendations = []
            
            for chart_type, rules in self.chart_rules.items():
                score, reason = self._score_chart_type(chart_type, rules, df, column_types)
                if score > 0.5:
                    rec = self._create_recommendation(chart_type, df, column_types, score, reason)
                    recommendations.append(rec)
            
            # Sort by score
            recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return recommendations[:6]  # Top 6 recommendations
            
        except Exception as e:
            logger.error(f"Chart recommendation failed: {e}")
            return self._get_default_recommendations()
    
    async def recommend_from_nlp(self, dataset, natural_language_request: str) -> Dict:
        """Generate chart recommendation from natural language query"""
        try:
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            column_types = self._analyze_columns(df)
            
            # Parse intent from natural language
            intent = self._parse_nlp_intent(natural_language_request)
            
            # Find best matching chart
            best_chart = None
            best_score = 0
            
            for chart_type, rules in self.chart_rules.items():
                score = self._score_for_intent(chart_type, intent, df, column_types)
                if score > best_score:
                    best_score = score
                    best_chart = chart_type
            
            if best_chart:
                rec = self._create_recommendation(best_chart, df, column_types, best_score, intent)
                return {
                    "chart_type": rec.chart_type,
                    "title": rec.title,
                    "description": rec.description,
                    "config": rec.config,
                    "confidence": best_score,
                    "suggested_columns": self._suggest_columns(best_chart, df, column_types)
                }
            
            return {"error": "Could not determine suitable chart type"}
            
        except Exception as e:
            logger.error(f"NLP recommendation failed: {e}")
            return {"error": str(e)}
    
    def _analyze_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Analyze column types"""
        types = {}
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                types[col] = "datetime"
            elif pd.api.types.is_numeric_dtype(df[col]):
                types[col] = "numeric"
            else:
                types[col] = "categorical"
        return types
    
    def _score_chart_type(self, chart_type: str, rules: Dict, df: pd.DataFrame, column_types: Dict) -> tuple:
        """Score how suitable a chart type is for the data"""
        score = 0.5
        reason = ""
        
        requires = rules["requires"]
        available_types = list(column_types.values())
        
        # Check if required types are available
        for req in requires:
            if req in available_types:
                score += 0.15
            else:
                score -= 0.3
        
        # Special rules
        if chart_type == "pie":
            cat_cols = [c for c, t in column_types.items() if t == "categorical"]
            for col in cat_cols:
                if df[col].nunique() <= rules.get("max_categories", 8):
                    score += 0.2
                    reason = f"Good for showing composition of {col}"
                else:
                    score -= 0.4
        
        if chart_type == "line":
            dt_cols = [c for c, t in column_types.items() if t == "datetime"]
            num_cols = [c for c, t in column_types.items() if t == "numeric"]
            if dt_cols and num_cols:
                score += 0.3
                reason = f"Perfect for showing trends of {num_cols[0]} over time"
        
        if chart_type == "scatter":
            num_cols = [c for c, t in column_types.items() if t == "numeric"]
            if len(num_cols) >= 2:
                score += 0.2
                # Check correlation
                corr = df[num_cols[:2]].corr().iloc[0, 1]
                if abs(corr) > 0.5:
                    score += 0.2
                    reason = f"Strong correlation ({corr:.2f}) detected between {num_cols[0]} and {num_cols[1]}"
        
        score *= rules.get("score_boost", 1.0)
        
        return min(score, 1.0), reason
    
    def _parse_nlp_intent(self, query: str) -> Dict:
        """Parse intent from natural language query"""
        query_lower = query.lower()
        
        intent = {
            "trend": any(w in query_lower for w in ["trend", "over time", "history", "growth"]),
            "comparison": any(w in query_lower for w in ["compare", "versus", "vs", "difference", "between"]),
            "distribution": any(w in query_lower for w in ["distribution", "histogram", "spread", "range"]),
            "correlation": any(w in query_lower for w in ["correlation", "relationship", "vs", "against"]),
            "composition": any(w in query_lower for w in ["breakdown", "composition", "percentage", "share", "proportion"]),
            "ranking": any(w in query_lower for w in ["top", "bottom", "ranking", "best", "worst"]),
            "time_range": None
        }
        
        # Detect time ranges
        if "last month" in query_lower or "past month" in query_lower:
            intent["time_range"] = "1M"
        elif "last quarter" in query_lower or "past quarter" in query_lower:
            intent["time_range"] = "1Q"
        elif "last year" in query_lower or "past year" in query_lower:
            intent["time_range"] = "1Y"
        
        return intent
    
    def _score_for_intent(self, chart_type: str, intent: Dict, df: pd.DataFrame, column_types: Dict) -> float:
        """Score chart type based on user intent"""
        scores = {
            "line": intent["trend"] * 1.0 + intent["comparison"] * 0.3,
            "bar": intent["comparison"] * 1.0 + intent["ranking"] * 1.0,
            "scatter": intent["correlation"] * 1.0 + intent["distribution"] * 0.5,
            "pie": intent["composition"] * 1.0,
            "histogram": intent["distribution"] * 1.0,
            "heatmap": intent["correlation"] * 0.8,
            "area": intent["trend"] * 0.9 + intent["composition"] * 0.5
        }
        
        base_score = scores.get(chart_type, 0.5)
        
        # Apply data compatibility score
        compat_score, _ = self._score_chart_type(chart_type, self.chart_rules[chart_type], df, column_types)
        
        return base_score * compat_score
    
    def _create_recommendation(self, chart_type: str, df: pd.DataFrame, column_types: Dict, 
                               score: float, reason: str) -> ChartRecommendation:
        """Create a chart recommendation"""
        
        # Select appropriate columns
        x_col, y_col, color_col = self._select_columns(chart_type, df, column_types)
        
        title = f"{y_col} by {x_col}" if x_col and y_col else f"{chart_type.title()} Chart"
        description = reason if reason else f"Visualize data using {chart_type} chart"
        
        config = {
            "chart_type": chart_type,
            "x_axis": {"column": x_col, "type": column_types.get(x_col, "categorical")} if x_col else None,
            "y_axis": [{"column": y_col, "type": "value"}] if y_col else None,
            "color_by": color_col,
            "show_legend": color_col is not None,
            "theme": "default"
        }
        
        rec = ChartRecommendation(chart_type, title, description, config)
        rec.score = score
        
        return rec
    
    def _select_columns(self, chart_type: str, df: pd.DataFrame, column_types: Dict) -> tuple:
        """Select appropriate columns for chart type"""
        dt_cols = [c for c, t in column_types.items() if t == "datetime"]
        num_cols = [c for c, t in column_types.items() if t == "numeric"]
        cat_cols = [c for c, t in column_types.items() if t == "categorical"]
        
        if chart_type in ["line", "area"]:
            x = dt_cols[0] if dt_cols else (cat_cols[0] if cat_cols else None)
            y = num_cols[0] if num_cols else None
            color = cat_cols[0] if cat_cols and len(cat_cols) > 1 else None
        
        elif chart_type == "bar":
            x = cat_cols[0] if cat_cols else None
            y = num_cols[0] if num_cols else None
            color = cat_cols[1] if len(cat_cols) > 1 else None
        
        elif chart_type == "scatter":
            x = num_cols[0] if num_cols else None
            y = num_cols[1] if len(num_cols) > 1 else (num_cols[0] if num_cols else None)
            color = cat_cols[0] if cat_cols else None
        
        elif chart_type == "pie":
            x = None
            y = num_cols[0] if num_cols else None
            color = cat_cols[0] if cat_cols else None
        
        else:
            x = df.columns[0] if len(df.columns) > 0 else None
            y = df.columns[1] if len(df.columns) > 1 else None
            color = None
        
        return x, y, color
    
    def _suggest_columns(self, chart_type: str, df: pd.DataFrame, column_types: Dict) -> Dict:
        """Suggest which columns to use"""
        x, y, color = self._select_columns(chart_type, df, column_types)
        return {
            "x_axis": x,
            "y_axis": y,
            "color_by": color,
            "alternatives": {
                "datetime": [c for c, t in column_types.items() if t == "datetime"],
                "numeric": [c for c, t in column_types.items() if t == "numeric"],
                "categorical": [c for c, t in column_types.items() if t == "categorical"]
            }
        }
    
    def _get_default_recommendations(self) -> List[ChartRecommendation]:
        """Return default recommendations when data analysis fails"""
        return [
            ChartRecommendation(
                "bar",
                "Sample Bar Chart",
                "Compare values across categories",
                {"chart_type": "bar"}
            ),
            ChartRecommendation(
                "line",
                "Sample Line Chart", 
                "Show trends over time",
                {"chart_type": "line"}
            ),
            ChartRecommendation(
                "scatter",
                "Sample Scatter Chart",
                "Explore relationships between variables",
                {"chart_type": "scatter"}
            )
        ]
