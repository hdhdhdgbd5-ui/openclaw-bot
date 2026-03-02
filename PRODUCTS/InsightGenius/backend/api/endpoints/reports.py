"""
Reports API Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.report import Report, ScheduledReport
from models.dashboard import Dashboard
from services.report_generator import ReportGeneratorService
from schemas.report import (
    ReportCreate,
    ReportUpdate,
    ScheduledReportCreate,
    ReportResponse
)

router = APIRouter()
report_service = ReportGeneratorService()

@router.post("/", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new report"""
    db_report = Report(
        name=report.name,
        description=report.description,
        report_type=report.report_type,
        source_id=report.source_id,
        sections=report.sections,
        formats=report.formats,
        template=report.template,
        branding=report.branding,
        owner_id=current_user.id
    )
    db.add(db_report)
    await db.commit()
    await db.refresh(db_report)
    return db_report

@router.post("/{report_id}/generate")
async def generate_report(
    report_id: int,
    format: str = "pdf",
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate report file"""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.owner_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Generate
    file_path = await report_service.generate(report, format)
    
    return {
        "message": "Report generated",
        "format": format,
        "download_url": f"/api/v1/export/download/{file_path}"
    }

@router.post("/{report_id}/schedule")
async def schedule_report(
    report_id: int,
    schedule: ScheduledReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule automated report delivery"""
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.owner_id == current_user.id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    db_schedule = ScheduledReport(
        report_id=report_id,
        name=schedule.name,
        frequency=schedule.frequency,
        cron_expression=schedule.cron_expression,
        recipients=schedule.recipients,
        subject=schedule.subject,
        message=schedule.message,
        is_active=True
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    
    # Schedule with Celery
    from tasks.report_tasks import schedule_report_task
    schedule_report_task.delay(db_schedule.id)
    
    return db_schedule

@router.get("/scheduled/")
async def list_scheduled_reports(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all scheduled reports for user"""
    result = await db.execute(
        select(ScheduledReport)
        .join(Report)
        .where(Report.owner_id == current_user.id)
    )
    return result.scalars().all()

@router.delete("/scheduled/{schedule_id}")
async def delete_scheduled_report(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a scheduled report"""
    result = await db.execute(
        select(ScheduledReport)
        .join(Report)
        .where(ScheduledReport.id == schedule_id, Report.owner_id == current_user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    await db.delete(schedule)
    await db.commit()
    
    return {"message": "Schedule deleted"}
