from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.models.source import Source, SourceStatus
from app.models.tender import Tender
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.source_schema import (
    SourceCreate, SourceUpdate, SourceResponse, SourceList, SourceStats
)
from cryptography.fernet import Fernet
from app.core.config import settings

router = APIRouter()


# Encryption for passwords
def get_cipher():
    key = settings.SECRET_KEY[:32].encode().ljust(32, b'0')
    from base64 import urlsafe_b64encode
    return Fernet(urlsafe_b64encode(key))


def encrypt_password(password: str) -> str:
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()


@router.get("/", response_model=SourceList)
async def get_sources(
        search: Optional[str] = Query(None),
        status: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = db.query(Source)

    if search:
        query = query.filter(Source.name.ilike(f"%{search}%"))

    if status:
        query = query.filter(Source.status == status)

    sources = query.order_by(Source.name).all()

    # Calculate stats
    total = len(sources)
    active = sum(1 for s in sources if s.is_active and s.status == SourceStatus.ACTIVE)
    disabled = sum(1 for s in sources if not s.is_active or s.status == SourceStatus.DISABLED)
    errors = sum(1 for s in sources if s.status == SourceStatus.ERROR)

    return {
        "total": total,
        "active": active,
        "disabled": disabled,
        "errors": errors,
        "items": sources
    }


@router.get("/stats", response_model=SourceStats)
async def get_source_stats(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    total = db.query(func.count(Source.id)).scalar()
    active = db.query(func.count(Source.id)).filter(
        Source.is_active == True,
        Source.status == SourceStatus.ACTIVE
    ).scalar()
    disabled = db.query(func.count(Source.id)).filter(
        Source.is_active == False
    ).scalar()
    errors = db.query(func.count(Source.id)).filter(
        Source.status == SourceStatus.ERROR
    ).scalar()

    return {
        "total_sources": total,
        "active_sources": active,
        "disabled_sources": disabled,
        "error_sources": errors
    }


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
        source_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )

    return source


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
        source_data: SourceCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Check if source with same URL exists
    existing = db.query(Source).filter(Source.url == source_data.url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source with this URL already exists"
        )

    # Create source
    source_dict = source_data.dict(exclude={'password'})

    # Encrypt password if provided
    if source_data.password:
        source_dict['encrypted_password'] = encrypt_password(source_data.password)

    source = Source(**source_dict)
    db.add(source)
    db.commit()
    db.refresh(source)

    return source


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(
        source_id: int,
        source_update: SourceUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )

    update_data = source_update.dict(exclude_unset=True, exclude={'password'})

    # Handle password update
    if source_update.password:
        update_data['encrypted_password'] = encrypt_password(source_update.password)

    for field, value in update_data.items():
        setattr(source, field, value)

    db.commit()
    db.refresh(source)

    return source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
        source_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )

    # Check if source has tenders
    tender_count = db.query(func.count(Tender.id)).filter(
        Tender.source_id == source_id
    ).scalar()

    if tender_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete source with {tender_count} associated tenders"
        )

    db.delete(source)
    db.commit()

    return None


@router.post("/{source_id}/toggle", response_model=SourceResponse)
async def toggle_source(
        source_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )

    source.is_active = not source.is_active
    if source.is_active:
        source.status = SourceStatus.ACTIVE
    else:
        source.status = SourceStatus.DISABLED

    db.commit()
    db.refresh(source)

    return source