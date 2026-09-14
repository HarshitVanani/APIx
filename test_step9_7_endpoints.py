"""
STEP 9.7 VERIFICATION SUITE
Tests FastAPI endpoints: Auth, Latest Index, Historical Series,
Route Analytics, Lead-Time Curves, CSV Export, and Health Probe.
"""

import asyncio
import httpx
from backend.api.main import app


async def test_step9_7_api():
    print("==================================================")
    print("  🧪 Verifying Step 9.7: Complete FastAPI Backend")
    print("==================================================\n")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Health Probe
        print("[1/7] Testing Health Check /api/health...")
        res = await client.get("/api/health")
        assert res.status_code == 200
        print(f"  ✅ Health Check: {res.json()['status']}")

        # 2. Authentication Login
        print("\n[2/7] Testing JWT Auth /api/auth/login...")
        res = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        assert res.status_code == 200
        token = res.json()["access_token"]
        print(f"  ✅ JWT Generated: {token[:24]}...")

        # 3. Latest Index
        print("\n[3/7] Testing Latest Index /api/index/latest...")
        res = await client.get("/api/index/latest")
        assert res.status_code == 200
        print(f"  ✅ Latest Index Value: {res.json().get('index_value') or res.json().get('current_index')}")

        # 4. Historical Index Series
        print("\n[4/7] Testing Historical Series /api/index/historical?days=7...")
        res = await client.get("/api/index/historical?days=7")
        assert res.status_code == 200
        print(f"  ✅ Historical Series Data Points: {res.json()['count']}")

        # 5. Lead-Time Elasticity Curve
        print("\n[5/7] Testing Lead-Time Curve /api/analytics/lead-time-curve...")
        res = await client.get("/api/analytics/lead-time-curve")
        assert res.status_code == 200
        print(f"  ✅ Advance Windows Returned: {len(res.json()['windows'])} windows")

        # 6. Route Heatmap
        print("\n[6/7] Testing Route Heatmap /api/analytics/route-heatmap...")
        res = await client.get("/api/analytics/route-heatmap")
        assert res.status_code == 200
        print(f"  ✅ Basket Routes Tracked: {len(res.json()['routes'])} routes")

        # 7. CSV Streaming Export
        print("\n[7/7] Testing CSV Export /api/export/csv...")
        res = await client.get("/api/export/csv")
        assert res.status_code == 200
        assert "Date,Route,Airline" in res.text
        print("  ✅ CSV Stream generated and verified.")

    print("\n🎉 STEP 9.7 FASTAPI ENDPOINTS FULLY VERIFIED WITH 0 ERRORS!")


if __name__ == "__main__":
    asyncio.run(test_step9_7_api())