from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.responses import StreamingResponse
import json
from app.core.database import get_db
from app.models.excel_raw import ExcelRowRaw

router = APIRouter(prefix="/api/stream", tags=["STREAM"])

async def stream_rows(db: AsyncSession):
    result = await db.stream(select(ExcelRowRaw))
    async for row in result.scalars():
        yield json.dumps({
            "id": row.id,
            "sheet_id": row.sheet_id,
            "row_index": row.row_index,
            "row_data": row.row_data
        }) + "\n"

@router.get("/rows")
async def stream_api(db: AsyncSession = Depends(get_db)):
    return StreamingResponse(stream_rows(db), media_type="application/json")
