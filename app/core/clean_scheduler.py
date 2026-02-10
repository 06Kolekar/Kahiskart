import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.businessLogic.excel_processor_clean import CleanTransformer
from app.core.database import AsyncSessionLocal

scheduler = AsyncIOScheduler()

# Job function
async def run_clean_job():
    async with AsyncSessionLocal() as db:
        await CleanTransformer.enterprise_clean(db)

# Wrapper for APScheduler
def start_clean_scheduler():
    scheduler.add_job(run_clean_job, "interval", minutes=1)
    scheduler.start()
    print(" Clean Scheduler Started")
