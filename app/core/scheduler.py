from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal

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


