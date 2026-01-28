from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class SourceScraping(Base):
    __tablename__ = "source_scraping"

    id = Column(Integer, primary_key=True, index=True)

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    page_url = Column(String(1000), nullable=False)
    page_title = Column(String(255))

    # Human-readable instructions
    search_keyword = Column(String(255))
    page_type = Column(String(50))  # search_page | listing | direct_form

    actions = Column(JSON, nullable=False)
    results_mapping = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
