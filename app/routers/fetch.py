from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.fetch_log import FetchLog, FetchStatus
from app.models.source import Source
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.fetch_log_schema import (
    FetchLogResponse, FetchLogList, FetchLogFilter
)

router = APIRouter()


@router.get("/logs", response_model=FetchLogList)
async def get_fetch_logs(
        status: Optional[str] = Query(None),
        source_id: Optional[int] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(25, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = db.query(FetchLog)

    if status:
        query = query.filter(FetchLog.status == status)

    if source_id:
        query = query.filter(FetchLog.source_id == source_id)

    # Count total and by status
    total = query.count()
    success_count = query.filter(FetchLog.status == FetchStatus.SUCCESS).count()
    warning_count = query.filter(FetchLog.status == FetchStatus.WARNING).count()
    error_count = query.filter(FetchLog.status == FetchStatus.ERROR).count()
    info_count = query.filter(FetchLog.status == FetchStatus.INFO).count()

    # Pagination
    offset = (page - 1) * page_size
    logs = query.order_by(FetchLog.created_at.desc()).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "success_count": success_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "info_count": info_count,
        "items": logs
    }


@router.post("/now")
async def fetch_now(
        source_id: Optional[int] = None,
        background_tasks: BackgroundTasks = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    from app.businessLogic.source_service import fetch_from_source, fetch_from_all_sources

    if source_id:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found"
            )

        if not source.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot fetch from disabled source"
            )

        # Trigger fetch in background
        background_tasks.add_task(fetch_from_source, db, source_id)

        return {
            "message": f"Fetch started for {source.name}",
            "source_id": source_id,
            "source_name": source.name
        }
    else:
        # Fetch all active sources
        background_tasks.add_task(fetch_from_all_sources, db)

        active_count = db.query(Source).filter(Source.is_active == True).count()

        return {
            "message": "Fetch started for all active sources",
            "active_sources": active_count
        }


@router.get("/status")
async def get_fetch_status(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    from sqlalchemy import func

    # Get last successful fetch
    last_success = db.query(FetchLog).filter(
        FetchLog.status == FetchStatus.SUCCESS
    ).order_by(FetchLog.created_at.desc()).first()

    # Get sources that haven't been fetched in 24 hours
    day_ago = datetime.utcnow() - timedelta(hours=24)
    stale_sources = db.query(Source).filter(
        Source.is_active == True,
        Source.last_fetch_at < day_ago
    ).count()

    return {
        "last_sync": last_success.created_at if last_success else None,
        "last_sync_message": last_success.message if last_success else "No successful fetch yet",
        "stale_sources": stale_sources,
        "is_fetching": False  # TODO: Track actual fetch status
    }


@router.delete("/logs/clear")
async def clear_old_logs(
        days: int = Query(30, ge=7, le=365),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    deleted = db.query(FetchLog).filter(
        FetchLog.created_at < cutoff_date
    ).delete()

    db.commit()

    return {
        "message": f"Deleted {deleted} log entries older than {days} days",
        "deleted_count": deleted
    }