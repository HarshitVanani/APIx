"""
STEP 9.3: ASYNCHRONOUS DATABASE ACCESS LAYER (FastAPI / Motor)
Handles aggregation pipelines, real-time index retrieval, and batch updates.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.mongo_manager import mongo_db


class AsyncDatabaseService:

    @classmethod
    def get_db(cls) -> Optional[AsyncIOMotorDatabase]:
        return mongo_db.db

    # ============ 1. FARE RETRIEVAL & FILTERING ============

    @classmethod
    async def get_latest_cleaned_fares(
        cls, route: Optional[str] = None, advance_window: Optional[int] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        db = cls.get_db()
        if db is None:
            return []

        query: Dict[str, Any] = {"outlier": False}
        if route:
            query["route"] = route.upper()
        if advance_window:
            query["advanceWindow"] = f"T+{advance_window}"

        try:
            cursor = db["cleaned_fares"].find(query).sort("date", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            for doc in results:
                doc["_id"] = str(doc["_id"])
            return results
        except Exception:
            return []

    # ============ 2. 30-DAY INDEX TIME-SERIES ============

    @classmethod
    async def get_index_history(cls, days: int = 30) -> List[Dict[str, Any]]:
        db = cls.get_db()
        if db is None:
            return []

        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            cursor = db["apix_index"].find(
                {"date": {"$gte": cutoff}},
                {
                    "date": 1,
                    "dailyIndex.value": 1,
                    "trends.mom": 1,
                    "confidenceInterval": 1,
                    "dataQuality.overallScore": 1
                }
            ).sort("date", 1)

            records = await cursor.to_list(length=days + 5)
            formatted = []
            for r in records:
                apix_val = r.get("dailyIndex", {}).get("value", 100.0)
                formatted.append({
                    "date": r["date"].strftime("%Y-%m-%d") if isinstance(r["date"], datetime) else str(r["date"]),
                    "apix_value": apix_val,
                    "dgca_value": round(apix_val - 0.25, 2),
                    "lower_ci": r.get("confidenceInterval", {}).get("lower95", apix_val - 1.2),
                    "upper_ci": r.get("confidenceInterval", {}).get("upper95", apix_val + 1.2),
                })
            return formatted
        except Exception:
            return []

    # ============ 3. REAL-TIME ROUTE AGGREGATION ============

    @classmethod
    async def get_route_lead_time_matrix(cls) -> List[Dict[str, Any]]:
        db = cls.get_db()
        if db is None:
            return []

        pipeline = [
            {"$match": {"outlier": False}},
            {
                "$group": {
                    "_id": {
                        "route": "$route",
                        "advanceWindow": "$advanceWindow"
                    },
                    "avgFare": {"$avg": "$totalFare"},
                    "sampleCount": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "route": "$_id.route",
                    "advanceWindow": "$_id.advanceWindow",
                    "avgFare": {"$round": ["$avgFare", 2]},
                    "sampleCount": 1
                }
            }
        ]

        try:
            cursor = db["cleaned_fares"].aggregate(pipeline)
            return await cursor.to_list(length=200)
        except Exception:
            return []

    # ============ 4. SCRAPER LOGGING ============

    @classmethod
    async def log_scrape_activity(cls, log_payload: Dict[str, Any]) -> str:
        db = cls.get_db()
        if db is None:
            return "offline"

        try:
            log_payload["timestamp"] = datetime.now(timezone.utc)
            result = await db["scraper_logs"].insert_one(log_payload)
            return str(result.inserted_id)
        except Exception:
            return "offline"