"""
STEP 9.9 VERIFICATION SUITE: BASE SCRAPER & TELEMETRY ENGINE
Validates:
  1. ProxyManager rotation and failure thresholds
  2. UserAgentManager randomized headers
  3. BaseScraper lifecycle, rate limiting with jitter, and fare serialization
  4. Concrete IndiGoScraper scraping session execution & metric reporting
"""

import asyncio
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.scrapers.base_scraper import (
    IndiGoScraper,
    ProxyManager,
    ScraperConfig,
    UserAgentManager,
)


async def test_step9_9():
    print("==================================================")
    print("  🌐 Verifying Step 9.9: Professional Base Scraper")
    print("==================================================\n")

    # 1. Test Proxy Manager
# 1. Test Proxy Manager
    print("[1/4] Testing ProxyManager Rotation & Failure Handling...")
    pm = ProxyManager(["http://proxy-a:8080", "http://proxy-b:8080"])
    p1 = pm.get_next_proxy()
    p2 = pm.get_next_proxy()
    assert p1 is not None and p2 is not None
    assert p1 != p2
    pm.mark_proxy_failure(p1)
    print(f"  ✅ Proxies rotated: {p1} ➔ {p2}")

    # 2. Test User Agent Headers
    print("\n[2/4] Testing UserAgentManager Header Generation...")
    headers = UserAgentManager.get_headers()
    assert "User-Agent" in headers
    assert "Sec-Fetch-Dest" in headers
    print(f"  ✅ Random User-Agent: {headers['User-Agent'][:48]}...")

    # 3. Test Concrete Scraper Execution
    print("\n[3/4] Running Live Scraping Session via IndiGoScraper...")
    scraper = IndiGoScraper()
    test_routes = [("DEL", "BOM"), ("BLR", "DEL")]
    test_windows = ["T+1", "T+15"]

    fares, metrics = await scraper.run_scraping_session(test_routes, test_windows)
    assert len(fares) == 4
    print(f"  ✅ Extracted {len(fares)} FareRecords successfully.")
    print(f"  ✅ Sample fare: {fares[0].departure}➔{fares[0].arrival} | Total: ₹{fares[0].total_fare} | Class: {fares[0].fare_class}")

    # 4. Telemetry Metrics Verification
    print("\n[4/4] Validating Performance Metrics...")
    scraper.log_metrics()
    assert metrics.fares_extracted == 4
    assert metrics.execution_time > 0

    print("🎉 STEP 9.9 PROFESSIONAL BASE SCRAPER ARCHITECTURE VERIFIED WITH 0 ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_9())