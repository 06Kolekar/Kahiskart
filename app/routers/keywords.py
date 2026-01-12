from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.keyword import Keyword
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.keyword_schema import (
    KeywordCreate, KeywordUpdate, KeywordResponse, KeywordList
)

router = APIRouter()


@router.get("/", response_model=KeywordList)
async def get_keywords(
        search: Optional[str] = Query(None),
        category: Optional[str] = Query(None),
        priority: Optional[str] = Query(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = db.query(Keyword).filter(Keyword.is_active == True)

    if search:
        query = query.filter(Keyword.keyword.ilike(f"%{search}%"))

    if category:
        query = query.filter(Keyword.category == category)

    if priority:
        query = query.filter(Keyword.priority == priority)

    keywords = query.order_by(Keyword.created_at.desc()).all()

    return {
        "total": len(keywords),
        "items": keywords
    }


@router.get("/{keyword_id}", response_model=KeywordResponse)
async def get_keyword(
        keyword_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    return keyword


@router.post("/", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
async def create_keyword(
        keyword_data: KeywordCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Check if keyword already exists
    existing = db.query(Keyword).filter(
        Keyword.keyword.ilike(keyword_data.keyword)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword already exists"
        )

    keyword = Keyword(**keyword_data.dict())
    db.add(keyword)
    db.commit()
    db.refresh(keyword)

    return keyword


@router.patch("/{keyword_id}", response_model=KeywordResponse)
async def update_keyword(
        keyword_id: int,
        keyword_update: KeywordUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    for field, value in keyword_update.dict(exclude_unset=True).items():
        setattr(keyword, field, value)

    db.commit()
    db.refresh(keyword)

    return keyword


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
        keyword_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    keyword = db.query(Keyword).filter(Keyword.id == keyword_id).first()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )

    # Soft delete
    keyword.is_active = False
    db.commit()

    return None


@router.get("/stats/top")
async def get_top_keywords(
        limit: int = Query(5, ge=1, le=20),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    keywords = db.query(Keyword).filter(
        Keyword.is_active == True
    ).order_by(Keyword.match_count.desc()).limit(limit).all()

    return [
        {
            "keyword": k.keyword,
            "matches": k.match_count,
            "priority": k.priority
        }
        for k in keywords
    ]