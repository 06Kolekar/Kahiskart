from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Date,
    Text,
    ForeignKey,
    JSON,
)



class Tender(Base):
    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    title = Column(String(500), nullable=False, index=True)
    reference_id = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)

    # Agency & Location
    agency_name = Column(String(255), index=True)
    agency_location = Column(String(255))

    # Dates
    published_date = Column(Date, index=True)
    deadline_date = Column(Date, index=True)

    # Source Information
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    source_url = Column(String(1000))

    # Status
    status = Column(String(50), default="new", index=True)

    # Attachments
    attachments = Column(JSON)

    # Change Detection
    content_hash = Column(String(64), index=True)
    version = Column(Integer, default=1)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # --------------------
    # RELATIONSHIPS
    # --------------------
    source = relationship("Source", back_populates="tenders")

    notifications = relationship(
        "Notification",
        back_populates="tender",
        cascade="all, delete-orphan"
    )

    keyword_matches = relationship(
        "TenderKeywordMatch",
        back_populates="tender",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Tender {self.reference_id}: {self.title[:50]}>"

    @property
    def days_until_deadline(self):
        if self.deadline_date:
            return (self.deadline_date - datetime.utcnow().date()).days
        return None

    @property
    def is_expired(self):
        if self.deadline_date:
            return self.deadline_date < datetime.utcnow().date()
        return False
