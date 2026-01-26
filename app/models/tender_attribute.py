from sqlalchemy import Column, String, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class TenderAttribute(Base):
    __tablename__ = "tender_attributes"

    id = Column(BigInteger, primary_key=True)
    tender_id = Column(
        BigInteger,
        ForeignKey("tenders.id", ondelete="CASCADE"),
        index=True
    )

    attribute_key = Column(String(100), index=True)
    attribute_value = Column(Text)

    tender = relationship("Tender", back_populates="attributes")

    def __repr__(self):
        return f"<Attr {self.attribute_key}={self.attribute_value}>"
