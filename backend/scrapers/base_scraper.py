import asyncio
import logging
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ScraperEngine")


class BaseScraper(ABC):
    """Production-grade abstract base scraper with anti-detection safeguards."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    ]

    def __init__(self, name: str, rate_limit_delay: float = 2.5):
        self.name = name
        self.rate_limit_delay = rate_limit_delay
        self.client: Optional[httpx.AsyncClient] = None

    def get_random_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    async def setup_session(self):
        if not self.client:
            self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def close_session(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    @abstractmethod
    async def scrape(self, route_from: str, route_to: str, departure_date: str) -> List[Dict]:
        """Scrape raw fare records for a single city pair and departure date."""
        pass

    async def scrape_advance_windows(
        self, route_from: str, route_to: str, windows: List[int] = [1, 7, 15, 30, 45]
    ) -> List[Dict]:
        """Collects fares systematically across the 5 standard lead-time windows."""
        all_fares = []
        today = datetime.now()

        for window in windows:
            target_date = today + timedelta(days=window)
            date_str = target_date.strftime("%Y-%m-%d")
            logger.info(f"[{self.name}] Scraping {route_from}->{route_to} for T+{window} ({date_str})")
            
            try:
                fares = await self.scrape(route_from, route_to, date_str)
                for f in fares:
                    f["advance_window"] = window
                all_fares.extend(fares)
                logger.info(f"[{self.name}] Harvested {len(fares)} fares for T+{window}")
            except Exception as e:
                logger.error(f"[{self.name}] Error scraping T+{window} window: {str(e)}")

            # Polite jitter to evade rate limits
            await asyncio.sleep(self.rate_limit_delay + random.uniform(0.5, 1.5))

        return all_fares