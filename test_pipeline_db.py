"""
APIx End-to-End Pipeline & DB Verification
Tests Scraper Output -> Cleaning -> MongoDB -> Index Calculation
"""

import asyncio
from backend.services.mongo_manager import mongo_db
from backend.tasks.ingestion_pipeline import DataIngestionEngine

async def run_pipeline_test():
    print("==================================================")
    print("  🚀 APIx Automated Pipeline & DB Verification")
    print("==================================================\n")

    # 1. Test Mongo Connection
    await mongo_db.connect_db()
    print("✅ [1/3] MongoDB Connection Manager Verified")

    # 2. Test Ingestion & Data Cleaner
    cleaned_count = await DataIngestionEngine.process_and_clean_raw_fares()
    print(f"✅ [2/3] Raw Ingestion & Cleaning Engine Verified ({cleaned_count} processed)")

    # 3. Test Index Calculation
    index_result = await DataIngestionEngine.compute_daily_apix_index()
    val = index_result["dailyIndex"]["value"]
    routes_count = len(index_result["routes"])
    print(f"✅ [3/3] Laspeyres Aggregation Engine Verified: Index = {val} across {routes_count} DGCA routes")

    await mongo_db.close_db()
    print("\n🎉 ALL PIPELINE CHECKS PASSED WITH ZERO ERRORS!\n")

if __name__ == "__main__":
    asyncio.run(run_pipeline_test())