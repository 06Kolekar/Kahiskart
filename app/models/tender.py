from sqlalchemy import (
    Column, String, Text, Date, DateTime,
    BigInteger, Enum, DECIMAL, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Tender(Base):
    __tablename__ = "tenders"

    id = Column(BigInteger, primary_key=True, index=True)

    # Source info
    source_id = Column(BigInteger, ForeignKey("sources.id"), nullable=False)
    source_name = Column(String(100), nullable=False)

    # Core fields (common across most portals)
    title = Column(Text, nullable=False)
    description = Column(Text)

    published_date = Column(Date)
    closing_date = Column(Date)

    tender_value = Column(DECIMAL(18, 2))
    currency = Column(String(10))

    organization = Column(String(255))
    location = Column(String(255))

    tender_url = Column(Text, nullable=False)
    document_url = Column(Text)

    status = Column(
        Enum(TenderStatus),
        default=TenderStatus.UNKNOWN,
        index=True
    )

    # De-duplication & tracking
    checksum = Column(String(64), unique=True, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    attributes = relationship(
        "TenderAttribute",
        back_populates="tender",
        cascade="all, delete-orphan"
    )

    raw_data = relationship(
        "TenderRawData",
        back_populates="tender",
        cascade="all, delete-orphan",
        uselist=False
    )

    __table_args__ = (
        Index("idx_tender_dates", "published_date", "closing_date"),
    )

    def __repr__(self):
        return f"<Tender {self.title[:50]}>"
