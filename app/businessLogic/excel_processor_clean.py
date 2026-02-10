from sqlalchemy import select
from app.models.excel_raw import ExcelRowRaw
from app.models.excel_row_clean import ExcelRowClean
import hashlib

BATCH_SIZE = 10000  # 10K rows per batch

class CleanTransformer:

    @staticmethod
    async def enterprise_clean(db):
        offset = 0

        while True:
            query = select(ExcelRowRaw).offset(offset).limit(BATCH_SIZE)
            result = await db.execute(query)
            rows = result.scalars().all()

            if not rows:
                break

            await CleanTransformer.process_batch(db, rows)

            offset += BATCH_SIZE
            print(f"Processed batch offset={offset}")

    @staticmethod
    async def process_batch(db, rows):
        clean_objects = []

        for r in rows:
            data = r.row_data or {}

            title = data.get("title")
            agency = data.get("agency")
            vendor = data.get("vendor")

            hash_val = hashlib.md5(str(data).encode()).hexdigest()

            clean_objects.append(
                ExcelRowClean(
                    sheet_id=r.sheet_id,
                    title=title,
                    agency=agency,
                    vendor=vendor,
                    row_hash=hash_val
                )
            )

        db.add_all(clean_objects)
        await db.commit()
