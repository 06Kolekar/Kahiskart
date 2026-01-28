from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TenderDocument(Base):
    __tablename__ = "tender_documents"

    id = Column(Integer, primary_key=True)
    tender_id = Column(Integer, ForeignKey("tenders.id"))

    document_name = Column(String(255))
    document_url = Column(Text)
    document_type = Column(String(50))
    local_path = Column(Text)

    tender = relationship("Tender", back_populates="documents")
