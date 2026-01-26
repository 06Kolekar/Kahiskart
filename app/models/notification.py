from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    BigInteger,
    Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum
from sqlalchemy.dialects.mysql import BIGINT

class NotificationType(str, enum.Enum):
    NEW_TENDER = "new_tender"
    KEYWORD_MATCH = "keyword_match"
    DEADLINE_APPROACHING = "deadline_approaching"
    SYSTEM_ERROR = "system_error"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    DESKTOP = "desktop"
    BOTH = "both"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(BigInteger, primary_key=True, index=True)

    # --------------------
    # Ownership
    # --------------------
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    tender_id = Column(
        BigInteger,
        ForeignKey("tenders.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # --------------------
    # Notification Details
    # --------------------
    type = Column(Enum(NotificationType), nullable=False, index=True)
    channel = Column(Enum(NotificationChannel), default=NotificationChannel.BOTH)

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # --------------------
    # Status
    # --------------------
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_sent = Column(Boolean, default=False, nullable=False)

    email_sent = Column(Boolean, default=False)
    desktop_sent = Column(Boolean, default=False)

    sent_at = Column(DateTime, nullable=True)

    # --------------------
    # Error / Retry
    # --------------------
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # --------------------
    # Metadata
    # --------------------
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # --------------------
    # Relationships
    # --------------------
    user = relationship("User", back_populates="notifications")
    tender = relationship("Tender", back_populates="notifications")

    __table_args__ = (
        Index("idx_user_unread", "user_id", "is_read"),
        Index("idx_type_created", "type", "created_at"),
    )

    def __repr__(self):
        return (
            f"<Notification "
            f"id={self.id} "
            f"type={self.type} "
            f"user_id={self.user_id} "
            f"is_read={self.is_read}>"
        )
