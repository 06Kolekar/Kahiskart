def extract_fields(raw_fields: dict) -> dict:
    """
    Converts site-specific fields to clean dict
    """
    cleaned = {}

    for key, value in raw_fields.items():
        if not value:
            continue
        cleaned[key.strip()] = str(value).strip()

    return cleaned
