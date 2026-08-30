import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from scrapers.engine.indigo import IndigoProductionScraper
from scrapers.engine.makemytrip import MakeMyTripProductionScraper
from scrapers.engine.base import RawFarePayload

logger = logging.getLogger("APIx.Orchestrator")

# Top DGCA Representative City-Pair Routes (Covering ~60% domestic passenger volume)
DGCA_BASKET_ROUTES = [
    {"origin": "DEL", "destination": "BOM", "weight": 0.12},
    {"origin": "BOM", "destination": "DEL", "weight": 0.12},
    {"origin": "DEL", "destination": "BLR", "weight": 0.08},
    {"origin": "BLR", "destination": "DEL", "weight": 0.08},
    {"origin": "BOM", "destination": "BLR", "weight": 0.06},
    {"origin": "DEL", "destination": "CCU", "weight": 0.05},
    {"origin": "DEL", "destination": "HYD", "weight": 0.05},
    {"origin": "BOM", "destination": "MAA", "weight": 0.04},
    {"origin": "DEL", "destination": "AMD", "weight": 0.04},
    {"origin": "BOM", "destination": "GOI", "weight": 0.03},
]

ADVANCE_PURCHASE_WINDOWS = [1, 7, 15, 30, 45]  # T+1 to T+45 advance purchase tiers


class ScrapingOrchestrationPipeline:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "apix_db"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]
        self.raw_collection = self.db["raw_fares"]
        self.indigo_engine = IndigoProductionScraper(concurrency_limit=2)
        self.mmt_engine = MakeMyTripProductionScraper(concurrency_limit=2)

    async def initialize_db_indexes(self):
        await self.raw_collection.create_index([("fare_id", 1)], unique=True)
        await self.raw_collection.create_index([("origin_iata", 1), ("destination_iata", 1)])
        await self.raw_collection.create_index([("advance_purchase_window", 1)])
        await self.raw_collection.create_index([("scraped_at", -1)])
        logger.info("Database compound indices verified.")

    async def execute_basket_cycle(self):
        await self.initialize_db_indexes()
        await self.indigo_engine.initialize_engine()
        await self.mmt_engine.initialize_engine()

        now = datetime.now(timezone.utc)
        logger.info(f"Starting APIx automated basket run across {len(DGCA_BASKET_ROUTES)} routes...")

        total_collected = 0

        for route in DGCA_BASKET_ROUTES:
            origin = route["origin"]
            dest = route["destination"]

            for window in ADVANCE_PURCHASE_WINDOWS:
                travel_date = now + timedelta(days=window)

                # Fetch concurrently across sources
                tasks = [
                    self.indigo_engine.fetch_route_fares(origin, dest, travel_date, window),
                    self.mmt_engine.fetch_route_fares(origin, dest, travel_date, window),
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)
                batch_records: List[RawFarePayload] = []

                for res in results:
                    if isinstance(res, list):
                        batch_records.extend(res)
                    elif isinstance(res, Exception):
                        logger.error(f"Task error on {origin}-{dest} (T+{window}): {res}")

                if batch_records:
                    inserted = await self._persist_records(batch_records)
                    total_collected += inserted

                # Rate limiting between city pairs
                await asyncio.sleep(1.5)

        await self.indigo_engine.close()
        await self.mmt_engine.close()
        logger.info(f"Scrape cycle complete. Successfully persisted {total_collected} unique fare records.")

    async def _persist_records(self, records: List[RawFarePayload]) -> int:
        bulk_ops = []
        for r in records:
            doc = r.model_dump()
            bulk_ops.append(
                UpdateOne(
                    {"fare_id": r.fare_id},
                    {"$set": doc},
                    upsert=True,
                )
            )

        if bulk_ops:
            result = await self.raw_collection.bulk_write(bulk_ops, ordered=False)
            return (result.upserted_count or 0) + (result.modified_count or 0)
        return 0


if __name__ == "__main__":
    pipeline = ScrapingOrchestrationPipeline()
    asyncio.run(pipeline.execute_basket_cycle())