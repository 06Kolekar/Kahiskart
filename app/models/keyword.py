from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


# ---------------------------
# ENUMS
# ---------------------------

class KeywordPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class KeywordCategory(str, enum.Enum):
    INFORMATION_TECHNOLOGY = "Information Technology"
    CONSTRUCTION = "Construction"
    HEALTHCARE = "Healthcare"
    ENVIRONMENTAL = "Environmental"
    SERVICES = "Services"
    OTHER = "Other"


# ---------------------------
# KEYWORD MODEL
# ---------------------------

class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False, index=True)

    category = Column(
        Enum(KeywordCategory),
        default=KeywordCategory.OTHER,
        index=True
    )

    priority = Column(
        Enum(KeywordPriority),
        default=KeywordPriority.MEDIUM,
        index=True
    )

    # Matching behavior
    is_case_sensitive = Column(Boolean, default=False)
    match_whole_word = Column(Boolean, default=False)

    # Notification settings
    enable_alerts = Column(Boolean, default=True)

    # Statistics
    match_count = Column(Integer, default=0)
    last_match_date = Column(DateTime)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    tender_matches = relationship(
        "TenderKeywordMatch",
        back_populates="keyword",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Keyword {self.keyword} ({self.category})>"


# ---------------------------
# TENDER ↔ KEYWORD MATCH TABLE
# ---------------------------

class TenderKeywordMatch(Base):
    __tablename__ = "tender_keyword_matches"

    id = Column(Integer, primary_key=True, index=True)

    tender_id = Column(
        Integer,
        ForeignKey("tenders.id", ondelete="CASCADE"),
        index=True
    )

    keyword_id = Column(
        Integer,
        ForeignKey("keywords.id", ondelete="CASCADE"),
        index=True
    )

    match_location = Column(String(50))  # title / description / document
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    keyword = relationship("Keyword", back_populates="tender_matches")
    tender = relationship("Tender", back_populates="keyword_matches")
