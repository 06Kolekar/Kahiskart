# from fastapi import APIRouter
# from app.businessLogic.excel_processor_local import ExcelProcessorLocal

# router = APIRouter(prefix="/excel", tags=["Excel"])

# @router.post("/test-load")
# async def test_excel_load():
#     await ExcelProcessorLocal.process_excel_once()
#     return {"status": "Excel loaded (test rows only)"}
from fastapi import APIRouter
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from datetime import datetime
from app.models.excel_raw import ExcelFile

router = APIRouter(prefix="/excel", tags=["Excel"])


@router.post("/register-file")
async def register_excel_file(path: str):
    # Convert Windows path → Unix style
    path = path.replace("\\", "/")

    async with AsyncSessionLocal() as db:

        # Check existing
        result = await db.execute(
            select(ExcelFile).where(ExcelFile.file_path == path)
        )
        existing = result.scalar_one_or_none()

        if existing:
            return {"status": "already exists", "id": existing.id}

        excel_file = ExcelFile(
            file_path=path,
            created_at=datetime.utcnow()
        )
        db.add(excel_file)
        await db.commit()
        await db.refresh(excel_file)

    return {"status": "registered", "id": excel_file.id}
