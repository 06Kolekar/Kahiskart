from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# =====================================================
# DATABASE ENGINE
# =====================================================

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # SQL logs in dev
    pool_pre_ping=True,                          # Auto-reconnect
    future=True
)

# =====================================================
# ASYNC SESSION FACTORY
# =====================================================

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# =====================================================
# BASE MODEL
# =====================================================

Base = declarative_base()

# =====================================================
# FASTAPI DB DEPENDENCY
# =====================================================

async def get_db() -> AsyncSession:
    """
    FastAPI dependency.
    Provides a database session per request
    and ensures proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
