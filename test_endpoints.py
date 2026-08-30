import requests

BASE_URL = "http://localhost:8000"

endpoints = [
    ("GET", "/api/health"),
    ("GET", "/api/index/realtime"),
    ("GET", "/api/index/history?days=30"),
    ("GET", "/api/fares/latest"),
    ("GET", "/api/analytics/lead-time-curve"),
    ("GET", "/api/export/csv"),
]

print("=== Running APIx Endpoint Verification ===\n")
for method, path in endpoints:
    url = f"{BASE_URL}{path}"
    try:
        res = requests.request(method, url, timeout=5)
        status = "PASSED" if res.status_code == 200 else f"FAILED ({res.status_code})"
        print(f"[{status}] {method} {path} -> {res.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[FAILED] {method} {path} -> Connection Refused (Is backend running on port 8000?)")

print("\nVerification Complete.")