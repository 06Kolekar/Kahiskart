from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    BigInteger,
    Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class FetchStatus(str, enum.Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class FetchLog(Base):
    __tablename__ = "fetch_logs"

    id = Column(BigInteger, primary_key=True, index=True)

    source_id = Column(
        BigInteger,
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Denormalized (snapshot at fetch time)
    source_name = Column(String(255), nullable=False, index=True)

    # Fetch result
    status = Column(
        Enum(FetchStatus, name="fetchstatus"),
        nullable=False,
        index=True
    )

    message = Column(Text, nullable=False)

    # Statistics
    tenders_found = Column(Integer, default=0, nullable=False)
    new_tenders = Column(Integer, default=0, nullable=False)
    updated_tenders = Column(Integer, default=0, nullable=False)

    # Error Details
    error_details = Column(Text)

    # Timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    source = relationship("Source", back_populates="fetch_logs")

    __table_args__ = (
        Index("idx_fetch_source_status", "source_id", "status"),
        Index("idx_fetch_created", "created_at"),
    )

    def __repr__(self):
        return (
            f"<FetchLog source_id={self.source_id} "
            f"status={self.status} "
            f"found={self.tenders_found}>"
        )
