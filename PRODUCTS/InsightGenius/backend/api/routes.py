"""
Main API Router
"""

from fastapi import APIRouter

from api.endpoints import (
    auth,
    data_sources,
    datasets,
    visualizations,
    dashboards,
    ml_models,
    predictions,
    alerts,
    reports,
    nlp_queries,
    export,
    realtime
)

router = APIRouter()

# Auth
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Data
router.include_router(data_sources.router, prefix="/data-sources", tags=["Data Sources"])
router.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])

# Visualization & Dashboards
router.include_router(visualizations.router, prefix="/visualizations", tags=["Visualizations"])
router.include_router(dashboards.router, prefix="/dashboards", tags=["Dashboards"])

# ML & Predictions
router.include_router(ml_models.router, prefix="/ml-models", tags=["ML Models"])
router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])

# Alerts & Reports
router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# NLP & Export
router.include_router(nlp_queries.router, prefix="/query", tags=["NLP Queries"])
router.include_router(export.router, prefix="/export", tags=["Export"])

# Real-time
router.include_router(realtime.router, prefix="/realtime", tags=["Real-time"])
