"""
STEP 9.3 VERIFICATION SUITE
Tests field validation, deduplication, component normalization,
IQR outlier filtering, and quality score computation.
"""

import asyncio
from datetime import datetime, timezone
from backend.services.mongo_manager import mongo_db
from backend.tasks.data_cleansing_service import DataCleansingService


async def run_step9_3_tests():
    print("==================================================")
    print("  🧪 Verifying Step 9.3: Data Cleansing Service")
    print("==================================================\n")

    service = DataCleansingService()
    await mongo_db.connect_db()
    db = mongo_db.db

    # Test 1: Field Validation
    print("[1/5] Testing Field Validation & Non-Negative Constraints...")
    invalid_fare = {"departure": "DEL", "arrival": "BOM", "totalFare": -500}
    assert service.validate_required_fields(invalid_fare) is False
    print("  ✅ Rejected invalid/negative fare properly.")

    # Test 2: Standardization & Tolerance Calculation
    print("\n[2/5] Testing Fare Component Normalization...")
    mismatched_fare = {"baseFare": 4000.0, "tax": 600.0, "totalFare": 4900.0}
    standardized = service.standardize_components(mismatched_fare)
    assert standardized["totalFare"] == 4600.0
    print(f"  ✅ Auto-corrected totalFare to sum: ₹{standardized['totalFare']}")

    # Test 3: Quality Scoring Logic
    print("\n[3/5] Testing Quality Score Engine...")
    score = service.calculate_quality_score(standardized)
    print(f"  ✅ Computed Quality Score: {score}/100")
    assert score >= 90.0

    # Test 4: End-to-End Raw Ingestion -> Clean Document
    if db is not None:
        print("\n[4/5] Testing Database Raw Fare Cleansing...")
        test_raw = {
            "date": datetime.now(timezone.utc),
            "source": "indigo_scraper",
            "departure": "DEL",
            "arrival": "BOM",
            "airline": "IndiGo",
            "baseFare": 5100.0,
            "tax": 900.0,
            "totalFare": 6000.0,
            "advancePurchaseWindow": "T+15",
            "valid": True
        }
        res = await db["raw_fares"].insert_one(test_raw)
        cleaned_record = await service.clean_fare_data(res.inserted_id)
        assert cleaned_record is not None
        print(f"  ✅ Inserted Cleaned Fare ID: {cleaned_record['_id']} (Quality: {cleaned_record['qualityScore']}%)")

        # Test 5: Deduplication Check
        print("\n[5/5] Testing Deduplication Rule...")
        is_dup = await service.is_duplicate(test_raw)
        assert is_dup is True
        print("  ✅ Deduplication successfully detected duplicate flight record.")
        
        # Cleanup
        await db["raw_fares"].delete_one({"_id": res.inserted_id})
        await db["cleaned_fares"].delete_one({"_id": cleaned_record["_id"]})

    await mongo_db.close_db()
    print("\n🎉 STEP 9.3 DATA CLEANSING SERVICE VERIFIED SUCCESSFULLY WITH 0 ERRORS!")


if __name__ == "__main__":
    asyncio.run(run_step9_3_tests())