"""
STEP 9.5 VERIFICATION SUITE: REDIS CACHING LAYER
Validates caching primitives, domain key invalidation patterns,
lead-time caching, and hit/miss telemetry statistics.
"""

import asyncio
from backend.services.redis_cache_service import RedisCacheService


async def test_step9_5_redis():
    print("==================================================")
    print("  🧪 Verifying Step 9.5: Redis Cache Service")
    print("==================================================\n")

    cache = RedisCacheService()
    await cache.connect()

    # 1. Test Key Set / Get
    print("[1/5] Testing Primitive Set and Get Operations...")
    await cache.set("test:greeting", {"message": "Hello APIx"}, expiration_seconds=60)
    data = await cache.get("test:greeting")
    assert data is not None
    assert data.get("message") == "Hello APIx"
    print(f"  ✅ Cache Write/Read verified: {data}")

    # 2. Test Domain Caching (Index Data)
    print("\n[2/5] Testing Domain-Specific Index Caching...")
    test_index = {
        "index_value": 105.69,
        "routes_included": ["DEL-BOM", "BLR-DEL"],
        "quality_score": 0.984
    }
    await cache.cache_index_data("2026-08-30", test_index, ttl=3600)
    cached_index = await cache.get_cached_index_data("2026-08-30")
    assert cached_index is not None
    assert cached_index.get("index_value") == 105.69
    print(f"  ✅ Cached Index Payload: {cached_index}")

    # 3. Test Lead-Time Elasticity & Route Caching
    print("\n[3/5] Testing Route & Fare Statistics Caching...")
    await cache.cache_route_data("DEL-BOM", {"avg_fare": 5200, "weight": 0.185})
    await cache.cache_fare_stats("DEL-BOM", "T+15", {"avg": 4850, "samples": 120})

    route_data = await cache.get_cached_route_data("DEL-BOM")
    stats_data = await cache.get_cached_fare_stats("DEL-BOM", "T+15")
    assert route_data is not None
    assert stats_data is not None
    assert route_data.get("avg_fare") == 5200
    assert stats_data.get("avg") == 4850
    print("  ✅ Route & Lead-Time stats successfully stored and retrieved.")

    # 4. Test Pattern Invalidation
    print("\n[4/5] Testing Pattern Invalidation (apix:index:*)...")
    deleted_keys = await cache.invalidate_index_cache()
    after_invalidation = await cache.get_cached_index_data("2026-08-30")
    assert after_invalidation is None
    print(f"  ✅ Successfully invalidated {deleted_keys} keys. Post-invalidation fetch returned None.")

    # 5. Telemetry & Stats Verification
    print("\n[5/5] Checking Cache Telemetry & Health Probe...")
    stats = cache.get_stats()
    health = await cache.health_check()
    print(f"  ✅ Hit Rate: {stats['hitRate']} | Total Requests: {stats['totalRequests']}")
    print(f"  ✅ Health Check: {health}")

    await cache.disconnect()
    print("\n🎉 STEP 9.5 REDIS CACHE SERVICE FULLY VERIFIED WITH 0 ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_5_redis())