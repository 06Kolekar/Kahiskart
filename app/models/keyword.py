from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    BigInteger,
    Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


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


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(BigInteger, primary_key=True, index=True)
    keyword = Column(String(255), nullable=False, index=True)

    category = Column(
        Enum(KeywordCategory, name="keywordcategory"),
        default=KeywordCategory.OTHER,
        nullable=False,
        index=True
    )

    priority = Column(
        Enum(KeywordPriority, name="keywordpriority"),
        default=KeywordPriority.MEDIUM,
        nullable=False,
        index=True
    )

    is_case_sensitive = Column(Boolean, default=False, nullable=False)
    match_whole_word = Column(Boolean, default=False, nullable=False)

    enable_alerts = Column(Boolean, default=True, nullable=False)

    match_count = Column(Integer, default=0, nullable=False)
    last_match_date = Column(DateTime)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    tender_matches = relationship(
        "TenderKeywordMatch",
        back_populates="keyword",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_keyword_category_priority", "category", "priority"),
    )

    def __repr__(self):
        return f"<Keyword id={self.id} keyword='{self.keyword}'>"
