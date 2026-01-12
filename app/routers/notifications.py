from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.notification_schema import (
    NotificationResponse, NotificationList, NotificationSettings, NotificationSettingsUpdate
)

router = APIRouter()


@router.get("/", response_model=NotificationList)
async def get_notifications(
        is_read: Optional[bool] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(25, ge=1, le=100),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    offset = (page - 1) * page_size
    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "unread_count": unread_count,
        "items": notifications
    }


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
        notification_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    db.commit()
    db.refresh(notification)

    return notification


@router.post("/mark-all-read")
async def mark_all_read(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    updated = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})

    db.commit()

    return {
        "message": f"Marked {updated} notifications as read",
        "updated_count": updated
    }


@router.delete("/{notification_id}")
async def delete_notification(
        notification_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return {"message": "Notification deleted"}


@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # In a real app, this would be stored in a UserSettings table
    # For now, return default settings
    return NotificationSettings()


@router.patch("/settings", response_model=NotificationSettings)
async def update_notification_settings(
        settings_update: NotificationSettingsUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # TODO: Store in UserSettings table
    # For now, just return the updated settings
    return NotificationSettings(**settings_update.dict(exclude_unset=True))


@router.get("/count/unread")
async def get_unread_count(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    return {"unread_count": count}