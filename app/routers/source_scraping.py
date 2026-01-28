from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.source_scraping import SourceScraping
from app.schemas.source_scraping import SourceScrapingCreate, SourceScrapingOut

router = APIRouter(prefix="/source-scraping", tags=["Source Scraping"])


@router.post("/", response_model=SourceScrapingOut)
def create_source_scraping(
    payload: SourceScrapingCreate,
    db: Session = Depends(get_db)
):
    record = SourceScraping(
        source_id=payload.source_id,
        page_url=str(payload.page_url),
        page_title=payload.page_title,
        search_keyword=payload.search_keyword,
        page_type=payload.page_type,
        actions=[a.dict() for a in payload.actions],
        results_mapping=payload.results_mapping.dict() if payload.results_mapping else None
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record
