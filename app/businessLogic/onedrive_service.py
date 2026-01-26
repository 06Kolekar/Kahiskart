# import requests
# import hashlib
# import logging
# import base64
# from io import BytesIO
# from typing import Optional, Dict, Any
# from datetime import datetime

# import pandas as pd

# logger = logging.getLogger(__name__)


# class OneDriveService:
#     """
#     Service to download and process Excel files from OneDrive share links
#     """

#     def __init__(self):
#         self.session = requests.Session()
#         self.session.headers.update({
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#         })

#     # ------------------------------------------------------------------
#     # OneDrive URL handling
#     # ------------------------------------------------------------------

#     def _encode_share_url(self, url: str) -> str:
#         """
#         Microsoft-required base64 URL-safe encoding for OneDrive share links
#         """
#         encoded = base64.b64encode(url.encode()).decode()
#         return encoded.rstrip("=").replace("/", "_").replace("+", "-")

#     def convert_share_link_to_download_url(self, share_link: str) -> str:
#         """
#         Convert OneDrive share link to direct download URL
#         """
#         encoded = self._encode_share_url(share_link)
#         return f"https://api.onedrive.com/v1.0/shares/u!{encoded}/root/content"

#     # ------------------------------------------------------------------
#     # Download & file utilities
#     # ------------------------------------------------------------------

#     def download_excel_file(self, share_link: str) -> Optional[BytesIO]:
#         """
#         Download Excel file from OneDrive share link
#         """
#         try:
#             download_url = self.convert_share_link_to_download_url(share_link)
#             logger.info(f"Downloading Excel from OneDrive")

#             response = self.session.get(
#                 download_url,
#                 timeout=60,
#                 allow_redirects=True
#             )

#             if response.status_code != 200:
#                 logger.error(
#                     f"Download failed [{response.status_code}] "
#                     f"{response.text[:300]}"
#                 )
#                 return None

#             logger.info(f"Excel downloaded ({len(response.content)} bytes)")
#             return BytesIO(response.content)

#         except Exception as e:
#             logger.exception("Error downloading Excel file")
#             return None

#     def calculate_file_hash(self, file_content: BytesIO) -> str:
#         """
#         Calculate MD5 hash for change detection
#         """
#         file_content.seek(0)
#         file_hash = hashlib.md5(file_content.read()).hexdigest()
#         file_content.seek(0)
#         return file_hash

#     # ------------------------------------------------------------------
#     # Excel handling
#     # ------------------------------------------------------------------

#     def normalize_sheet_name(self, sheet_name: str) -> str:
#         """
#         Normalize Excel sheet names for DB / API consistency
#         """
#         return (
#             sheet_name.strip()
#             .lower()
#             .replace(" ", "_")
#             .replace("-", "_")
#         )

#     def read_excel_sheets(self, file_content: BytesIO) -> Dict[str, pd.DataFrame]:
#         """
#         Read all sheets from Excel file safely
#         """
#         try:
#             file_content.seek(0)
#             excel = pd.ExcelFile(file_content, engine="openpyxl")

#             sheets: Dict[str, pd.DataFrame] = {}

#             for original_name in excel.sheet_names:
#                 try:
#                     normalized_name = self.normalize_sheet_name(original_name)

#                     df = pd.read_excel(
#                         excel,
#                         sheet_name=original_name,
#                         header=0
#                     )

#                     # Remove completely empty rows
#                     df.dropna(how="all", inplace=True)

#                     sheets[normalized_name] = df

#                     logger.info(
#                         f"Sheet '{original_name}' → '{normalized_name}' "
#                         f"({len(df)} rows, {len(df.columns)} cols)"
#                     )

#                 except Exception:
#                     logger.exception(f"Failed reading sheet: {original_name}")

#             return sheets

#         except Exception:
#             logger.exception("Error reading Excel file")
#             return {}

#     # ------------------------------------------------------------------
#     # Column normalization & mapping
#     # ------------------------------------------------------------------

