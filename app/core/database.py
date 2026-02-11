# import os
# from sqlalchemy.ext.asyncio import (
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine
# )
# from sqlalchemy.orm import sessionmaker, declarative_base
# from app.core.config import settings

# # -------------------------
# # ASYNC ENGINE
# # -------------------------
# DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# if DB_TYPE == "mysql":
#     DATABASE_URL = "mysql+aiomysql://user:pass@localhost/tender_db"
# else:
#     DATABASE_URL = "sqlite+aiosqlite:///./tender_local.db"

# engine = create_async_engine(
#     DATABASE_URL,
#     connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
# )
# AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
# Base = declarative_base()
# # engine = create_async_engine(
# #     settings.DATABASE_URL,
# #     echo=settings.ENVIRONMENT == "development",
# #     pool_pre_ping=True
# # )

# # -------------------------
# # ASYNC SESSION FACTORY
# # -------------------------
# AsyncSessionLocal = async_sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

# # -------------------------
# # BASE
# # -------------------------
# Base = declarative_base()

# # -------------------------
# # FASTAPI DEPENDENCY
# # -------------------------
# async def get_db() -> AsyncSession:
#     async with AsyncSessionLocal() as session:
#         yield session

import os, sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -------------------------
# EXE SAFE PATH
# -------------------------
def get_base_path():
    if getattr(sys, 'frozen', False):   # EXE mode
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
SQLITE_DB_PATH = os.path.join(BASE_DIR, "tender_local.db")

# -------------------------
# DATABASE SWITCH
# -------------------------
DB_TYPE = os.getenv("DB_TYPE", "sqlite")   # mysql or sqlite

if DB_TYPE == "mysql":
    DATABASE_URL_ASYNC = "mysql+aiomysql://user:pass@localhost/tender_db"
    DATABASE_URL_SYNC = "mysql+pymysql://user:pass@localhost/tender_db"
else:
    DATABASE_URL_ASYNC = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"
    DATABASE_URL_SYNC = f"sqlite:///{SQLITE_DB_PATH}"

# -------------------------
# ASYNC ENGINE (FastAPI)
# -------------------------
engine = create_async_engine(
    DATABASE_URL_ASYNC,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL_ASYNC else {}
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# -------------------------
# SYNC ENGINE (Excel Bulk Insert)
# -------------------------
engine_sync = create_engine(
    DATABASE_URL_SYNC,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL_SYNC else {}
)

SyncSessionLocal = sessionmaker(bind=engine_sync)

# -------------------------
# BASE ORM
# -------------------------
Base = declarative_base()

# -------------------------
# FASTAPI DEPENDENCY
# -------------------------
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
