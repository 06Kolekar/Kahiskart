from datetime import datetime

def parse_deadline(value):
    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d"
    ]

    for f in formats:
        try:
            return datetime.strptime(value, f)
        except:
            pass

    return None
