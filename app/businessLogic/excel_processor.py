# import logging
# from typing import Dict, List, Optional, Any
# from datetime import datetime
# import pandas as pd
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.onedrive import (
#     ExcelFileTracker, RawExcelSheet, FileStatus, SheetHeaderMapping
# )
# from app.businessLogic.onedrive_service import OneDriveService

# logger = logging.getLogger(__name__)

# class ExcelProcessor:
#     """Process Excel files and store data in database (async version)"""
    
#     def __init__(self, db: AsyncSession):
#         self.db = db
#         self.onedrive_service = OneDriveService()
    
#     async def process_onedrive_file(self, share_link: str, force_refresh: bool = False) -> Optional[ExcelFileTracker]:
#         """
#         Main method to download and process OneDrive Excel file
        
#         Args:
#             share_link: OneDrive share link
#             force_refresh: Force reprocessing even if file hasn't changed
            
#         Returns:
#             ExcelFileTracker object or None
#         """
#         file_tracker = None
#         try:
#             # Download file
#             logger.info(f"Downloading Excel file from OneDrive...")
#             file_content = await self.onedrive_service.download_excel_file(share_link)
            
#             if not file_content:
#                 logger.error("Failed to download Excel file")
#                 return None
            
#             # Calculate hash
#             file_hash = self.onedrive_service.calculate_file_hash(file_content)
#             logger.info(f"File hash: {file_hash}")
            
#             # Check if file already processed
#             if not force_refresh:
#                 stmt = select(ExcelFileTracker).where(ExcelFileTracker.file_hash == file_hash)
#                 result = await self.db.execute(stmt)
#                 existing_file = result.scalars().first()
                
#                 if existing_file and existing_file.status == FileStatus.DONE:
#                     logger.info(f"File already processed (file_id: {existing_file.file_id})")
#                     return existing_file
            
#             # Read all sheets
#             sheets_data = await self.onedrive_service.read_excel_sheets(file_content)
            
#             if not sheets_data:
#                 logger.error("No sheets found in Excel file")
#                 return None
            
#             # Create file tracker record
#             file_tracker = ExcelFileTracker(
#                 file_name="OneDrive_Tenders_" + datetime.utcnow().strftime("%Y%m%d_%H%M%S"),
#                 sheet_count=len(sheets_data),
#                 status=FileStatus.PROCESSING,
#                 file_hash=file_hash,
#                 onedrive_file_id=share_link,
#                 last_modified=datetime.utcnow()
#             )
            
#             self.db.add(file_tracker)
#             await self.db.commit()
#             await self.db.refresh(file_tracker)
            
#             logger.info(f"Created file tracker record (file_id: {file_tracker.file_id})")
            
#             # Process each sheet
#             total_rows = 0
#             for sheet_name, df in sheets_data.items():
#                 try:
#                     rows_processed = await self._process_sheet(
#                         file_tracker.file_id,
#                         sheet_name,
#                         df
#                     )
#                     total_rows += rows_processed
#                     logger.info(f"Processed {rows_processed} rows from sheet '{sheet_name}'")
#                 except Exception as e:
#                     logger.error(f"Error processing sheet '{sheet_name}': {str(e)}", exc_info=True)
#                     continue
            
#             # Update file tracker
#             file_tracker.status = FileStatus.DONE
#             file_tracker.processed_at = datetime.utcnow()
#             file_tracker.total_rows = total_rows
#             await self.db.commit()
            
#             logger.info(f"Successfully processed {total_rows} total rows from {len(sheets_data)} sheets")
#             return file_tracker
            
#         except Exception as e:
#             logger.error(f"Error processing OneDrive file: {str(e)}", exc_info=True)
#             if file_tracker:
#                 file_tracker.status = FileStatus.FAILED
#                 file_tracker.error_message = str(e)
#                 await self.db.commit()
#             return None
    
#     async def _process_sheet(self, file_id: int, sheet_name: str, df: pd.DataFrame) -> int:
#         """Process individual sheet and store rows"""
#         if df.empty:
#             logger.warning(f"Sheet '{sheet_name}' is empty")
#             return 0
        
#         header_mapping = await self._get_or_create_header_mapping(sheet_name, df)
#         source_website = self._extract_source_from_sheet_name(sheet_name)
        
#         batch_size = 1000
#         rows_processed = 0
        
#         for i in range(0, len(df), batch_size):
#             batch_df = df.iloc[i:i+batch_size]
#             batch_records = []
            
#             for idx, row in batch_df.iterrows():
#                 try:
#                     row_dict = self._row_to_json(row, header_mapping)
#                     tender_id = self._extract_tender_id(row_dict)
                    
#                     raw_sheet = RawExcelSheet(
#                         file_id=file_id,
#                         sheet_name=sheet_name,
#                         row_number=idx + 1,
#                         row_json=row_dict,
#                         source_website=source_website,
#                         tender_id=tender_id
#                     )
#                     batch_records.append(raw_sheet)
#                 except Exception as e:
#                     logger.error(f"Error processing row {idx} in sheet '{sheet_name}': {str(e)}")
#                     continue
            
#             if batch_records:
#                 for obj in batch_records:
#                     self.db.add(obj)
#                 await self.db.commit()
#                 rows_processed += len(batch_records)
        
#         return rows_processed
    
#     async def _get_or_create_header_mapping(self, sheet_name: str, df: pd.DataFrame) -> Dict[str, str]:
#         """Get existing header mapping or create new one"""
#         stmt = select(SheetHeaderMapping).where(SheetHeaderMapping.sheet_name == sheet_name)
#         result = await self.db.execute(stmt)
#         mapping = result.scalars().first()
        
#         if mapping:
#             return mapping.header_mapping
        
#         detected_mapping = self.onedrive_service.detect_tender_fields(df)
        
#         new_mapping = SheetHeaderMapping(
#             sheet_name=sheet_name,
#             source_website=self._extract_source_from_sheet_name(sheet_name),
#             header_mapping=detected_mapping
#         )
        
#         self.db.add(new_mapping)
#         await self.db.commit()
        
#         return detected_mapping
    
#     def _row_to_json(self, row: pd.Series, header_mapping: Dict[str, str]) -> Dict[str, Any]:
#         """Convert pandas row to JSON"""
#         row_dict = {}
#         for col, value in row.items():
#             if pd.isna(value):
#                 row_dict[col] = None
#             elif isinstance(value, (pd.Timestamp, datetime)):
#                 row_dict[col] = value.isoformat()
#             elif isinstance(value, (int, float)):
#                 row_dict[col] = float(value) if isinstance(value, float) else int(value)
#             else:
#                 row_dict[col] = str(value)
        
#         if header_mapping:
#             for field, original_col in header_mapping.items():
#                 if original_col in row_dict:
#                     row_dict[f"normalized_{field}"] = row_dict[original_col]
        
#         return row_dict
    
#     def _extract_source_from_sheet_name(self, sheet_name: str) -> Optional[str]:
#         sheet_lower = sheet_name.lower()
#         patterns = {
#             'gem': 'GeM Portal',
#             'eprocure': 'eProcurement',
#             'cppp': 'CPPP Portal',
#             'etender': 'eTender',
#             'ireps': 'IREPS',
#             'sam': 'SAM.gov',
#             'ted': 'TED Europa',
#         }
#         for key, val in patterns.items():
#             if key in sheet_lower:
#                 return val
#         return sheet_name
    
#     def _extract_tender_id(self, row_dict: Dict[str, Any]) -> Optional[str]:
#         if 'normalized_tender_id' in row_dict and row_dict['normalized_tender_id']:
#             return str(row_dict['normalized_tender_id'])
#         possible_fields = ['tender_id', 'tender_no', 'reference_no', 'ref_no', 'id']
#         for field in possible_fields:
#             for key, value in row_dict.items():
#                 if field in key.lower() and value:
#                     return str(value)
#         return None
    
#     async def get_latest_file_info(self) -> Optional[ExcelFileTracker]:
#         stmt = select(ExcelFileTracker).order_by(ExcelFileTracker.uploaded_at.desc())
#         result = await self.db.execute(stmt)
#         return result.scalars().first()
    
#     async def get_sheet_data(
#         self, 
#         file_id: Optional[int] = None,
#         sheet_name: Optional[str] = None,
#         limit: int = 100,
#         offset: int = 0
#     ) -> List[RawExcelSheet]:
#         """Get sheet data with optional filtering"""
#         stmt = select(RawExcelSheet)
#         if file_id:
#             stmt = stmt.where(RawExcelSheet.file_id == file_id)
#         if sheet_name:
#             stmt = stmt.where(RawExcelSheet.sheet_name == sheet_name)
#         stmt = stmt.offset(offset).limit(limit)
#         result = await self.db.execute(stmt)
#         return result.scalars().all()


# import logging
# from typing import Dict, List, Optional, Any
# from datetime import datetime

# import pandas as pd
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.onedrive import (
#     ExcelFileTracker,
#     RawExcelSheet,
#     FileStatus,
#     SheetHeaderMapping
# )
# from app.businessLogic.onedrive_service import OneDriveService

# logger = logging.getLogger(__name__)
# # logger = logging.getLogger(__name__)


# class ExcelProcessor:
#     """Process Excel files and store data in database (async DB, sync pandas/I/O)"""

#     def __init__(self, db: AsyncSession):
#         self.db = db
#         self.onedrive_service = OneDriveService()

#     async def process_onedrive_file(
#         self,
#         share_link: str,
#         force_refresh: bool = False
#     ) -> Optional[ExcelFileTracker]:

#         file_tracker: Optional[ExcelFileTracker] = None

#         try:
#             logger.info("Downloading Excel file from OneDrive")

#             # ❌ was awaited earlier (BUG)
#             file_content = self.onedrive_service.download_excel_file(share_link)

#             if not file_content:
#                 logger.error("Excel download failed")
#                 return None

#             file_hash = self.onedrive_service.calculate_file_hash(file_content)

#             if not force_refresh:
#                 stmt = select(ExcelFileTracker).where(
#                     ExcelFileTracker.file_hash == file_hash,
#                     ExcelFileTracker.status == FileStatus.DONE
#                 )
#                 res = await self.db.execute(stmt)
#                 existing = res.scalars().first()
#                 if existing:
#                     logger.info(f"File already processed: {existing.file_id}")
#                     return existing

#             # ❌ was awaited earlier (BUG)
#             sheets_data = self.onedrive_service.read_excel_sheets(file_content)

#             if not sheets_data:
#                 logger.warning("No sheets found in Excel")
#                 return None

#             file_tracker = ExcelFileTracker(
#                 file_name=f"OneDrive_Tenders_{datetime.utcnow():%Y%m%d_%H%M%S}",
#                 sheet_count=len(sheets_data),
#                 status=FileStatus.PROCESSING,
#                 file_hash=file_hash,
#                 onedrive_file_id=share_link,
#                 last_modified=datetime.utcnow()
#             )

#             self.db.add(file_tracker)
#             await self.db.commit()
#             await self.db.refresh(file_tracker)

#             total_rows = 0

#             for sheet_name, df in sheets_data.items():
#                 try:
#                     rows = await self._process_sheet(
#                         file_tracker.file_id,
#                         sheet_name,
#                         df
#                     )
#                     total_rows += rows
#                 except Exception:
#                     logger.exception(f"Sheet failed: {sheet_name}")

#             file_tracker.status = FileStatus.DONE
#             file_tracker.processed_at = datetime.utcnow()
#             file_tracker.total_rows = total_rows

#             await self.db.commit()

#             logger.info(
#                 f"Processing complete | sheets={len(sheets_data)} rows={total_rows}"
#             )

#             return file_tracker

#         except Exception as e:
#             logger.exception("Excel processing failed")
#             if file_tracker:
#                 file_tracker.status = FileStatus.FAILED
#                 file_tracker.error_message = str(e)
#                 await self.db.commit()
#             return None

#     async def _process_sheet(
#         self,
#         file_id: int,
#         sheet_name: str,
#         df: pd.DataFrame
#     ) -> int:

#         if df.empty:
#             logger.warning(f"Empty sheet: {sheet_name}")
#             return 0

#         # ✅ normalize headers
#         df = self.onedrive_service.normalize_column_names(df)

#         header_mapping = await self._get_or_create_header_mapping(sheet_name, df)
#         source_website = self._extract_source_from_sheet_name(sheet_name)

#         batch_size = 1000
#         rows_processed = 0

#         for start in range(0, len(df), batch_size):
#             batch_df = df.iloc[start:start + batch_size]
#             records: List[RawExcelSheet] = []

#             for idx, row in batch_df.iterrows():
#                 row_json = self._row_to_json(row, header_mapping)
#                 tender_id = self._extract_tender_id(row_json)

#                 records.append(
#                     RawExcelSheet(
#                         file_id=file_id,
#                         sheet_name=sheet_name,
#                         row_number=idx + 1,
#                         row_json=row_json,
#                         source_website=source_website,
#                         tender_id=tender_id
#                     )
#                 )

#             self.db.add_all(records)
#             await self.db.commit()

#             rows_processed += len(records)

#         return rows_processed

#     async def _get_or_create_header_mapping(
#         self,
#         sheet_name: str,
#         df: pd.DataFrame
#     ) -> Dict[str, str]:

#         stmt = select(SheetHeaderMapping).where(
#             SheetHeaderMapping.sheet_name == sheet_name
#         )
#         res = await self.db.execute(stmt)
#         mapping = res.scalars().first()

#         if mapping:
#             return mapping.header_mapping

#         detected = self.onedrive_service.detect_tender_fields(df)

#         # ✅ fallback mapping
#         if not detected:
#             detected = {col: col for col in df.columns}

#         new_mapping = SheetHeaderMapping(
#             sheet_name=sheet_name,
#             source_website=self._extract_source_from_sheet_name(sheet_name),
#             header_mapping=detected
#         )

#         self.db.add(new_mapping)
#         await self.db.commit()

#         return detected

#     def _row_to_json(
#         self,
#         row: pd.Series,
#         header_mapping: Dict[str, str]
#     ) -> Dict[str, Any]:

#         data: Dict[str, Any] = {}

#         for col, val in row.items():
#             if pd.isna(val):
#                 data[col] = None
#             elif isinstance(val, (pd.Timestamp, datetime)):
#                 data[col] = val.isoformat()
#             else:
#                 data[col] = str(val)

#         for norm_field, original_col in header_mapping.items():
#             if original_col in data:
#                 data[f"normalized_{norm_field}"] = data[original_col]

#         return data

#     def _extract_source_from_sheet_name(self, sheet_name: str) -> Optional[str]:
#         name = sheet_name.lower()
#         sources = {
#             "gem": "GeM Portal",
#             "sam": "SAM.gov",
#             "ireps": "IREPS",
#             "eprocure": "eProcurement",
#             "cppp": "CPPP Portal",
#             "ted": "TED Europa",
#         }
#         for key, val in sources.items():
#             if key in name:
#                 return val
#         return sheet_name

#     def _extract_tender_id(self, row: Dict[str, Any]) -> Optional[str]:
#         if row.get("normalized_tender_id"):
#             return str(row["normalized_tender_id"])

#         for k, v in row.items():
#             if v and any(x in k.lower() for x in ["tender", "ref", "id"]):
#                 return str(v)
#         return None

#     async def get_latest_file_info(self) -> Optional[ExcelFileTracker]:
#         stmt = select(ExcelFileTracker).order_by(
#             ExcelFileTracker.uploaded_at.desc()
#         )
#         res = await self.db.execute(stmt)
#         return res.scalars().first()

#     async def get_sheet_data(
#         self,
#         file_id: Optional[int] = None,
#         sheet_name: Optional[str] = None,
#         limit: int = 100,
#         offset: int = 0
#     ) -> List[RawExcelSheet]:

#         stmt = select(RawExcelSheet)

#         if file_id:
#             stmt = stmt.where(RawExcelSheet.file_id == file_id)
#         if sheet_name:
#             stmt = stmt.where(RawExcelSheet.sheet_name == sheet_name)

#         stmt = stmt.offset(offset).limit(limit)
#         res = await self.db.execute(stmt)
#         return res.scalars().all()

# import logging
# from pathlib import Path
# from typing import Dict
# from datetime import datetime

# import pandas as pd
# from sqlalchemy.ext.asyncio import AsyncSession

# from app.models.onedrive import (
#     ExcelFileTracker,
#     RawExcelSheet,
#     FileStatus
# )

# logger = logging.getLogger(__name__)


# class ExcelProcessor:

#     def __init__(self, db: AsyncSession):
#         self.db = db

#     async def process_local_excel(self, file_path: str):
#         logger.info(f"Reading Excel from: {file_path}")

#         if not Path(file_path).exists():
#             logger.error("Excel file not found")
#             return

#         excel = pd.ExcelFile(file_path, engine="openpyxl")

#         tracker = ExcelFileTracker(
#             file_name=Path(file_path).name,
#             sheet_count=len(excel.sheet_names),
#             status=FileStatus.PROCESSING,
#             uploaded_at=datetime.utcnow()
#         )

#         self.db.add(tracker)
#         await self.db.commit()
#         await self.db.refresh(tracker)

#         total_rows = 0

#         for sheet_name in excel.sheet_names:
#             logger.info(f"Processing sheet: {sheet_name}")

#             df = pd.read_excel(excel, sheet_name=sheet_name)
#             df.dropna(how="all", inplace=True)

#             rows = await self._insert_sheet_rows(
#                 tracker.file_id, sheet_name, df
#             )
#             total_rows += rows

#         tracker.status = FileStatus.DONE
#         tracker.total_rows = total_rows
#         tracker.processed_at = datetime.utcnow()

#         await self.db.commit()

#         logger.info(
#             f"Excel processed | Sheets={tracker.sheet_count}, Rows={total_rows}"
#         )

#     async def _insert_sheet_rows(
#         self,
#         file_id: int,
#         sheet_name: str,
#         df: pd.DataFrame
#     ) -> int:

#         count = 0

#         for idx, row in df.iterrows():
#             record = RawExcelSheet(
#                 file_id=file_id,
#                 sheet_name=sheet_name,
#                 row_number=idx + 1,
#                 row_json=row.to_dict()
#             )
#             self.db.add(record)
#             count += 1

#         await self.db.commit()
#         return count

# app/businessLogic/excel_processor.py

import logging
from datetime import datetime
from io import BytesIO

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.onedrive import (
    ExcelFileTracker,
    RawExcelSheet,
    FileStatus,
)

logger = logging.getLogger(__name__)


class ExcelProcessor:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_excel(
        self,
        file_content: BytesIO,
        file_name: str,
        file_hash: str,
        etag: str | None,
        last_modified: str | None,
    ):
        # -------------------------------------------------
        # SKIP IF FILE ALREADY PROCESSED
        # -------------------------------------------------
        result = await self.db.execute(
            select(ExcelFileTracker)
            .where(ExcelFileTracker.file_hash == file_hash)
            .limit(1)
        )

        if result.scalar():
            logger.info("Excel unchanged — skipping ingestion")
            return

        tracker = ExcelFileTracker(
            file_name=file_name,
            status=FileStatus.PROCESSING,
            uploaded_at=datetime.utcnow(),
            file_hash=file_hash,
            onedrive_etag=etag,
            last_modified=last_modified,
        )

        self.db.add(tracker)
        await self.db.commit()
        await self.db.refresh(tracker)

        try:
            excel = pd.ExcelFile(file_content, engine="openpyxl")
            tracker.sheet_count = len(excel.sheet_names)

            total_rows = 0

            for sheet_name in excel.sheet_names:
                logger.info(f"Processing sheet: {sheet_name}")

                df = pd.read_excel(excel, sheet_name=sheet_name)
                df.dropna(how="all", inplace=True)

                rows = await self._insert_rows(
                    tracker.file_id, sheet_name, df
                )
                total_rows += rows

            tracker.status = FileStatus.DONE
            tracker.total_rows = total_rows
            tracker.processed_at = datetime.utcnow()

            await self.db.commit()

            logger.info(
                f"Excel processed | File={file_name} Sheets={tracker.sheet_count} Rows={total_rows}"
            )

        except Exception as exc:
            tracker.status = FileStatus.FAILED
            tracker.error_message = str(exc)
            await self.db.commit()
            raise

    async def _insert_rows(
        self,
        file_id: int,
        sheet_name: str,
        df: pd.DataFrame,
    ) -> int:
        records = []

        for idx, row in df.iterrows():
            records.append(
                RawExcelSheet(
                    file_id=file_id,
                    sheet_name=sheet_name,
                    row_number=idx + 1,
                    row_json=row.to_dict(),
                )
            )

        self.db.add_all(records)
        await self.db.commit()

        return len(records)
