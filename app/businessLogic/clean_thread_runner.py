import asyncio
from app.core.database import AsyncSessionLocal
from app.businessLogic.excel_processor_clean import CleanTransformer

async def run_clean_job():
    async with AsyncSessionLocal() as db:
        await CleanTransformer.enterprise_clean(db)

# FOR MANUAL SCRIPT RUN
if __name__ == "__main__":
    asyncio.run(run_clean_job())
