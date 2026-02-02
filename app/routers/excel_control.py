# # from fastapi import APIRouter
# # from app.businessLogic.excel_processor_local import ExcelProcessorLocal

# # router = APIRouter(prefix="/excel", tags=["Excel"])

# # @router.post("/test-load")
# # async def test_excel_load():
# #     await ExcelProcessorLocal.process_excel_once()
# #     return {"status": "Excel loaded (test rows only)"}
# from fastapi import APIRouter
# from app.core.database import AsyncSessionLocal
# from sqlalchemy import select
# from datetime import datetime
# from app.models.excel_raw import ExcelFile

# router = APIRouter(prefix="/excel", tags=["Excel"])


# @router.post("/register-file")
# async def register_excel_file(path: str):
#     # Convert Windows path → Unix style
#     path = path.replace("\\", "/").strip('\'"')

#     async with AsyncSessionLocal() as db:

#         # Check existing
#         result = await db.execute(
#             select(ExcelFile).where(ExcelFile.file_path == path)
#         )
#         existing = result.scalar_one_or_none()

#         if existing:
#             return {"status": "already exists", "id": existing.id}

#         excel_file = ExcelFile(
#             file_path=path,
#             created_at=datetime.utcnow()
#         )
#         db.add(excel_file)
#         await db.commit()
#         await db.refresh(excel_file)

#     return {"status": "registered", "id": excel_file.id}

from fastapi import APIRouter, Query
from app.core.database import AsyncSessionLocal
from sqlalchemy import select, func
from datetime import datetime
from app.models.excel_raw import ExcelFile
from app.models.excel_raw import ExcelRowRaw

router = APIRouter(prefix="/excel", tags=["Excel"])


# Register Excel File Path
@router.post("/register-file")
async def register_excel_file(path: str):
    path = path.replace("\\", "/").strip('\'"')

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ExcelFile).where(ExcelFile.file_path == path))
        existing = result.scalar_one_or_none()

        if existing:
            return {"status": "already exists", "id": existing.id}

        excel_file = ExcelFile(file_path=path, created_at=datetime.utcnow())
        db.add(excel_file)
        await db.commit()
        await db.refresh(excel_file)

    return {"status": "registered", "id": excel_file.id}



# GET ALL REGISTERED FILES
@router.get("/files")
async def get_all_excel_files():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ExcelFile))
        files = result.scalars().all()

        return [
            {
                "id": f.id,
                "file_path": f.file_path,
                "created_at": f.created_at
            }
            for f in files
        ]



# GET FILE BY ID
@router.get("/file/{file_id}")
async def get_excel_file(file_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ExcelFile).where(ExcelFile.id == file_id))
        file = result.scalar_one_or_none()

        if not file:
            return {"error": "File not found"}

        return {
            "id": file.id,
            "file_path": file.file_path,
            "created_at": file.created_at
        }



# PAGINATION (Enterprise Style)
@router.get("/files/paginated")
async def get_files_paginated(
    limit: int = Query(10, le=100),
    offset: int = Query(0)
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ExcelFile).limit(limit).offset(offset))
        files = result.scalars().all()

        return {
            "count": len(files),
            "data": [
                {"id": f.id, "file_path": f.file_path, "created_at": f.created_at}
                for f in files
            ]
        }

# @router.get("/all")
# async def get_all_rows():
#     async with AsyncSessionLocal() as db:
#         result = await db.execute(select(ExcelRowRaw))
#         rows = result.scalars().all()

#         return [
#             {
#                 "id": r.id,
#                 "sheet_id": r.sheet_id,
#                 "row_index": r.row_index,
#                 "row_data": r.row_data,
#                 "created_at": r.created_at
#             }
#             for r in rows
#         ]

@router.get("/all")
async def get_all_rows_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(100, le=1000)
):
    offset = (page - 1) * limit

    async with AsyncSessionLocal() as db:

        # Get total rows count
        total_result = await db.execute(select(func.count()).select_from(ExcelRowRaw))
        total_rows = total_result.scalar()

        # Fetch paginated rows
        result = await db.execute(
            select(ExcelRowRaw)
            .order_by(ExcelRowRaw.id)
            .limit(limit)
            .offset(offset)
        )
        rows = result.scalars().all()

        return {
            "page": page,
            "limit": limit,
            "total_rows": total_rows,
            "total_pages": (total_rows // limit) + (1 if total_rows % limit else 0),
            "data": [
                {
                    "id": r.id,
                    "sheet_id": r.sheet_id,
                    "row_index": r.row_index,
                    "row_data": r.row_data,
                    "created_at": r.created_at
                }
                for r in rows
            ]
        }


@router.get("/sheet/{sheet_id}")
async def get_rows_by_sheet(sheet_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ExcelRowRaw).where(ExcelRowRaw.sheet_id == sheet_id)
        )
        rows = result.scalars().all()

        return rows

@router.get("/paginated")
async def get_rows_paginated(
    sheet_id: int,
    limit: int = Query(50, le=500),
    offset: int = 0
):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ExcelRowRaw)
            .where(ExcelRowRaw.sheet_id == sheet_id)
            .limit(limit)
            .offset(offset)
        )
        rows = result.scalars().all()

        return {
            "sheet_id": sheet_id,
            "limit": limit,
            "offset": offset,
            "count": len(rows),
            "data": [
                {
                    "id": r.id,
                    "row_index": r.row_index,
                    "row_data": r.row_data
                }
                for r in rows
            ]
        }
