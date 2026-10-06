import pytest
from processing.cleaning import clean_price, clean_rating, clean_whitespace
from processing.validation import validate_record
from processing.deduplication import deduplicate_records

def test_clean_price():
    assert clean_price("£51.77") == 51.77
    assert clean_price("$19.99") == 19.99
    assert clean_price("Price: 42.00 INR") == 42.00
    assert clean_price(None) is None
    assert clean_price("") is None

def test_clean_rating():
    assert clean_rating("One") == 1.0
    assert clean_rating("Five") == 5.0
    assert clean_rating("4.0") == 4.0
    assert clean_rating(None) is None

def test_clean_whitespace():
    assert clean_whitespace("   A Light in the Attic \n\t") == "A Light in the Attic"
    assert clean_whitespace("“A timeless classic.”") == "A timeless classic."

def test_validate_record():
    valid = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/item.html",
        "name_or_title": "Example Book",
        "price": 20.0,
        "rating": 4.0
    }
    is_valid, _ = validate_record(valid)
    assert is_valid is True

    invalid_no_title = valid.copy()
    invalid_no_title["name_or_title"] = None
    is_valid, reason = validate_record(invalid_no_title)
    assert is_valid is False
    assert "name_or_title" in reason

    invalid_rating = valid.copy()
    invalid_rating["rating"] = 6.0
    is_valid, reason = validate_record(invalid_rating)
    assert is_valid is False
    assert "Rating value out of bounds" in reason

def test_deduplication():
    records = [
        {"source": "Quotes to Scrape", "name_or_title": "Be yourself; everyone else is taken."},
        {"source": "Quotes to Scrape", "name_or_title": "  BE YOURSELF; everyone else is taken!  "},
        {"source": "Quotes to Scrape", "name_or_title": "Different Quote entirely"}
    ]
    unique, dup_count = deduplicate_records(records)
    assert len(unique) == 2
    assert dup_count == 1