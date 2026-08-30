"""
STEP 9.5: BACKGROUND TASK SCHEDULER
Periodically coordinates scraper harvests, data sanitization,
MongoDB insertion, and daily index generation.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone

# Ensure backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.mongo_manager import mongo_db
from tasks.ingestion_pipeline import DataIngestionEngine
from scrapers.indigo_scraper import IndigoScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TaskScheduler")

# Official DGCA Evaluation Route Pairs
ROUTE_PAIRS = [
    ("DEL", "BOM"),
    ("BOM", "DEL"),
    ("BLR", "DEL"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BOM", "GOI"),
    ("DEL", "HYD")
]

ADVANCE_WINDOWS = [1, 7, 15, 30, 45]


class APITaskScheduler:
    is_running = False

    @classmethod
    async def run_harvest_and_compute_cycle(cls) -> dict:
        """
        Executes one full end-to-end telemetry cycle:
        1. Scrape routes across advance windows.
        2. Insert raw records into 'raw_fares' collection.
        3. Clean data & remove statistical outliers.
        4. Recompute daily APIx index & update 'apix_index'.
        """
        logger.info("🕒 Starting automated airfare telemetry cycle...")
        scraper = IndigoScraper()
        total_raw_collected = []

        # 1. Scrape all routes
        for origin, dest in ROUTE_PAIRS:
            try:
                fares = await scraper.scrape_advance_windows(origin, dest, windows=ADVANCE_WINDOWS)
                total_raw_collected.extend(fares)
            except Exception as e:
                logger.error(f"Error scraping route {origin}-{dest}: {e}")

        logger.info(f"📊 Harvested {len(total_raw_collected)} raw fare observations.")

        # 2. Persist to MongoDB raw_fares
        db = mongo_db.db
        if db is not None and total_raw_collected:
            try:
                raw_docs = []
                for item in total_raw_collected:
                    doc = {
                        "date": datetime.now(timezone.utc),
                        "source": item.get("source", "indigo"),
                        "departure": item.get("route_from", "DEL"),
                        "arrival": item.get("route_to", "BOM"),
                        "airline": item.get("airline", "IndiGo"),
                        "baseFare": float(item.get("base_fare", item.get("total_price", 5000) * 0.85)),
                        "tax": float(item.get("tax", item.get("total_price", 5000) * 0.15)),
                        "totalFare": float(item.get("total_price", 5000)),
                        "advancePurchaseWindow": f"T+{item.get('advance_window', 7)}",
                        "valid": True,
                        "scrapedAt": datetime.now(timezone.utc)
                    }
                    raw_docs.append(doc)
                await db["raw_fares"].insert_many(raw_docs)
            except Exception as e:
                logger.warning(f"Failed to persist raw records to MongoDB: {e}")

        # 3. Clean & Sanitize
        cleaned_count = await DataIngestionEngine.process_and_clean_raw_fares()

        # 4. Recompute Daily APIx
        index_result = await DataIngestionEngine.compute_daily_apix_index()
        logger.info(f"✨ Telemetry cycle complete. APIx Index: {index_result['dailyIndex']['value']}")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_collected": len(total_raw_collected),
            "cleaned_processed": cleaned_count,
            "apix_index": index_result["dailyIndex"]["value"]
        }

    @classmethod
    async def start_periodic_scheduler(cls, interval_seconds: int = 3600):
        """
        Runs continuously in the background at the specified interval.
        Default: 3600s (1 hour).
        """
        cls.is_running = True
        logger.info(f"🚀 Task Scheduler started (Interval: {interval_seconds}s).")
        while cls.is_running:
            try:
                await cls.run_harvest_and_compute_cycle()
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
            await asyncio.sleep(interval_seconds)

    @classmethod
    def stop_scheduler(cls):
        cls.is_running = False
        logger.info("🛑 Task Scheduler stopped.")