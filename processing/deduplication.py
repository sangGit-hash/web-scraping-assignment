import re
from typing import List, Dict, Any, Tuple

def generate_dedup_key(record: Dict[str, Any]) -> str:
    """Constructs an invariant compound key: source::normalized_content"""
    source = (record.get("source") or "").lower().strip()
    name = (record.get("name_or_title") or "").lower()
    normalized_name = re.sub(r"[^\w\s]", "", name)
    normalized_name = re.sub(r"\s+", " ", normalized_name).strip()
    return f"{source}::{normalized_name}"

def deduplicate_records(records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """Filters duplicate items and tracks duplicate occurrences."""
    seen_keys = set()
    unique_records = []
    duplicate_count = 0

    for rec in records:
        key = generate_dedup_key(rec)
        if key in seen_keys:
            duplicate_count += 1
            continue
        seen_keys.add(key)
        unique_records.append(rec)

    return unique_records, duplicate_count