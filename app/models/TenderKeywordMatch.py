from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
    BigInteger,
    Index,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class MatchLocation(str, enum.Enum):
    TITLE = "title"
    DESCRIPTION = "description"
    DOCUMENT = "document"


class TenderKeywordMatch(Base):
    __tablename__ = "tender_keyword_matches"

    id = Column(BigInteger, primary_key=True)

    tender_id = Column(
        BigInteger,
        ForeignKey("tenders.id", ondelete="CASCADE"),
        nullable=False
    )

    keyword_id = Column(
        BigInteger,
        ForeignKey("keywords.id", ondelete="CASCADE"),
        nullable=False
    )

    match_location = Column(
        Enum(MatchLocation),
        nullable=False
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    keyword = relationship("Keyword", back_populates="tender_matches")
    tender = relationship("Tender", back_populates="keyword_matches")

    __table_args__ = (
        # Prevent duplicate matches
        UniqueConstraint(
            "tender_id",
            "keyword_id",
            "match_location",
            name="uq_tender_keyword_location"
        ),

        Index("idx_tender_keyword", "tender_id", "keyword_id"),
        Index("idx_keyword_created", "keyword_id", "created_at"),
    )

    def __repr__(self):
        return (
            f"<TenderKeywordMatch tender_id={self.tender_id} "
            f"keyword_id={self.keyword_id} location={self.match_location}>"
        )
