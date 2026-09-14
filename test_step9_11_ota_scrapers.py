"""
STEP 9.11 VERIFICATION SUITE: OTA & AGGREGATOR SCRAPERS
Validates:
  1. EaseMyTrip, MakeMyTrip, and Yatra scrapers
  2. Aggregated multi-carrier fare extraction
  3. Parallel OTAScrapeOrchestrator execution & metric tracking
"""

import asyncio
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.scrapers.ota_scrapers import (
    EaseMyTripScraper,
    MakeMyTripScraper,
    OTAScrapeOrchestrator,
    YatraScraper,
)


async def test_step9_11():
    print("==================================================")
    print("  🏨 Verifying Step 9.11: OTA Scrapers Engine")
    print("==================================================\n")

    test_routes = [("DEL", "BOM"), ("BLR", "DEL")]
    test_windows = ["T+1", "T+15"]

    # 1. Test EaseMyTrip Scraper
    print("[1/3] Testing EaseMyTrip Scraper...")
    emt = EaseMyTripScraper()
    emt_fares, _ = await emt.run_scraping_session(test_routes, test_windows)
    assert len(emt_fares) == 4
    print(f"  ✅ EaseMyTrip extracted {len(emt_fares)} fares | Sample: {emt_fares[0].airline} {emt_fares[0].flight_number} (₹{emt_fares[0].total_fare})")

    # 2. Test MakeMyTrip & Yatra Scrapers
    print("\n[2/3] Testing MakeMyTrip & Yatra Scrapers...")
    mmt = MakeMyTripScraper()
    yatra = YatraScraper()
    mmt_fares, _ = await mmt.run_scraping_session(test_routes, test_windows)
    yatra_fares, _ = await yatra.run_scraping_session(test_routes, test_windows)
    assert len(mmt_fares) == 4
    assert len(yatra_fares) == 4
    print(f"  ✅ MakeMyTrip extracted {len(mmt_fares)} fares | Sample: {mmt_fares[0].airline} (₹{mmt_fares[0].total_fare})")
    print(f"  ✅ Yatra extracted {len(yatra_fares)} fares | Sample: {yatra_fares[0].airline} (₹{yatra_fares[0].total_fare})")

    # 3. Test Full Parallel OTA Orchestrator
    print("\n[3/3] Running Parallel OTAScrapeOrchestrator across all 3 OTAs...")
    orchestrator = OTAScrapeOrchestrator()
    results = await orchestrator.scrape_all(test_routes, test_windows)

    total_collected = sum(len(f) for f in results.values())
    assert total_collected == 12
    print(f"  ✅ Orchestrator harvested {total_collected} total fares across {len(results)} OTAs:")
    for ota_name, fares in results.items():
        print(f"     ➔ [{ota_name}] {len(fares)} fares extracted")

    print("\n🎉 STEP 9.11 OTA & AGGREGATOR SCRAPERS VERIFIED WITH 0 ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_11())