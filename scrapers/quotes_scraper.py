import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class QuotesScraper(BaseScraper):
    def __init__(self, base_url: str = "https://quotes.toscrape.com/"):
        super().__init__(base_url=base_url)

    def scrape(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        records = []
        current_url = self.base_url
        page_num = 1

        logger.info("Initializing Quotes to Scrape spider.")
        while current_url:
            if max_pages and page_num > max_pages:
                logger.info(f"Page limit reached ({max_pages}) for Quotes.")
                break

            logger.info(f"[Quotes to Scrape] Fetching page {page_num}: {current_url}")
            response = self.fetch(current_url)
            if not response:
                logger.warning(f"Skipping page {page_num} due to fetch error.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            quote_pods = soup.select("div.quote")
            if not quote_pods:
                logger.warning(f"No quotes discovered on page {page_num}.")
                break

            for pod in quote_pods:
                try:
                    text_elem = pod.select_one("span.text")
                    quote_text = text_elem.get_text() if text_elem else None

                    author_elem = pod.select_one("small.author")
                    author = author_elem.get_text(strip=True) if author_elem else None

                    author_link = pod.select_one("span > a")
                    author_url = urljoin(self.base_url, author_link.get("href")) if author_link else current_url

                    tags = [t.get_text(strip=True) for t in pod.select("div.tags a.tag")]
                    tags_str = ", ".join(tags) if tags else None

                    records.append({
                        "source": "Quotes to Scrape",
                        "source_url": author_url,
                        "name_or_title": quote_text,
                        "category": "Quotes",
                        "price": None,
                        "rating": None,
                        "author": author,
                        "tags": tags_str,
                        "description": quote_text,
                        "scraped_at": datetime.now(timezone.utc).isoformat()
                    })
                except Exception as item_err:
                    logger.warning(f"Error parsing quote item on page {page_num}: {item_err}")
                    continue

            # Pagination resolution
            next_tag = soup.select_one("li.next > a")
            if next_tag and next_tag.get("href"):
                current_url = urljoin(self.base_url, next_tag.get("href"))
                page_num += 1
            else:
                logger.info(f"Terminating Quotes crawl: no next page selector on page {page_num}.")
                current_url = None

        logger.info(f"Finished Quotes scraping. Total records collected: {len(records)}")
        return records