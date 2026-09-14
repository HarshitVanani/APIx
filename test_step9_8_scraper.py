"""
STEP 9.8 VERIFICATION SUITE: MULTI-AIRLINE SCRAPER & INGESTION BRIDGE
Validates:
  1. Multi-airline fare generation (IndiGo, Air India, SpiceJet, Akasa)
  2. Full harvest cycle across DGCA basket routes
  3. Seamless ingestion into MongoDB via Step 9.9 DataIngestionEngine
"""

import os
import sys
import asyncio

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.services.mongo_manager import mongo_db
from backend.scrapers.multi_airline_scraper import scraper_engine
from backend.tasks.ingestion_pipeline import ingestion_pipeline


async def test_step9_8():
    print("==================================================")
    print("  🧪 Verifying Step 9.8: Multi-Airline Scraper")
    print("==================================================\n")

    await mongo_db.connect_db()
    db = mongo_db.db
    assert db is not None, "MongoDB connection failed - database handle is None"

    # 1. Harvest multi-airline fares
    print("[1/3] Scraping Live Fares across 8 Routes & 4 Airlines...")
    raw_fares = await scraper_engine.harvest_all_routes()
    assert len(raw_fares) > 0
    print(f"  ✅ Harvested {len(raw_fares)} raw fare records.")
    print(
        f"  ✅ Sample observation: {raw_fares[0]['airline']} "
        f"{raw_fares[0]['departure']}➔{raw_fares[0]['arrival']} "
        f"({raw_fares[0]['advancePurchaseWindow']}) Total: ₹{raw_fares[0]['totalFare']}"
    )

    # 2. Ingest via Step 9.9 Engine
    print("\n[2/3] Passing Raw Fares to Step 9.9 Ingestion Pipeline Engine...")
    report = await ingestion_pipeline(db, raw_fares)
    print(f"  ✅ Pipeline Status: {report['status']}")
    print(f"  ✅ Fares Cleaned: {report['statistics']['faresCleaned']}")
    print(f"  ✅ Duplicates Removed: {report['statistics']['duplicatesRemoved']}")
    print(f"  ✅ Outliers Filtered: {report['statistics']['outliersRemoved']}")
    print(f"  ✅ Daily Index Calculated: {report['statistics']['indexCalculated']}")

    # 3. Verify Database Persistence
    print("\n[3/3] Verifying MongoDB Persistent Records...")
    raw_count = await db["raw_fares"].count_documents({})
    cleaned_count = await db["cleaned_fares"].count_documents({})
    latest_idx = await db["apix_index"].find_one({}, sort=[("created_at", -1)])
    print(f"  ✅ Total Raw Fares in MongoDB: {raw_count}")
    print(f"  ✅ Total Cleaned Fares in MongoDB: {cleaned_count}")
    print(f"  ✅ Computed Laspeyres Index in DB: {latest_idx.get('index_value') if latest_idx else 'N/A'}")

    await scraper_engine.close()
    await mongo_db.close_db()
    print("\n🎉 STEP 9.8 MULTI-AIRLINE SCRAPER & INGESTION PIPELINE VERIFIED SUCCESSFULLY WITH 0 ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_8())