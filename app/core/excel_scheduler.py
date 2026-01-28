from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
import logging
from datetime import datetime
from app.core.database import AsyncSessionLocal
from app.businessLogic.excel_processor import ExcelProcessor

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)


def local_excel_job():
    db = AsyncSessionLocal()
    try:
        logger.info(f"[{datetime.utcnow()}] Checking local Excel...")
        processor = ExcelProcessor(db)
        processor.process_local_excel(
            file_path=settings.LOCAL_EXCEL_PATH,
            force_refresh=False
        )
    except Exception:
        logger.exception("Local Excel job failed")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        local_excel_job,
        IntervalTrigger(seconds=settings.EXCEL_POLL_INTERVAL),
        id="local_excel_ingest",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Local Excel scheduler started")
