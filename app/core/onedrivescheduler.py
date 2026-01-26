# import logging
# import asyncio
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from datetime import datetime

# from app.core.config import settings
# from app.core.database import AsyncSessionLocal
# from app.businessLogic.excel_processor import ExcelProcessor
# from app.businessLogic.onedrive_service import OneDriveService

# logger = logging.getLogger(__name__)

# class OneDriveScheduler:
#     """Async Scheduler for automatic OneDrive Excel processing"""

#     def __init__(self):
#         self.scheduler = AsyncIOScheduler()
#         self.is_running = False

#     def start(self):
#         if not self.is_running:
#             # Schedule ingestion every X seconds defined in settings
#             self.scheduler.add_job(
#                 self.process_onedrive_file,
#                 trigger=IntervalTrigger(seconds=settings.ONEDRIVE_POLL_INTERVAL),
#                 id="onedrive_file_check",
#                 name="Check and process OneDrive file",
#                 replace_existing=True,
#             )
#             self.scheduler.start()
#             self.is_running = True
#             logger.info(f"OneDrive scheduler started. Polling every {settings.ONEDRIVE_POLL_INTERVAL}s")

#     async def process_onedrive_file(self):
#         async with AsyncSessionLocal() as db:
#             try:
#                 logger.info(f"[{datetime.utcnow()}] Checking OneDrive file for updates...")

#                 onedrive = OneDriveService()
#                 file_content = onedrive.download_excel_file(settings.ONEDRIVE_SHARE_LINK)
#                 if not file_content:
#                     logger.warning("No Excel file downloaded")
#                     return

#                 processor = ExcelProcessor(db)
#                 await processor.process_excel(file_content)

#                 logger.info("OneDrive Excel ingestion completed")

#             except Exception as e:
#                 logger.error(f"Error in OneDrive processing: {str(e)}", exc_info=True)

#     def run_now(self):
#         """Manual trigger"""
#         asyncio.create_task(self.process_onedrive_file())
#         logger.info("Manual trigger: Processing OneDrive file now")


# # Global instance
# onedrive_scheduler = OneDriveScheduler()

# app/core/onedrive_scheduler.py

# app/core/onedrive_scheduler.py

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.businessLogic.onedrive_service import OneDriveService
from app.businessLogic.excel_processor import ExcelProcessor

logger = logging.getLogger(__name__)


class OneDriveScheduler:

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False

    def start(self):
        if self.running:
            return

        self.scheduler.add_job(
            self.process_onedrive_excel,
            IntervalTrigger(seconds=settings.ONEDRIVE_POLL_INTERVAL),
            id="onedrive_excel_job",
            replace_existing=True,
        )

        self.scheduler.start()
        self.running = True
        logger.info("OneDrive scheduler started")

    async def process_onedrive_excel(self):
        logger.info(f"[{datetime.utcnow()}] Checking OneDrive Excel")

        async with AsyncSessionLocal() as db:
            service = OneDriveService()
            processor = ExcelProcessor(db)

            result = await service.download_excel(
                settings.ONEDRIVE_SHARE_LINK
            )
            if not result:
                return

            await processor.process_excel(
                file_content=result["content"],
                file_name=result["file_name"],
                file_hash=result["file_hash"],
                etag=result["etag"],
                last_modified=result["last_modified"],
            )


onedrive_scheduler = OneDriveScheduler()

