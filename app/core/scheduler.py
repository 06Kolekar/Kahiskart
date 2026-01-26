from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.businessLogic.excel_processor import ExcelProcessor
from app.businessLogic.onedrive_service import OneDriveService

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)


async def fetch_all_sources_job():
    from app.businessLogic.source_service import fetch_from_all_sources

    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting scheduled fetch job...")
            await fetch_from_all_sources(db)
            logger.info("Scheduled fetch job completed")
        except Exception as e:
            logger.error(f"Error in scheduled fetch job: {str(e)}")


async def keyword_matching_job():
    from app.businessLogic.tender_service import run_keyword_matching

    async with AsyncSessionLocal() as db:
        try:
            logger.info("Starting keyword matching job...")
            await run_keyword_matching(db)
            logger.info("Keyword matching job completed")
        except Exception as e:
            logger.error(f"Error in keyword matching job: {str(e)}")

# --------------------------------------------------
# EXCEL INGESTION (ONEDRIVE)
# --------------------------------------------------
async def run_excel_ingestion():
    logger.info("Running Excel ingestion...")

    async with AsyncSessionLocal() as db:
        try:
            onedrive = OneDriveService()

            result = await onedrive.download_excel(
                settings.ONEDRIVE_SHARE_LINK
            )

            if not result:
                logger.warning("No Excel file downloaded")
                return

            processor = ExcelProcessor(db)

            await processor.process_excel(
                file_content=result["content"],
                file_name=result["file_name"],
                file_hash=result["file_hash"],
                etag=result["etag"],
                last_modified=result["last_modified"],
            )

            logger.info("Excel ingestion completed successfully")

        except Exception:
            await db.rollback()
            logger.exception("Excel ingestion failed")
            raise

# Add jobs to scheduler
scheduler.add_job(
    fetch_all_sources_job,
    CronTrigger(hour='*/6'),  # Every 6 hours
    id='fetch_all_sources',
    name='Fetch all tender sources',
    replace_existing=True
)

scheduler.add_job(
    keyword_matching_job,
    CronTrigger(hour='*/1'),  # Every hour
    id='keyword_matching',
    name='Run keyword matching',
    replace_existing=True
)

scheduler.add_job(
    run_excel_ingestion,
    CronTrigger(minute="*/5"),  # Every 5 minutes
    id="excel_ingestion",
    replace_existing=True,
)