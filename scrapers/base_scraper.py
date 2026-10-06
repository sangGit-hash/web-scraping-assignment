import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class providing standard HTTP handling, polite rate limiting,
    and automatic exponential backoff retries.
    """
    def __init__(self, base_url: str, delay: float = 0.5, timeout: int = 15):
        self.base_url = base_url
        self.delay = delay
        self.timeout = timeout
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9"
        })
        return session

    def fetch(self, url: str) -> Optional[requests.Response]:
        """Fetches page content with polite rate limiting and timeout management."""
        time.sleep(self.delay)
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as exc:
            logger.error(f"Failed to fetch {url}: {exc}")
            return None

    @abstractmethod
    def scrape(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Executes source-specific pagination and extraction logic."""
        pass