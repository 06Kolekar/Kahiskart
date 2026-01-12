from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.tender import Tender
from app.models.keyword import Keyword
from app.models.source import Source
from app.auth.dependencies import get_current_user

router = APIRouter()


@router.get("/dashboard/stats")
def get_dashboard_stats(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get dashboard statistics
    Matches all cards on Dashboard page
    """
    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    yesterday_start = today_start - timedelta(days=1)

    # New tenders today
    new_today = db.query(Tender).filter(Tender.created_at >= today_start).count()
    new_yesterday = db.query(Tender).filter(
        and_(
            Tender.created_at >= yesterday_start,
            Tender.created_at < today_start
        )
    ).count()

    # Calculate percentage change
    new_change = 0
    if new_yesterday > 0:
        new_change = ((new_today - new_yesterday) / new_yesterday) * 100

    # Keyword matches today
    matched_today = db.query(Tender).filter(
        and_(
            Tender.is_matched == True,
            Tender.created_at >= today_start
        )
    ).count()

    matched_yesterday = db.query(Tender).filter(
        and_(
            Tender.is_matched == True,
            Tender.created_at >= yesterday_start,
            Tender.created_at < today_start
        )
    ).count()

    matched_change = 0
    if matched_yesterday > 0:
        matched_change = ((matched_today - matched_yesterday) / matched_yesterday) * 100

    # Active sources
    active_sources = db.query(Source).filter(Source.is_active == True).count()
    total_sources = db.query(Source).count()

    # Alerts today (new + matched)
    alerts_today = new_today + matched_today

    # Top keywords with match counts
    top_keywords = db.query(
        Keyword.keyword,
        Keyword.group_name,
        func.count(Tender.id).label('match_count')
    ).join(
        Tender,
        Tender.matched_keywords.like(func.concat('%', Keyword.keyword, '%'))
    ).filter(
        Tender.created_at >= today_start - timedelta(days=30)
    ).group_by(
        Keyword.id
    ).order_by(
        desc('match_count')
    ).limit(5).all()

    return {
        "new_tenders_today": new_today,
        "new_tenders_change": round(new_change, 1),
        "keyword_matches_today": matched_today,
        "keyword_matches_change": round(matched_change, 1),
        "active_sources": active_sources,
        "total_sources": total_sources,
        "alerts_today": alerts_today,
        "top_keywords": [
            {
                "keyword": kw[0],
                "category": kw[1],
                "matches": kw[2]
            } for kw in top_keywords
        ]
    }


@router.get("/dashboard/recent-tenders")
def get_recent_tenders(
        limit: int = Query(5, ge=1, le=20),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get recent tenders for dashboard
    Shows in "Recent Tenders" section
    """
    tenders = db.query(Tender).order_by(
        desc(Tender.publish_date)
    ).limit(limit).all()

    return tenders


@router.get("/dashboard/source-status")
def get_source_status_overview(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """
    Get source status overview
    For "Source Status Overview" section
    """
    from app.models.fetch_log import FetchLog

    sources = db.query(Source).filter(Source.is_active == True).all()

    result = []
    today_start = datetime.now().replace(hour=0, minute=0, second=0)

    for source in sources:
        # Get today's tender count
        tender_count = db.query(Tender).filter(
            and_(
                Tender.source_name == source.name,
                Tender.created_at >= today_start
            )
        ).count()

        result.append({
            "name": source.name,
            "status": source.fetch_status,
            "tenders_today": tender_count,
            "last_fetch": source.last_fetch
        })

    return result