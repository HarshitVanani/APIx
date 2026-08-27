import os
import sys
from pathlib import Path

# Add backend directory to Python sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import asyncio
import logging
from datetime import datetime
from scrapers.indigo_scraper import IndigoScraper
from services.data_cleaner import DataCleaner
from services.index_calculator import APIxIndexEngine
from services.mongo_service import mongo_db
from services.dgca_service import DGCAService

logger = logging.getLogger("ScraperWorker")


async def run_daily_scraping_job():
    """Automated batch pipeline executed every 24 hours."""
    logger.info("Starting scheduled multi-route scraping pipeline...")
    scraper = IndigoScraper()
    raw_harvest = []

    # Iterate over top DGCA high-density city pairs
    routes = DGCAService.DGCA_ROUTE_BASKET[:4]  # Top 4 representative pairs
    windows = [1, 7, 15, 30, 45]

    for r in routes:
        fares = await scraper.scrape_advance_windows(
            route_from=r["origin"],
            route_to=r["destination"],
            windows=windows
        )
        raw_harvest.extend(fares)

    # 1. Store raw payload in MongoDB
    if raw_harvest:
        mongo_db.insert_raw_fares(raw_harvest)

    # 2. Clean, deduplicate & filter outliers
    cleaned = DataCleaner.clean_fare_batch(raw_harvest)
    if cleaned:
        mongo_db.insert_cleaned_fares(cleaned)

    # 3. Calculate daily APIx benchmark
    daily_index = APIxIndexEngine.calculate_daily_apix(cleaned)
    logger.info(f"Daily Index Generated: {daily_index['index_value']} (Data points: {daily_index['data_points']})")

    return daily_index


if __name__ == "__main__":
    mongo_db.connect()
    asyncio.run(run_daily_scraping_job())