"""
Visualization Service
Handles chart rendering and D3.js configuration
"""

import json
from typing import Dict, Any, List
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

from core.logging import logger

class VisualizationService:
    """Service for creating and rendering visualizations"""
    
    def __init__(self):
        self.color_schemes = {
            "default": ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"],
            "dark": ["#60a5fa", "#34d399", "#fbbf24", "#f87171", "#a78bfa", "#f472b6"],
            "warm": ["#f97316", "#f59e0b", "#eab308", "#ef4444", "#dc2626", "#991b1b"],
            "cool": ["#06b6d4", "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef"]
        }
    
    async def render(self, visualization, format: str, width: int, height: int) -> Dict:
        """Render visualization to specified format"""
        try:
            # Get data
            data = await self._fetch_data(visualization)
            
            if format == "json":
                return {"data": data, "config": visualization.config}
            
            elif format == "html":
                fig = self._create_plotly_figure(visualization, data)
                html = fig.to_html(include_plotlyjs='cdn', full_html=False)
                return {"html": html}
            
            elif format in ["png", "jpg", "svg"]:
                fig = self._create_plotly_figure(visualization, data)
                img_bytes = fig.to_image(format=format, width=width, height=height)
                return {"image_data": img_bytes, "format": format}
            
            else:
                return {"error": f"Unsupported format: {format}"}
                
        except Exception as e:
            logger.error(f"Render failed: {e}")
            return {"error": str(e)}
    
    async def generate_d3_config(self, visualization) -> Dict:
        """Generate D3.js configuration for frontend rendering"""
        try:
            data = await self._fetch_data(visualization)
            config = visualization.config
            chart_type = visualization.chart_type
            
            # Base D3 configuration
            d3_config = {
                "chartType": chart_type,
                "data": data,
                "dimensions": {
                    "width": 800,
                    "height": 400,
                    "margin": {"top": 20, "right": 20, "bottom": 40, "left": 60}
                },
                "scales": self._get_d3_scales(chart_type, data, config),
                "axes": self._get_d3_axes(chart_type, data, config),
                "marks": self._get_d3_marks(chart_type, data, config),
                "colors": self.color_schemes.get(config.get("color_scheme", "default"), self.color_schemes["default"]),
                "interactions": {
                    "tooltip": True,
                    "zoom": config.get("enable_zoom", True),
                    "brush": config.get("enable_brush", False),
                    "click": True
                },
                "animation": {
                    "duration": 750,
                    "easing": "ease-in-out"
                }
            }
            
            return d3_config
            
        except Exception as e:
            logger.error(f"D3 config generation failed: {e}")
            return {"error": str(e)}
    
    def _create_plotly_figure(self, visualization, data: pd.DataFrame):
        """Create Plotly figure"""
        chart_type = visualization.chart_type
        config = visualization.config
        
        colors = self.color_schemes.get(config.get("color_scheme", "default"))
        
        if chart_type == "line":
            fig = px.line(
                data,
                x=config.get("x_axis", {}).get("column"),
                y=config.get("y_axis", [{}])[0].get("column"),
                color=config.get("color_by"),
                title=visualization.name
            )
        
        elif chart_type == "bar":
            fig = px.bar(
                data,
                x=config.get("x_axis", {}).get("column"),
                y=config.get("y_axis", [{}])[0].get("column"),
                color=config.get("color_by"),
                barmode=config.get("barmode", "group"),
                title=visualization.name
            )
        
        elif chart_type == "scatter":
            fig = px.scatter(
                data,
                x=config.get("x_axis", {}).get("column"),
                y=config.get("y_axis", [{}])[0].get("column"),
                color=config.get("color_by"),
                size=config.get("size_by"),
                title=visualization.name
            )
        
        elif chart_type == "pie":
            fig = px.pie(
                data,
                names=config.get("labels_column"),
                values=config.get("values_column"),
                title=visualization.name
            )
        
        elif chart_type == "heatmap":
            pivot_data = data.pivot(
                index=config.get("y_column"),
                columns=config.get("x_column"),
                values=config.get("value_column")
            )
            fig = px.imshow(pivot_data, title=visualization.name)
        
        elif chart_type == "area":
            fig = px.area(
                data,
                x=config.get("x_axis", {}).get("column"),
                y=config.get("y_axis", [{}])[0].get("column"),
                color=config.get("color_by"),
                title=visualization.name
            )
        
        else:
            # Default to table
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(data.columns)),
                cells=dict(values=[data[col] for col in data.columns])
            )])
        
        # Apply styling
        fig.update_layout(
            template="plotly_dark" if config.get("theme") == "dark" else "plotly_white",
            colorway=colors,
            showlegend=config.get("show_legend", True)
        )
        
        return fig
    
    def _get_d3_scales(self, chart_type: str, data: pd.DataFrame, config: Dict) -> Dict:
        """Generate D3 scale configuration"""
        scales = {}
        
        x_col = config.get("x_axis", {}).get("column")
        y_col = config.get("y_axis", [{}])[0].get("column") if config.get("y_axis") else None
        
        if x_col and x_col in data.columns:
            if pd.api.types.is_datetime64_any_dtype(data[x_col]):
                scales["x"] = {"type": "time", "domain": [data[x_col].min(), data[x_col].max()]}
            elif pd.api.types.is_numeric_dtype(data[x_col]):
                scales["x"] = {"type": "linear", "domain": [data[x_col].min(), data[x_col].max()]}
            else:
                scales["x"] = {"type": "band", "domain": data[x_col].unique().tolist()}
        
        if y_col and y_col in data.columns and pd.api.types.is_numeric_dtype(data[y_col]):
            scales["y"] = {"type": "linear", "domain": [0, data[y_col].max() * 1.1]}
        
        return scales
    
    def _get_d3_axes(self, chart_type: str, data: pd.DataFrame, config: Dict) -> Dict:
        """Generate D3 axis configuration"""
        return {
            "x": {
                "label": config.get("x_axis_label", config.get("x_axis", {}).get("column", "")),
                "format": config.get("x_axis_format", "")
            },
            "y": {
                "label": config.get("y_axis_label", config.get("y_axis", [{}])[0].get("column", "") if config.get("y_axis") else ""),
                "format": config.get("y_axis_format", "")
            }
        }
    
    def _get_d3_marks(self, chart_type: str, data: pd.DataFrame, config: Dict) -> Dict:
        """Generate D3 mark configuration"""
        marks = {"type": chart_type}
        
        if chart_type == "line":
            marks["strokeWidth"] = 2
            marks["curve"] = "monotoneX"
            marks["dots"] = config.get("show_dots", True)
        
        elif chart_type == "bar":
            marks["padding"] = 0.1
            marks["cornerRadius"] = 2
        
        elif chart_type == "scatter":
            marks["radius"] = 5
            marks["opacity"] = 0.7
        
        return marks
    
    async def _fetch_data(self, visualization) -> pd.DataFrame:
        """Fetch data for visualization"""
        # TODO: Fetch from actual dataset
        # For now, return sample data
        import numpy as np
        
        np.random.seed(42)
        dates = pd.date_range("2024-01-01", periods=30, freq="D")
        
        return pd.DataFrame({
            "date": dates,
            "value": np.random.randn(30).cumsum() + 100,
            "category": np.random.choice(["A", "B", "C"], 30),
            "sales": np.random.randint(50, 200, 30)
        })
