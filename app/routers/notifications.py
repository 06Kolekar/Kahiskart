from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Base query
    stmt = select(Notification).where(
        Notification.user_id == current_user.id
    )

    # Filter read/unread
    if is_read is not None:
        stmt = stmt.where(Notification.is_read == is_read)

    # Total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    # Unread count
    unread_stmt = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )
    unread_result = await db.execute(unread_stmt)
    unread_count = unread_result.scalar()

    # Pagination
    offset = (page - 1) * page_size

    stmt = (
        stmt
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )

    # Fetch items
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    return {
        "total": total,
        "unread_count": unread_count,
        "items": notifications
    }


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )

    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.is_read = True
    await db.commit()
    await db.refresh(notification)

    return notification



@router.post("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )

    result = await db.execute(stmt)
    notifications = result.scalars().all()

    count = 0
    for n in notifications:
        n.is_read = True
        count += 1

    await db.commit()

    return {
        "message": f"Marked {count} notifications as read",
        "updated_count": count
    }



@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    )

    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    await db.delete(notification)
    await db.commit()

    return {"message": "Notification deleted"}



@router.get("/settings", response_model=NotificationSettings)
async def get_notification_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # In a real app, this would be stored in a UserSettings table
    # For now, return default settings
    return NotificationSettings()


@router.patch("/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings_update: NotificationSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TODO: Store in UserSettings table
    # For now, just return the updated settings
    return NotificationSettings(**settings_update.dict(exclude_unset=True))


@router.get("/count/unread")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(func.count()).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )

    result = await db.execute(stmt)
    count = result.scalar()

    return {"unread_count": count}
