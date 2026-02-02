from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, desc, select
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.tender import Tender
from app.models.keyword import Keyword
from app.models.source import Source
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ===========================
# DASHBOARD STATS
# ===========================
@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get dashboard statistics
    Matches all cards on Dashboard page
    """

    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    yesterday_start = today_start - timedelta(days=1)

    # New tenders today
    new_today = await db.scalar(
        select(func.count(Tender.id))
        .where(Tender.created_at >= today_start)
    ) or 0

    new_yesterday = await db.scalar(
        select(func.count(Tender.id))
        .where(
            and_(
                Tender.created_at >= yesterday_start,
                Tender.created_at < today_start
            )
        )
    ) or 0

    # Percentage change
    new_change = 0
    if new_yesterday > 0:
        new_change = ((new_today - new_yesterday) / new_yesterday) * 100

    # Keyword matches today
    matched_today = await db.scalar(
        select(func.count(Tender.id))
        .where(
            and_(
                Tender.is_matched == True,
                Tender.created_at >= today_start
            )
        )
    ) or 0

    matched_yesterday = await db.scalar(
        select(func.count(Tender.id))
        .where(
            and_(
                Tender.is_matched == True,
                Tender.created_at >= yesterday_start,
                Tender.created_at < today_start
            )
        )
    ) or 0

    matched_change = 0
    if matched_yesterday > 0:
        matched_change = (
            (matched_today - matched_yesterday) / matched_yesterday
        ) * 100

    # Active sources
    active_sources = await db.scalar(
        select(func.count(Source.id))
        .where(Source.is_active == True)
    ) or 0

    total_sources = await db.scalar(
        select(func.count(Source.id))
    ) or 0

    # Alerts today
    alerts_today = new_today + matched_today

    # Top keywords (last 30 days)
    thirty_days_ago = today_start - timedelta(days=30)

    result = await db.execute(
        select(
            Keyword.keyword,
            Keyword.group_name,
            func.count(Tender.id).label("match_count")
        )
        .join(
            Tender,
            Tender.matched_keywords.like(
                func.concat('%', Keyword.keyword, '%')
            )
        )
        .where(Tender.created_at >= thirty_days_ago)
        .group_by(Keyword.id, Keyword.keyword, Keyword.group_name)
        .order_by(desc("match_count"))
        .limit(5)
    )

    keywords_data = result.all()

    top_keywords = [
        {
            "keyword": k[0],
            "category": k[1],
            "matches": k[2]
        }
        for k in keywords_data
    ]

    return {
        "new_tenders_today": new_today,
        "new_tenders_change": round(new_change, 1),

        "keyword_matches_today": matched_today,
        "keyword_matches_change": round(matched_change, 1),

        "active_sources": active_sources,
        "total_sources": total_sources,

        "alerts_today": alerts_today,

        "top_keywords": top_keywords
    }


# ===========================
# RECENT TENDERS
# ===========================
@router.get("/recent-tenders")
async def get_recent_tenders(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get recent tenders for dashboard
    """

    result = await db.execute(
        select(Tender)
        .where(Tender.is_deleted == False)
        .order_by(desc(Tender.publish_date))
        .limit(limit)
    )

    tenders = result.scalars().all()

    tender_list = []

    for t in tenders:

        # Normalize status
        status = t.status.lower() if t.status else "viewed"

        # Safe keyword handling
        if isinstance(t.matched_keywords, str):
            keywords = [k.strip() for k in t.matched_keywords.split(",")]
        elif isinstance(t.matched_keywords, list):
            keywords = t.matched_keywords
        else:
            keywords = []

        tender_list.append({
            "id": t.id,
            "title": t.title,
            "reference_id": t.reference_id,

            "agency_name": t.agency_name,
            "agency_location": t.agency_location,

            "source_name": t.source_name,

            "deadline_date": t.deadline_date,
            "days_until_deadline": t.days_until_deadline,

            "status": status,
            "matched_keywords": keywords,

            "description": t.description,
            "source_url": t.source_url,

            "attachments": t.attachments or [],

            "created_at": t.created_at
        })

    return tender_list


# ===========================
# SOURCE STATUS
# ===========================
@router.get("/source-status")
async def get_source_status_overview(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get source status overview
    """

    today_start = datetime.now().replace(hour=0, minute=0, second=0)

    # Get tender counts per source (OPTIMIZED)
    result = await db.execute(
        select(
            Tender.source_name,
            func.count(Tender.id)
        )
        .where(Tender.created_at >= today_start)
        .group_by(Tender.source_name)
    )

    tender_counts = dict(result.all())

    # Get all sources
    result = await db.execute(
        select(Source)
        .where(Source.is_active == True)
    )

    sources = result.scalars().all()

    result_list = []

    for s in sources:

        count_today = tender_counts.get(s.name, 0)

        result_list.append({
            "name": s.name,

            "status": s.fetch_status or "UNKNOWN",

            "tenders_today": count_today,

            "last_fetch": (
                s.last_fetch.isoformat()
                if s.last_fetch
                else None
            )
        })

    return result_list
