from sqlalchemy import Column, BigInteger, ForeignKey, JSON, Text
from app.core.database import Base


class TenderRawData(Base):
    __tablename__ = "tender_raw_data"

    id = Column(BigInteger, primary_key=True)
    tender_id = Column(BigInteger, ForeignKey("tenders.id"))
    raw_json = Column(JSON)
    html_snapshot = Column(Text)