#     def normalize_column_names(self, df: pd.DataFrame) -> Dict[str, str]:
#         """
#         Normalize column names and return mapping:
#         normalized_name -> original_name
#         """
#         mapping: Dict[str, str] = {}
#         new_columns = []

#         for col in df.columns:
#             normalized = (
#                 str(col).strip().lower()
#                 .replace(" ", "_")
#                 .replace("-", "_")
#                 .replace("/", "_")
#                 .replace("(", "")
#                 .replace(")", "")
#             )

#             mapping[normalized] = col
#             new_columns.append(normalized)

#         df.columns = new_columns
#         return mapping

#     def detect_tender_fields(self, df: pd.DataFrame) -> Dict[str, str]:
#         """
#         Detect common tender fields across varying Excel formats
#         Returns: canonical_field -> normalized_column
#         """
#         patterns = {
#             "tender_id": ["tender_no", "tender_id", "reference", "ref_no", "id"],
#             "title": ["title", "description", "subject"],
#             "organization": ["organization", "department", "buyer", "agency"],
#             "deadline": ["deadline", "due_date", "closing_date"],
#             "publish_date": ["publish_date", "posted_date"],
#             "value": ["value", "amount", "estimated_value"],
#             "status": ["status"],
#             "category": ["category", "type"],
#             "location": ["location", "city", "state"],
#         }

#         detected: Dict[str, str] = {}
#         cols = list(df.columns)

#         for field, keys in patterns.items():
#             for key in keys:
#                 match = next((c for c in cols if key in c), None)
#                 if match:
#                     detected[field] = match
#                     break

#         return detected

#     # ------------------------------------------------------------------
#     # Metadata
#     # ------------------------------------------------------------------

#     def get_file_metadata(self, share_link: str) -> Dict[str, Any]:
#         """
#         Lightweight metadata (Graph API not used)
#         """
#         return {
#             "share_link": share_link,
#             "checked_at": datetime.utcnow().isoformat()
#         }

# import requests
# import base64
# import hashlib
# import logging
# from io import BytesIO
# from typing import Dict, Optional

# import pandas as pd

# logger = logging.getLogger("onedrive")
# logger.setLevel(logging.INFO)

# logger = logging.getLogger("onedrive")


# class OneDriveService:
#     """
#     Responsible ONLY for:
#     1. Downloading Excel from OneDrive
#     2. Reading Excel sheets into DataFrames
#     """

#     def __init__(self):
#         self.session = requests.Session()
#         self.session.headers.update({
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#         })

#     # ---------------------------------------------------
#     # OneDrive URL handling
#     # ---------------------------------------------------

#     def _encode_share_url(self, share_link: str) -> str:
#         encoded = base64.b64encode(share_link.encode()).decode()
#         encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
#         return encoded

#     def build_download_url(self, share_link: str) -> str:
#         download_url = (
#             f"https://api.onedrive.com/v1.0/shares/u!"
#             f"{self._encode_share_url(share_link)}/root/content"
#         )
#         logger.info(f"[OneDrive] Download URL built")
#         return download_url

#     # ---------------------------------------------------
#     # DOWNLOAD
#     # ---------------------------------------------------

#     def download_excel_file(self, share_link: str) -> Optional[BytesIO]:
#         logger.info("[OneDrive] Starting Excel download")

#         try:
#             url = self.build_download_url(share_link)

#             response = self.session.get(
#                 url,
#                 timeout=60,
#                 allow_redirects=True
#             )

#             logger.info(
#                 f"[OneDrive] HTTP {response.status_code} | "
#                 f"Content-Length={len(response.content)}"
#             )

#             if response.status_code != 200:
#                 logger.error(
#                     f"[OneDrive] Download failed: "
#                     f"{response.text[:300]}"
#                 )
#                 return None

#             logger.info("[OneDrive] Excel download SUCCESS")
#             return BytesIO(response.content)

#         except Exception:
#             logger.exception("[OneDrive] Download exception")
#             return None

