import aiofiles
import magic
import uuid
import os

from fastapi import UploadFile, HTTPException
from pathlib import Path

from app.core.config import settings


# Upload directory from .env
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = settings.MAX_UPLOAD_SIZE

ALLOWED_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


async def validate_image(file: UploadFile):

    # Read first bytes to detect type
    content = await file.read(1024)

    mime = magic.from_buffer(content, mime=True)

    await file.seek(0)

    if mime not in ALLOWED_MIME:
        raise HTTPException(400, "Invalid image type")

    # Check file size
    size = 0

    while chunk := await file.read(1024):
        size += len(chunk)

    await file.seek(0)

    if size > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large")


async def save_upload_file(file: UploadFile, user_id: int):

    ext = os.path.splitext(file.filename)[1].lower()

    filename = f"{user_id}_{uuid.uuid4().hex}{ext}"

    path = UPLOAD_DIR / filename

    async with aiofiles.open(path, "wb") as f:

        while chunk := await file.read(1024):
            await f.write(chunk)

    return filename


def delete_old_profile_picture(filename: str):

    if not filename:
        return

    path = UPLOAD_DIR / filename

    if path.exists():
        path.unlink()

def build_profile_url(filename: str | None):

    if not filename:
        return None

    return f"{settings.BACKEND_URL}/uploads/{filename}"