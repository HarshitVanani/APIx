"""
STEP 9.12: MASTER SCRAPER ORCHESTRATOR & UNIFIED INGESTION BRIDGE
SIH 2026 - APIx Project (PS 26056)
Coordinates:
  - 4 Direct Airline Scrapers (IndiGo, Air India, SpiceJet, Akasa Air)
  - 3 OTA Aggregator Scrapers (EaseMyTrip, MakeMyTrip, Yatra)
  - Automatic Ingestion, Deduplication, and Laspeyres Index Generation
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

# Ensure root directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.scrapers.airline_scrapers import airline_orchestrator
from backend.scrapers.base_scraper import FareRecord
from backend.scrapers.ota_scrapers import ota_orchestrator
from backend.services.mongo_manager import mongo_db
from backend.services.redis_cache_service import redis_cache
from backend.tasks.ingestion_pipeline import DataIngestionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterOrchestrator")

DEFAULT_ROUTES: List[Tuple[str, str]] = [
    ("DEL", "BOM"),
    ("BOM", "DEL"),
    ("BLR", "DEL"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BOM", "GOI"),
    ("DEL", "HYD"),
]

DEFAULT_WINDOWS: List[str] = ["T+1", "T+7", "T+15", "T+30", "T+45"]


class MasterScraperOrchestrator:
    """Master controller executing airline and OTA harvests into MongoDB."""

    def __init__(self):
        self.airline_orchestrator = airline_orchestrator
        self.ota_orchestrator = ota_orchestrator

    async def execute_full_harvest(
        self,
        routes: List[Tuple[str, str]] = DEFAULT_ROUTES,
        advance_windows: List[str] = DEFAULT_WINDOWS,
    ) -> Dict[str, Any]:
        """Runs parallel extraction across all sources and persists data to MongoDB."""
        start_time = datetime.now(timezone.utc)
        logger.info("🚀 [MASTER HARVEST] Launching full multi-source harvest across Airlines and OTAs...")

        # Step 1: Run Airline and OTA orchestrators in parallel
        airline_task = self.airline_orchestrator.scrape_all(routes, advance_windows)
        ota_task = self.ota_orchestrator.scrape_all(routes, advance_windows)

        airline_res, ota_res = await asyncio.gather(airline_task, ota_task)

        # Step 2: Flatten all FareRecord models into standard raw dictionaries
        raw_fares_payload: List[Dict[str, Any]] = []

        for carrier, fare_records in airline_res.items():
            for rec in fare_records:
                raw_fares_payload.append(rec.to_dict())

        for ota_name, fare_records in ota_res.items():
            for rec in fare_records:
                raw_fares_payload.append(rec.to_dict())

        logger.info(f"📊 [MASTER HARVEST] Collected {len(raw_fares_payload)} total raw fare observations.")

        # Step 3: Stream payload into Ingestion Pipeline
        db = mongo_db.db
        if db is None:
            await mongo_db.connect_db()
            db = mongo_db.db

        engine = DataIngestionEngine(db)
        ingestion_report = await engine.run_complete_ingestion(raw_fares_payload)

        # Step 4: Clear stale Redis caches
        try:
            await redis_cache.invalidate_all()
        except Exception:
            pass

        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        return {
            "status": "success",
            "execution_time_seconds": round(duration, 2),
            "sources_scraped": {
                "airlines": list(airline_res.keys()),
                "otas": list(ota_res.keys()),
            },
            "total_fares_harvested": len(raw_fares_payload),
            "ingestion_summary": ingestion_report,
        }


master_orchestrator = MasterScraperOrchestrator()

__all__ = ["MasterScraperOrchestrator", "master_orchestrator"]