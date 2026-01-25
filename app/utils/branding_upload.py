import aiofiles
import magic
import uuid
import os

from fastapi import UploadFile, HTTPException
from pathlib import Path

from app.core.config import settings


UPLOAD_DIR = Path(settings.BRANDING_UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE

ALLOWED_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


#  Validate logo (single read)
async def validate_branding_image(file: UploadFile):

    content = await file.read()

    mime = magic.from_buffer(content, mime=True)

    if mime not in ALLOWED_MIME:
        raise HTTPException(400, "Invalid image type")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")

    await file.seek(0)


#  Save logo
async def save_branding_image(file: UploadFile):

    ext = os.path.splitext(file.filename)[1].lower()

    filename = f"branding_{uuid.uuid4().hex}{ext}"

    path = UPLOAD_DIR / filename

    async with aiofiles.open(path, "wb") as f:
        while chunk := await file.read(1024):
            await f.write(chunk)

    return filename


#  Delete old logo
def delete_old_branding(filename: str | None):

    if not filename:
        return

    path = UPLOAD_DIR / filename

    if path.exists():
        path.unlink()


#  Build public URL
def build_branding_url(filename: str | None):

    if not filename:
        return None

    return f"{settings.BACKEND_URL}/branding/{filename}"
