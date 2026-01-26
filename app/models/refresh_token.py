from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    BigInteger,
    Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from sqlalchemy.dialects.mysql import BIGINT

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(BigInteger, primary_key=True, index=True)

    # --------------------
    # Token Security
    # --------------------
    token_hash = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )

    # --------------------
    # Ownership
    # --------------------
    user_id = Column(
        BIGINT(unsigned=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens"
    )

    # --------------------
    # Lifecycle
    # --------------------
    expires_at = Column(DateTime, nullable=False)

    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    # Optional: track device / session
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 safe

    # --------------------
    # Metadata
    # --------------------
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_refresh_user_active", "user_id", "revoked"),
        Index("idx_refresh_expires", "expires_at"),
    )

    def __repr__(self):
        return (
            f"<RefreshToken "
            f"user_id={self.user_id} "
            f"revoked={self.revoked} "
            f"expires_at={self.expires_at}>"
        )
