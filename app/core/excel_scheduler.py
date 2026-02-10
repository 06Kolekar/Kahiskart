from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.database import AsyncSessionLocal
from app.businessLogic.excel_background_runner import ExcelBackgroundRunner

scheduler = AsyncIOScheduler()

async def run_excel_job():
    async with AsyncSessionLocal() as db:
        await ExcelBackgroundRunner.run_excel_sync(db)

def start_excel_scheduler():
    scheduler.add_job(run_excel_job, "interval", minutes=30)
    scheduler.start()
    print("[./\.] Excel Scheduler Running (30 min interval) [./\.]")
