import os
import sys
import json
import logging
import time
import argparse
import pandas as pd
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import clean_record
from processing.validation import validate_record
from processing.deduplication import deduplicate_records

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("logs/scraper.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Web Scraping & Consolidation Pipeline")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum pages to scrape per source (default: all)")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("PipelineOrchestrator")
    start_time = time.time()
    
    os.makedirs("output", exist_ok=True)
    logger.info("Pipeline execution triggered.")

    # 1. Extraction Phase
    books_scraper = BooksScraper()
    quotes_scraper = QuotesScraper()

    raw_books = books_scraper.scrape(max_pages=args.max_pages)
    raw_quotes = quotes_scraper.scrape(max_pages=args.max_pages)
    total_scraped = len(raw_books) + len(raw_quotes)

    # 2. Cleaning Phase
    all_raw = raw_books + raw_quotes
    cleaned_records = [clean_record(r) for r in all_raw]
    logger.info(f"Standardized {len(cleaned_records)} raw records.")

    # 3. Validation Phase
    valid_records = []
    rejected_records = []
    for record in cleaned_records:
        is_valid, reason = validate_record(record)
        if is_valid:
            valid_records.append(record)
        else:
            rejected_records.append({"record": record, "reason": reason})

    logger.info(f"Validation summary: {len(valid_records)} accepted, {len(rejected_records)} rejected.")

    # 4. Deduplication Phase
    unique_records, duplicate_count = deduplicate_records(valid_records)
    logger.info(f"Deduplication summary: {duplicate_count} duplicate items removed.")

    # 5. Data Consolidation & Export
    df = pd.DataFrame(unique_records)
    csv_path = "output/final_dataset.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"Consolidated dataset saved to {csv_path}")

    # 6. Summary Report Generation
    execution_time = round(time.time() - start_time, 2)
    summary_report = {
        "execution_time_seconds": execution_time,
        "total_records_collected": total_scraped,
        "records_per_source": {
            "Books to Scrape": len(raw_books),
            "Quotes to Scrape": len(raw_quotes)
        },
        "records_after_cleaning": len(cleaned_records),
        "records_rejected_validation": len(rejected_records),
        "duplicate_records_removed": duplicate_count,
        "final_record_count": len(unique_records),
        "validation_rejections_sample": rejected_records[:5]
    }

    summary_path = "output/summary_report.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=4)
    logger.info(f"Execution summary generated at {summary_path}")

if __name__ == "__main__":
    main()