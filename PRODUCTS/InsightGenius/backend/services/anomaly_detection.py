"""
Anomaly Detection Service
AI-powered anomaly detection for business metrics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor

from core.logging import logger

class AnomalyDetectionService:
    """Service for detecting anomalies in business data"""
    
    def __init__(self):
        self.sensitivity_thresholds = {
            "low": 0.1,
            "medium": 0.05,
            "high": 0.01
        }
    
    async def detect_anomalies(self, dataset, columns: List[str], 
                               sensitivity: str = "medium",
                               time_window: str = "1d") -> List[Dict]:
        """Detect anomalies in dataset"""
        try:
            # Load data
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            if df.empty or not columns:
                return []
            
            # Filter to requested columns
            available_cols = [c for c in columns if c in df.columns]
            if not available_cols:
                return []
            
            # Get numeric columns only
            numeric_cols = df[available_cols].select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                return []
            
            # Prepare data
            X = df[numeric_cols].fillna(df[numeric_cols].mean()).values
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Apply Isolation Forest
            contamination = self.sensitivity_thresholds.get(sensitivity, 0.05)
            
            clf = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            
            predictions = clf.fit_predict(X_scaled)
            scores = clf.decision_function(X_scaled)
            
            # Find anomalies
            anomalies = []
            for idx in np.where(predictions == -1)[0]:
                row_data = df.iloc[idx]
                
                # Calculate severity
                anomaly_score = abs(scores[idx])
                if anomaly_score > 0.6:
                    severity = "critical"
                elif anomaly_score > 0.4:
                    severity = "high"
                elif anomaly_score > 0.2:
                    severity = "medium"
                else:
                    severity = "low"
                
                # Identify affected columns
                affected = self._identify_affected_columns(X_scaled[idx], scaler, numeric_cols)
                
                anomaly = {
                    "index": int(idx),
                    "timestamp": datetime.utcnow().isoformat(),
                    "anomaly_score": float(anomaly_score),
                    "is_anomaly": True,
                    "severity": severity,
                    "affected_columns": affected,
                    "column_scores": {
                        col: float(X_scaled[idx][i]) 
                        for i, col in enumerate(numeric_cols)
                    },
                    "explanation": self._generate_explanation(affected, row_data, numeric_cols),
                    "data_snapshot": row_data.to_dict()
                }
                anomalies.append(anomaly)
            
            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            anomalies.sort(key=lambda x: severity_order.get(x["severity"], 4))
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _identify_affected_columns(self, scaled_values: np.ndarray, scaler, columns: List[str]) -> List[str]:
        """Identify which columns contribute most to anomaly"""
        # Columns with z-score > 2 or < -2 are significant contributors
        affected = []
        for i, col in enumerate(columns):
            if abs(scaled_values[i]) > 2:
                affected.append(col)
        return affected if affected else [columns[np.argmax(np.abs(scaled_values))]]
    
    def _generate_explanation(self, affected_columns: List[str], row_data: pd.Series, 
                              all_columns: List[str]) -> str:
        """Generate human-readable explanation for anomaly"""
        if not affected_columns:
            return "Unusual pattern detected across multiple metrics"
        
        explanations = []
        for col in affected_columns[:3]:  # Top 3
            value = row_data.get(col)
            
            # Calculate how far from mean (approximate)
            explanations.append(f"{col} = {value:.2f} (unusual value)")
        
        return "; ".join(explanations)
    
    async def detect_trend_anomalies(self, dataset, column: str, 
                                     window: str = "7d") -> List[Dict]:
        """Detect trend-based anomalies"""
        try:
            df = pd.DataFrame(dataset.sample_data) if dataset.sample_data else pd.DataFrame()
            if df.empty or column not in df.columns:
                return []
            
            # Ensure datetime index
            if 'date' in df.columns or 'timestamp' in df.columns:
                time_col = 'date' if 'date' in df.columns else 'timestamp'
                df[time_col] = pd.to_datetime(df[time_col])
                df = df.set_index(time_col)
            
            # Calculate rolling statistics
            window_size = 7 if window == "7d" else (30 if window == "30d" else 1)
            
            rolling_mean = df[column].rolling(window=window_size).mean()
            rolling_std = df[column].rolling(window=window_size).std()
            
            # Detect deviations
            upper_bound = rolling_mean + 2 * rolling_std
            lower_bound = rolling_mean - 2 * rolling_std
            
            anomalies = []
            for idx in df.index:
                value = df.loc[idx, column]
                if value > upper_bound.loc[idx] or value < lower_bound.loc[idx]:
                    anomalies.append({
                        "timestamp": idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                        "value": float(value),
                        "expected_range": [
                            float(lower_bound.loc[idx]),
                            float(upper_bound.loc[idx])
                        ],
                        "deviation": float(abs(value - rolling_mean.loc[idx])),
                        "severity": "high" if abs(value - rolling_mean.loc[idx]) > 3 * rolling_std.loc[idx] else "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Trend anomaly detection failed: {e}")
            return []
