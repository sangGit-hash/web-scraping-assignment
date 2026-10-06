import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class BooksScraper(BaseScraper):
    def __init__(self, base_url: str = "https://books.toscrape.com/"):
        super().__init__(base_url=base_url)

    def scrape(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        records = []
        current_url = urljoin(self.base_url, "catalogue/page-1.html")
        page_num = 1

        logger.info("Initializing Books to Scrape spider.")
        while current_url:
            if max_pages and page_num > max_pages:
                logger.info(f"Page limit reached ({max_pages}) for Books.")
                break

            logger.info(f"[Books to Scrape] Fetching page {page_num}: {current_url}")
            response = self.fetch(current_url)
            if not response:
                logger.warning(f"Skipping page {page_num} due to fetch error.")
                break

            soup = BeautifulSoup(response.text, "html.parser")
            product_pods = soup.select("article.product_pod")
            if not product_pods:
                logger.warning(f"No product items discovered on page {page_num}.")
                break

            for pod in product_pods:
                try:
                    title_elem = pod.select_one("h3 > a")
                    name = title_elem.get("title") or title_elem.get_text() if title_elem else None
                    prod_rel_url = title_elem.get("href") if title_elem else ""
                    prod_url = urljoin(current_url, prod_rel_url)

                    price_elem = pod.select_one("p.price_color")
                    raw_price = price_elem.get_text(strip=True) if price_elem else None

                    star_tag = pod.select_one("p.star-rating")
                    rating_classes = star_tag.get("class", []) if star_tag else []
                    raw_rating = next((c for c in rating_classes if c != "star-rating"), None)

                    avail_elem = pod.select_one("p.instock.availability")
                    availability = avail_elem.get_text(strip=True) if avail_elem else None

                    records.append({
                        "source": "Books to Scrape",
                        "source_url": prod_url,
                        "name_or_title": name,
                        "category": "Books",
                        "price": raw_price,
                        "rating": raw_rating,
                        "author": None,
                        "tags": availability,
                        "description": None,
                        "scraped_at": datetime.now(timezone.utc).isoformat()
                    })
                except Exception as item_err:
                    logger.warning(f"Error parsing item on page {page_num}: {item_err}")
                    continue

            # Pagination resolution
            next_tag = soup.select_one("li.next > a")
            if next_tag and next_tag.get("href"):
                current_url = urljoin(current_url, next_tag.get("href"))
                page_num += 1
            else:
                logger.info(f"Terminating Books crawl: no next page selector on page {page_num}.")
                current_url = None

        logger.info(f"Finished Books scraping. Total records collected: {len(records)}")
        return records