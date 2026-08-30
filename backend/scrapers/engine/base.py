import abc
import asyncio
import hashlib
import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
logger = logging.getLogger("APIx.ScraperEngine")


class RawFarePayload(BaseModel):
    fare_id: str
    source: str
    airline_code: str
    flight_number: str
    origin_iata: str
    destination_iata: str
    departure_datetime: datetime
    arrival_datetime: datetime
    duration_minutes: int
    stops: int
    base_fare: float
    taxes_and_surcharges: float
    total_fare: float
    currency: str = "INR"
    advance_purchase_window: int
    cabin_class: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("origin_iata", "destination_iata")
    @classmethod
    def validate_iata(cls, v: str) -> str:
        code = v.strip().upper()
        if len(code) != 3 or not code.isalpha():
            raise ValueError(f"Invalid IATA station code: {v}")
        return code

    @field_validator("total_fare")
    @classmethod
    def validate_fare(cls, v: float) -> float:
        if v <= 500.0 or v > 500000.0:
            raise ValueError(f"Abnormal fare value detected: {v}")
        return round(v, 2)


class BaseAirfareEngine(abc.ABC):
    """
    Production-grade base scraper handling context isolation,
    anti-fingerprinting, human-mimicking jitter, and network interception.
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ]

    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1440, "height": 900},
        {"width": 1536, "height": 864},
    ]

    def __init__(self, name: str, concurrency_limit: int = 3, proxy: Optional[str] = None):
        self.name = name
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.proxy = {"server": proxy} if proxy else None
        self._playwright = None
        self._browser: Optional[Browser] = None

    async def initialize_engine(self) -> None:
        if not self._browser:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--window-position=0,0",
                    "--ignore-certificate-errors",
                    "--disable-extensions",
                    "--disable-gpu",
                ],
                proxy=self.proxy,
            )
            logger.info(f"[{self.name}] Chrome CDP runtime initialized.")

    async def create_stealth_context(self) -> BrowserContext:
        if not self._browser:
            await self.initialize_engine()

        ua = random.choice(self.USER_AGENTS)
        vp = random.choice(self.VIEWPORTS)

        context = await self._browser.new_context(
            user_agent=ua,
            viewport=vp,
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            color_scheme="light",
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            java_script_enabled=True,
        )

        # Apply stealth patches to bypass webdriver and automation heuristics
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-IN', 'en-US', 'en'] });
        """)
        return context

    @staticmethod
    def generate_fingerprint_id(source: str, flight_num: str, origin: str, dest: str, dep_time: str) -> str:
        raw_key = f"{source}:{flight_num}:{origin}:{dest}:{dep_time}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    async def jitter_sleep(min_sec: float = 1.2, max_sec: float = 3.5) -> None:
        await asyncio.sleep(random.uniform(min_sec, max_sec))

    @abc.abstractmethod
    async def fetch_route_fares(
        self, origin: str, destination: str, travel_date: datetime, advance_window: int
    ) -> List[RawFarePayload]:
        pass

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        logger.info(f"[{self.name}] Engine shutdown complete.")