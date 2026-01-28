import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from app.scraping.base.scraper import BaseScraper
from app.scraping.utils.session_manager import SessionManager
from app.scraping.extractors.core_extractor import extract_core
from app.scraping.extractors.field_extractor import extract_fields


class HTMLScraper(BaseScraper):
    async def scrape(self) -> List[Dict]:
        session = SessionManager.get_session(self.source)

        response = session.get(self.source.url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        tenders = []

        for el in soup.select(".tender-item"):
            tender = self._extract(el)
            if tender and self.validate_tender_data(tender):
                tenders.append(tender)

        return tenders

    def _extract(self, element) -> Optional[Dict]:
        title = self.clean_text(element.get_text())
        if not title:
            return None

        return {
            "title": title,
            "reference_id": self.extract_reference_id(title),
            "source_url": self.source.url,
        }

    def fetch(self):
        response = requests.get(self.source.url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        tenders = []

        rows = soup.select(self.source.selector_config.get("row_selector"))

        for row in rows:
            raw = {
                "external_id": row.select_one(
                    self.source.selector_config["id"]
                ).text.strip(),

                "title": row.select_one(
                    self.source.selector_config["title"]
                ).text.strip(),

                "description": None,
                "published_date": None,
                "closing_date": None,
                "url": row.select_one("a")["href"],
            }

            fields = {}

            for field_name, selector in self.source.selector_config.get("fields", {}).items():
                element = row.select_one(selector)
                if element:
                    fields[field_name] = element.text

            tenders.append({
                "core": extract_core(raw),
                "fields": extract_fields(fields),
                "documents": []
            })

        return tenders