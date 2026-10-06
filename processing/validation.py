from typing import Dict, Any, Tuple
from urllib.parse import urlparse

def validate_record(record: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates record integrity against domain constraints."""
    if not record.get("source"):
        return False, "Missing mandatory field: 'source'"

    url = record.get("source_url", "")
    parsed_url = urlparse(str(url))
    if not parsed_url.scheme or not parsed_url.netloc:
        return False, f"Invalid or non-resolvable URL: '{url}'"

    if not record.get("name_or_title"):
        return False, "Missing primary content: 'name_or_title'"

    rating = record.get("rating")
    if rating is not None and not (1.0 <= rating <= 5.0):
        return False, f"Rating value out of bounds (1.0 - 5.0): {rating}"

    price = record.get("price")
    if price is not None and price < 0:
        return False, f"Negative price value rejected: {price}"

    return True, "Valid"