#     # ---------------------------------------------------
#     # EXCEL READ
#     # ---------------------------------------------------

#     def read_excel_sheets(self, file_content: BytesIO) -> Dict[str, pd.DataFrame]:
#         logger.info("[Excel] Reading Excel sheets")

#         try:
#             file_content.seek(0)
#             excel = pd.ExcelFile(file_content, engine="openpyxl")

#             sheets: Dict[str, pd.DataFrame] = {}

#             for name in excel.sheet_names:
#                 logger.info(f"[Excel] Reading sheet: {name}")

#                 df = pd.read_excel(excel, sheet_name=name)
#                 df.dropna(how="all", inplace=True)

#                 logger.info(
#                     f"[Excel] Sheet '{name}' → "
#                     f"{len(df)} rows, {len(df.columns)} columns"
#                 )

#                 sheets[name] = df

#             logger.info(
#                 f"[Excel] Total sheets read: {len(sheets)}"
#             )
#             return sheets

#         except Exception:
#             logger.exception("[Excel] Failed reading Excel")
#             return {}

#     # ---------------------------------------------------
#     # HASH (used by processor)
#     # ---------------------------------------------------
    
#     def calculate_file_hash(self, file_content: BytesIO) -> str:
#         file_content.seek(0)
#         file_hash = hashlib.md5(file_content.read()).hexdigest()
#         file_content.seek(0)
#         logger.info(f"[Excel] File hash: {file_hash}")
#         return file_hash

# import requests
# import logging
# from io import BytesIO
# import base64

# logger = logging.getLogger("onedrive")

# class OneDriveService:
#     """Download Excel from OneDrive share link"""

#     def __init__(self):
#         self.session = requests.Session()
#         self.session.headers.update({
#             "User-Agent": "Mozilla/5.0"
#         })

#     def _encode_share_url(self, share_link: str) -> str:
#         encoded = base64.b64encode(share_link.encode()).decode()
#         encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
#         return encoded

#     def build_download_url(self, share_link: str) -> str:
#         return f"https://api.onedrive.com/v1.0/shares/u!{self._encode_share_url(share_link)}/root/content"

#     def download_excel_file(self, share_link: str) -> BytesIO | None:
#         try:
#             url = self.build_download_url(share_link)
#             response = self.session.get(url, timeout=60, allow_redirects=True)
#             if response.status_code != 200:
#                 logger.error(f"[OneDrive] Failed download: {response.status_code} {response.text}")
#                 return None
#             logger.info("[OneDrive] Download success")
#             return BytesIO(response.content)
#         except Exception as e:
#             logger.exception("[OneDrive] Exception during download")
#             return None

# app/businessLogic/onedrive_service.py

import base64
import hashlib
import logging
from io import BytesIO
from typing import Optional, Dict

import httpx

logger = logging.getLogger("onedrive")


class OneDriveService:

    def _encode_share_url(self, share_link: str) -> str:
        encoded = base64.b64encode(share_link.encode()).decode()
        return encoded.rstrip("=").replace("/", "_").replace("+", "-")

    def build_download_url(self, share_link: str) -> str:
        encoded = self._encode_share_url(share_link)
        # return f"https://api.onedrive.com/v1.0/shares/u!{encoded}/root/content"
        return f"https://api.onedrive.com/v1.0/shares/u!{encoded}/driveItem/content"

    async def download_excel(self, share_link: str) -> Optional[Dict]:
        url = self.build_download_url(share_link)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(url, follow_redirects=True)

        if response.status_code != 200:
            logger.error(f"[OneDrive] Download failed: {response.status_code}")
            return None

        content = response.content

        file_name = (
            response.headers.get("Content-Disposition", "onedrive.xlsx")
            .split("filename=")[-1]
            .strip('"')
        )

        return {
            "content": BytesIO(content),
            "file_name": file_name,
            "etag": response.headers.get("ETag"),
            "last_modified": response.headers.get("Last-Modified"),
            "file_hash": hashlib.sha256(content).hexdigest(),
        }
