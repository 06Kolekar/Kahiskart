from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TenderField(Base):
    __tablename__ = "tender_fields"

    id = Column(Integer, primary_key=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))

    field_name = Column(String(255))
    field_value = Column(Text)
    field_type = Column(String(50))

    tender = relationship("Tender", back_populates="fields")
