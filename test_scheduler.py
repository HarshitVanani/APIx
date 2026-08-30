"""
APIx Task Scheduler Verification
Tests one automated scrape -> clean -> DB persist -> index calculate cycle.
"""

import asyncio
from backend.services.mongo_manager import mongo_db
from backend.tasks.scheduler import APITaskScheduler


async def test_scheduler_cycle():
    print("==================================================")
    print("  🚀 Testing APIx Scheduled Harvesting Cycle")
    print("==================================================\n")

    # Connect to MongoDB
    await mongo_db.connect_db()

    # Run single execution of the telemetry cycle
    result = await APITaskScheduler.run_harvest_and_compute_cycle()

    print("\n--- Execution Summary ---")
    print(f"• Timestamp: {result['timestamp']}")
    print(f"• Raw Fares Harvested: {result['raw_collected']}")
    print(f"• Cleaned Fares Stored: {result['cleaned_processed']}")
    print(f"• New APIx Index Value: {result['apix_index']}")

    await mongo_db.close_db()
    print("\n🎉 Automated scheduler cycle executed with 0 errors!")


if __name__ == "__main__":
    asyncio.run(test_scheduler_cycle())