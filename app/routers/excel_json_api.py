from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.excel_raw import ExcelRowRaw

router = APIRouter(prefix="/api/json", tags=["JSON API"])

@router.get("/rows")
async def get_rows(limit: int = 1000, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ExcelRowRaw).limit(limit))
    rows = result.scalars().all()

    return [
        {
            "id": r.id,
            "sheet_id": r.sheet_id,
            "row_index": r.row_index,
            "row_data": r.row_data,
            "created_at": str(r.created_at)
        }
        for r in rows
    ]
