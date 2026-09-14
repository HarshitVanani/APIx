"""
STEP 9.3: DATA CLEANSING SERVICE
Production-Grade Data Validation, Normalization & Outlier Filtering
Handles:
  1. Mandatory field & range validation
  2. Time-windowed deduplication (1-hour tolerance)
  3. Base + Tax fare component standardization
  4. Statistical IQR outlier detection (Route + Advance Window)
  5. Multi-factor Quality Score calculation (0-100)
"""

import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId

# Ensure backend root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.mongo_manager import mongo_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DataCleansingService")


class DataCleansingService:
    def __init__(self):
        self.stats = {
            "totalProcessed": 0,
            "duplicatesRemoved": 0,
            "outliersRemoved": 0,
            "cleaned": 0,
            "failed": 0,
        }

    def reset_stats(self):
        self.stats = {
            "totalProcessed": 0,
            "duplicatesRemoved": 0,
            "outliersRemoved": 0,
            "cleaned": 0,
            "failed": 0,
        }

    # ============ 1. FIELD VALIDATION ============

    def validate_required_fields(self, fare: Dict[str, Any]) -> bool:
        required = [
            "date",
            "source",
            "departure",
            "arrival",
            "airline",
            "baseFare",
            "tax",
            "totalFare",
            "advancePurchaseWindow",
        ]

        for field in required:
            val = fare.get(field)
            if val is None or val == "":
                logger.warning(f"Missing required field '{field}' in doc {fare.get('_id')}")
                return False

        try:
            base = float(fare["baseFare"])
            tax = float(fare["tax"])
            total = float(fare["totalFare"])
            if base < 0 or tax < 0 or total < 0:
                logger.warning(f"Negative fare values detected in doc {fare.get('_id')}")
                return False
        except (ValueError, TypeError):
            logger.warning(f"Non-numeric fare detected in doc {fare.get('_id')}")
            return False

        return True

    # ============ 2. DEDUPLICATION ============

    async def is_duplicate(self, fare: Dict[str, Any]) -> bool:
        db = mongo_db.db
        if db is None:
            return False

        raw_date = fare.get("date")
        if isinstance(raw_date, str):
            try:
                raw_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            except ValueError:
                raw_date = datetime.now(timezone.utc)
        elif not isinstance(raw_date, datetime):
            raw_date = datetime.now(timezone.utc)

        route_id = f"{fare.get('departure')}-{fare.get('arrival')}".upper()
        advance_window = fare.get("advancePurchaseWindow")
        airline = fare.get("airline")

        time_min = raw_date - timedelta(hours=1)
        time_max = raw_date + timedelta(hours=1)

        existing = await db["cleaned_fares"].find_one({
            "route": route_id,
            "airline": airline,
            "advanceWindow": advance_window,
            "date": {"$gte": time_min, "$lte": time_max}
        })

        return existing is not None

    # ============ 3. COMPONENT STANDARDIZATION ============

    def standardize_components(self, fare: Dict[str, Any]) -> Dict[str, float]:
        base_fare = float(fare.get("baseFare", 0))
        tax = float(fare.get("tax", 0))
        surcharges = float(fare.get("surcharges", 0))
        total_fare = float(fare.get("totalFare", 0))

        calculated_total = base_fare + tax + surcharges
        tolerance = base_fare * 0.05

        if abs(total_fare - calculated_total) > tolerance:
            logger.warning(f"Fare component mismatch. Adjusting totalFare to calculated sum {calculated_total:.2f}")
            total_fare = calculated_total

        return {
            "baseFare": round(base_fare, 2),
            "tax": round(tax, 2),
            "totalFare": round(total_fare, 2),
        }

    # ============ 4. IQR OUTLIER DETECTION ============

    async def is_outlier(self, standardized: Dict[str, float], departure: str, arrival: str, advance_window: str) -> bool:
        db = mongo_db.db
        if db is None:
            return False

        route_id = f"{departure}-{arrival}".upper()

        cursor = db["cleaned_fares"].find(
            {"route": route_id, "advanceWindow": advance_window},
            {"totalFare": 1, "_id": 0}
        ).limit(100)

        historical = await cursor.to_list(length=100)

        if len(historical) < 10:
            return False  # Not enough statistical sample size

        prices = sorted([float(doc["totalFare"]) for doc in historical if "totalFare" in doc])
        if len(prices) < 10:
            return False

        q1_idx = int(len(prices) * 0.25)
        q3_idx = int(len(prices) * 0.75)
        q1 = prices[q1_idx]
        q3 = prices[q3_idx]
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        fare_val = standardized["totalFare"]
        outlier = (fare_val < lower_bound) or (fare_val > upper_bound)

        if outlier:
            logger.warning(f"Outlier detected for {route_id} ({advance_window}): ₹{fare_val} outside [{lower_bound:.2f}, {upper_bound:.2f}]")

        return outlier

    # ============ 5. QUALITY SCORE ============

    def calculate_quality_score(self, standardized: Dict[str, float]) -> float:
        score = 100.0
        base = standardized["baseFare"]
        tax = standardized["tax"]
        total = standardized["totalFare"]

        # Deduct for component mismatch > 2%
        if abs(total - (base + tax)) > (base * 0.02):
            score -= 5.0

        # Deduct for zero base or tax
        if base <= 0 or tax <= 0:
            score -= 10.0

        # Bonus for fully validated positive breakdown
        if base > 0 and tax > 0 and total > 0:
            score += 5.0

        return float(max(0.0, min(100.0, score)))

    # ============ MAIN PIPELINE ============

    async def clean_fare_data(self, raw_fare_id: Any) -> Optional[Dict[str, Any]]:
        db = mongo_db.db
        if db is None:
            logger.error("MongoDB not connected.")
            return None

        try:
            if isinstance(raw_fare_id, str):
                raw_fare_id = ObjectId(raw_fare_id)

            raw_fare = await db["raw_fares"].find_one({"_id": raw_fare_id})
            if not raw_fare:
                logger.error(f"Raw fare not found for ID: {raw_fare_id}")
                return None

            self.stats["totalProcessed"] += 1

            # Step 1: Validate
            if not self.validate_required_fields(raw_fare):
                await db["raw_fares"].update_one({"_id": raw_fare_id}, {"$set": {"valid": False}})
                self.stats["failed"] += 1
                return None

            # Step 2: Deduplicate
            if await self.is_duplicate(raw_fare):
                self.stats["duplicatesRemoved"] += 1
                return None

            # Step 3: Standardize
            std = self.standardize_components(raw_fare)

            # Step 4: Outlier Check
            if await self.is_outlier(
                std,
                raw_fare["departure"],
                raw_fare["arrival"],
                raw_fare["advancePurchaseWindow"]
            ):
                self.stats["outliersRemoved"] += 1
                return None

            # Step 5: Save Cleaned Record
            raw_date = raw_fare.get("date")
            if isinstance(raw_date, str):
                raw_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            elif not isinstance(raw_date, datetime):
                raw_date = datetime.now(timezone.utc)

            cleaned_doc = {
                "rawFareId": raw_fare["_id"],
                "route": f"{raw_fare['departure']}-{raw_fare['arrival']}".upper(),
                "baseFare": std["baseFare"],
                "tax": std["tax"],
                "totalFare": std["totalFare"],
                "advanceWindow": raw_fare["advancePurchaseWindow"],
                "airline": raw_fare["airline"],
                "source": raw_fare.get("source", "scraper"),
                "date": raw_date,
                "qualityScore": self.calculate_quality_score(std),
                "createdAt": datetime.now(timezone.utc)
            }

            result = await db["cleaned_fares"].insert_one(cleaned_doc)
            cleaned_doc["_id"] = result.inserted_id
            self.stats["cleaned"] += 1
            return cleaned_doc

        except Exception as e:
            logger.error(f"Error cleaning fare {raw_fare_id}: {e}")
            self.stats["failed"] += 1
            return None

    # ============ BATCH CLEANING ============

    async def clean_batch(self, limit: int = 100) -> Dict[str, Any]:
        db = mongo_db.db
        if db is None:
            return self.stats

        logger.info(f"Starting batch cleaning of up to {limit} raw fares...")
        cursor = db["raw_fares"].find({"valid": True}).limit(limit)
        raw_fares = await cursor.to_list(length=limit)

        processed = 0
        for fare in raw_fares:
            await self.clean_fare_data(fare["_id"])
            processed += 1
            if processed % 20 == 0:
                logger.info(f"Processed {processed}/{len(raw_fares)} fares")

        logger.info(f"Batch cleaning finished: {self.stats}")
        return self.stats

    # ============ REPORTING ============

    async def generate_report(self) -> Dict[str, Any]:
        db = mongo_db.db
        
        total = 0
        cleaned = 0
        if db is not None:
            total = await db["raw_fares"].count_documents({})
            cleaned = await db["cleaned_fares"].count_documents({})

        failed = max(0, total - cleaned)
        failure_rate = round((failed / total) * 100, 2) if total > 0 else 0.0

        recommendations = []
        if failure_rate > 10.0:
            recommendations.append("High failure rate detected. Review scraper payload conformity.")
        if self.stats["outliersRemoved"] > (self.stats["cleaned"] * 0.05 + 1):
            recommendations.append("High outlier proportion detected. Check for airline dynamic pricing surges.")
        if self.stats["duplicatesRemoved"] > (self.stats["cleaned"] * 0.1 + 1):
            recommendations.append("High duplicate rate. Adjust scraper ingestion frequency.")
        if not recommendations:
            recommendations.append("Data quality nominal. All IQR & schema checks passed.")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "totalProcessed": self.stats["totalProcessed"],
            "duplicatesRemoved": self.stats["duplicatesRemoved"],
            "outliersRemoved": self.stats["outliersRemoved"],
            "cleaned": self.stats["cleaned"],
            "failed": self.stats["failed"],
            "databaseStats": {
                "totalRawFares": total,
                "cleanedFares": cleaned,
                "failureRate": f"{failure_rate}%",
            },
            "recommendations": recommendations,
        }
    # Alias to match JavaScript casing
    def standardizeComponents(self, fare: Dict[str, Any]) -> Dict[str, float]:
        return self.standardize_components(fare)


data_cleansing_service = DataCleansingService()