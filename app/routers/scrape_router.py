from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.source import Source
from app.scraping.implementations.html_scraper import HTMLScraper
from app.scraping.implementations.pdf_scraper import PDFScraper
from app.scraping.base.login_scraper import LoginScraper
from app.businessLogic.tender_service import TenderService
from app.businessLogic.scraper_service import ScraperService


router = APIRouter()

@router.post("/scrape/{source_id}")
async def scrape_source(source_id: int, db: AsyncSession = Depends(get_db)):

    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    tenders = await ScraperService.scrape_tenders_from_source(source)

    saved_count = 0

    for tender_data in tenders:
        await TenderService.create_tender(
            db=db,
            tender_data=tender_data,
            source_id=source.id
        )
        saved_count += 1

    return {
        "message": "Scraping completed",
        "saved_tenders": saved_count
    }
