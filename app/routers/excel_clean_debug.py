from fastapi import APIRouter
from app.businessLogic.excel_processor_clean import CleanTransformer
from app.core.database import AsyncSessionLocal

router = APIRouter()

@router.post("/clean/start")
async def start_clean():
    async with AsyncSessionLocal() as db:
        await CleanTransformer.enterprise_clean(db)
    return {"status": "started"}
