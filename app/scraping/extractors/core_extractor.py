from datetime import datetime
import hashlib


def generate_hash(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def extract_core(raw: dict) -> dict:
    """
    Normalize core tender fields
    """
    content_string = f"{raw.get('title')}{raw.get('description')}{raw.get('url')}"

    return {
        "external_id": raw.get("external_id"),
        "title": raw.get("title"),
        "description": raw.get("description"),
        "published_date": raw.get("published_date"),
        "closing_date": raw.get("closing_date"),
        "tender_url": raw.get("url"),
        "hash_signature": generate_hash(content_string),
    }
