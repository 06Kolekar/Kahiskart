from sqlalchemy import Column, BigInteger, String, DateTime, Index
from app.core.database import Base
from datetime import datetime

class ExcelRowClean(Base):
    __tablename__ = "excel_row_clean"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sheet_id = Column(String(255))
    title = Column(String(1000))
    agency = Column(String(500))
    deadline = Column(DateTime)
    url = Column(String(2000))
    source = Column(String(255))
    row_hash = Column(String(64), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Index("ix_excel_row_clean_deadline", ExcelRowClean.deadline)
