from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class KeywordPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class KeywordCategory(str, Enum):
    INFORMATION_TECHNOLOGY = "Information Technology"
    CONSTRUCTION = "Construction"
    HEALTHCARE = "Healthcare"
    ENVIRONMENTAL = "Environmental"
    SERVICES = "Services"
    OTHER = "Other"


class KeywordBase(BaseModel):
    keyword: str = Field(..., min_length=2, max_length=255)
    category: KeywordCategory = KeywordCategory.OTHER
    priority: KeywordPriority = KeywordPriority.MEDIUM
    enable_alerts: bool = True


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    keyword: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[KeywordCategory] = None
    priority: Optional[KeywordPriority] = None
    enable_alerts: Optional[bool] = None
    is_active: Optional[bool] = None


class KeywordResponse(KeywordBase):
    id: int
    match_count: int = 0
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KeywordList(BaseModel):
    total: int
    items: List[KeywordResponse]