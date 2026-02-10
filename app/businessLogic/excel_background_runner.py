import os
import hashlib
import pandas as pd
from sqlalchemy import select, update
from app.models.excel_raw import ExcelFile, ExcelSheet, ExcelRowRaw
from datetime import datetime


class ExcelBackgroundRunner:

    @staticmethod
    def get_file_checksum(path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()

    @staticmethod
    async def run_excel_sync(db):
        print("<-- Excel Background Sync Started -->")

        result = await db.execute(select(ExcelFile))
        files = result.scalars().all()

        for file in files:
            if not os.path.exists(file.file_path):
                print(f">< File missing: {file.file_path}")
                continue

            last_modified = datetime.fromtimestamp(os.path.getmtime(file.file_path))
            checksum = ExcelBackgroundRunner.get_file_checksum(file.file_path)

            # Skip if no change
            if file.last_modified == last_modified and file.checksum == checksum:
                continue

            print(f"::: Processing File: {file.file_path}")

            # Update file metadata
            await db.execute(
                update(ExcelFile)
                .where(ExcelFile.id == file.id)
                .values(last_modified=last_modified, checksum=checksum)
            )

            # Read Excel
            xls = pd.ExcelFile(file.file_path)

            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)

                # Insert Sheet Record
                sheet = ExcelSheet(
                    excel_file_id=file.id,
                    sheet_name=sheet_name,
                    row_count=len(df),
                    last_processed_at=datetime.utcnow()
                )
                db.add(sheet)
                await db.flush()  # Get sheet.id

                # Insert Rows JSON
                for idx, row in df.iterrows():
                    row_json = row.to_dict()
                    row_hash = hashlib.sha256(str(row_json).encode()).hexdigest()

                    db.add(ExcelRowRaw(
                        sheet_id=sheet.id,
                        row_index=idx,
                        row_data=row_json,
                        row_hash=row_hash
                    ))

            await db.commit()
            print(f".... File Synced: {file.file_path}")
