from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "..", "tender_local.db")

SYNC_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine_sync = create_engine(SYNC_DATABASE_URL, connect_args={"check_same_thread": False})
SyncSessionLocal = sessionmaker(bind=engine_sync)

# Use sync mysql driver
# DATABASE_URL_SYNC = settings.DATABASE_URL.replace("+asyncmy", "+pymysql")

# engine_sync = create_engine(
#     DATABASE_URL_SYNC,
#     pool_pre_ping=True,
#     pool_recycle=3600,
# )

# SyncSessionLocal = sessionmaker(bind=engine_sync)
