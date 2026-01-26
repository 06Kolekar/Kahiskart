import requests
import base64
from io import BytesIO
import logging

logger = logging.getLogger("onedrive")

class OneDriveService:
    """
    Responsible for downloading Excel files from OneDrive
    """

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def _encode_share_url(self, share_link: str) -> str:
        encoded = base64.b64encode(share_link.encode()).decode()
        encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
        return encoded

    def build_download_url(self, share_link: str) -> str:
        return f"https://api.onedrive.com/v1.0/shares/u!{self._encode_share_url(share_link)}/root/content"

    def download_excel_file(self, share_link: str) -> BytesIO | None:
        logger.info("[OneDrive] Starting Excel download")
        url = self.build_download_url(share_link)
        response = self.session.get(url, timeout=60, allow_redirects=True)
        if response.status_code != 200:
            logger.error(f"[OneDrive] Download failed: {response.text[:300]}")
            return None
        return BytesIO(response.content)
