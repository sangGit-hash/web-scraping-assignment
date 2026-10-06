import re
from typing import Dict, Any, Optional

RATING_MAP = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "four": 4.0,
    "five": 5.0
}

def clean_whitespace(val: Optional[str]) -> Optional[str]:
    """Collapses duplicate whitespace, tabs, and newlines; trims boundaries."""
    if not val or not isinstance(val, str):
        return None
    cleaned = re.sub(r"\s+", " ", val).strip()
    cleaned = cleaned.strip("“”\"'")
    return cleaned if cleaned else None

def clean_price(val: Any) -> Optional[float]:
    """Extracts numeric values from currency strings (e.g., '£51.77' -> 51.77)."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return round(float(val), 2)
    match = re.search(r"(\d+(\.\d+)?)", str(val))
    return round(float(match.group(1)), 2) if match else None

def clean_rating(val: Any) -> Optional[float]:
    """Converts written word star ratings to numeric 1.0 - 5.0."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    normalized = str(val).lower().strip()
    if normalized in RATING_MAP:
        return RATING_MAP[normalized]
    match = re.search(r"(\d+(\.\d+)?)", normalized)
    return float(match.group(1)) if match else None

def clean_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Standardizes a single raw dictionary record."""
    return {
        "source": clean_whitespace(record.get("source")),
        "source_url": clean_whitespace(record.get("source_url")),
        "name_or_title": clean_whitespace(record.get("name_or_title")),
        "category": clean_whitespace(record.get("category")),
        "price": clean_price(record.get("price")),
        "rating": clean_rating(record.get("rating")),
        "author": clean_whitespace(record.get("author")),
        "tags": clean_whitespace(record.get("tags")),
        "description": clean_whitespace(record.get("description")),
        "scraped_at": record.get("scraped_at")
    }