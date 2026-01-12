from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, time
from enum import Enum


class NotificationType(str, Enum):
    NEW_TENDER = "new_tender"
    KEYWORD_MATCH = "keyword_match"
    DEADLINE_APPROACHING = "deadline_approaching"
    SYSTEM_ERROR = "system_error"


class NotificationChannel(str, Enum):
    EMAIL = "email"
    DESKTOP = "desktop"
    BOTH = "both"


class NotificationBase(BaseModel):
    type: NotificationType
    channel: NotificationChannel = NotificationChannel.BOTH
    title: str = Field(..., max_length=255)
    message: str


class NotificationCreate(NotificationBase):
    user_id: int
    tender_id: Optional[int] = None


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    tender_id: Optional[int] = None
    is_read: bool
    is_sent: bool
    email_sent: bool
    desktop_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    total: int
    unread_count: int
    items: List[NotificationResponse]


class NotificationSettings(BaseModel):
    enable_desktop: bool = True
    enable_email: bool = True
    email_recipients: List[EmailStr] = []

    # Alert Triggers
    new_tender_published: bool = True
    keyword_match_found: bool = True
    deadline_approaching: bool = True
    system_errors: bool = False

    # Silent Hours
    enable_silent_hours: bool = False
    silent_start_time: Optional[time] = None
    silent_end_time: Optional[time] = None


class NotificationSettingsUpdate(BaseModel):
    enable_desktop: Optional[bool] = None
    enable_email: Optional[bool] = None
    email_recipients: Optional[List[EmailStr]] = None
    new_tender_published: Optional[bool] = None
    keyword_match_found: Optional[bool] = None
    deadline_approaching: Optional[bool] = None
    system_errors: Optional[bool] = None
    enable_silent_hours: Optional[bool] = None
    silent_start_time: Optional[time] = None
    silent_end_time: Optional[time] = None