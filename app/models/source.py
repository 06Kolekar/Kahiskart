from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    Enum,
    BigInteger,
    Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum

class SourceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    ERROR = "ERROR"
    WARNING = "WARNING"


class LoginType(str, enum.Enum):
    PUBLIC = "PUBLIC"
    REQUIRED = "REQUIRED"


class Source(Base):
    __tablename__ = "sources"

    id = Column(BigInteger, primary_key=True, index=True)

    # --------------------
    # Basic Information
    # --------------------
    name = Column(String(255), nullable=False, index=True)
    base_url = Column(String(1000), nullable=False)
    description = Column(Text)

    # --------------------
    # Authentication
    # --------------------
    login_type = Column(
        Enum(LoginType),
        default=LoginType.PUBLIC,
        nullable=False
    )

    login_url = Column(String(1000))
    encrypted_credentials = Column(Text)  
    # Store encrypted JSON: {"username": "...", "password": "..."}

    # --------------------
    # Scraper Configuration
    # --------------------
    scraper_type = Column(
        String(50),
        default="html",
        nullable=False
    )  
    # html | js | api | pdf | portal

    selector_config = Column(JSON)
    # Example:
    # {
    #   "title": ".tender-title",
    #   "closing_date": ".date-close",
    #   "pagination": ".next"
    # }

    # --------------------
    # Status & Health
    # --------------------
    status = Column(
        Enum(SourceStatus),
        default=SourceStatus.ACTIVE,
        index=True
    )

    is_active = Column(Boolean, default=True)

    # --------------------
    # Scraping Metrics
    # --------------------
    total_tenders = Column(Integer, default=0)
    last_fetch_at = Column(DateTime)
    last_success_at = Column(DateTime)
    consecutive_failures = Column(Integer, default=0)

    # --------------------
    # Metadata
    # --------------------
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # --------------------
    # Relationships
    # --------------------
    tenders = relationship(
        "Tender",
        back_populates="source",
        cascade="all, delete-orphan"
    )

    fetch_logs = relationship(
        "FetchLog",
        back_populates="source",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_source_status_active", "status", "is_active"),
    )

    def __repr__(self):
        return f"<Source id={self.id} name={self.name} status={self.status}>"
