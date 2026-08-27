from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from services.dgca_service import DGCAService

router = APIRouter(prefix="/api/fares", tags=["Fares Telemetry"])


@router.get("/latest")
async def get_latest_fares(
    route: Optional[str] = Query(None, description="Filter by Route ID (e.g. DEL-BOM)"),
    advance_window: Optional[int] = Query(None, description="Filter by Lead Window (1, 7, 15, 30, 45)"),
    airline: Optional[str] = Query(None, description="Filter by Airline")
):
    """Retrieve filtered fare stream."""
    sample_fares = [
        {"route_id": "DEL-BOM", "airline": "IndiGo", "advance_window": 1, "total_price": 6850.0, "base_fare": 5822.5, "tax": 685.0, "fees": 342.5, "dep_date": "2026-08-26"},
        {"route_id": "DEL-BOM", "airline": "IndiGo", "advance_window": 7, "total_price": 5400.0, "base_fare": 4590.0, "tax": 540.0, "fees": 270.0, "dep_date": "2026-09-01"},
        {"route_id": "DEL-BOM", "airline": "IndiGo", "advance_window": 15, "total_price": 4900.0, "base_fare": 4165.0, "tax": 490.0, "fees": 245.0, "dep_date": "2026-09-09"},
        {"route_id": "DEL-BOM", "airline": "IndiGo", "advance_window": 30, "total_price": 4500.0, "base_fare": 3825.0, "tax": 450.0, "fees": 225.0, "dep_date": "2026-09-24"},
        {"route_id": "BLR-DEL", "airline": "IndiGo", "advance_window": 7, "total_price": 5600.0, "base_fare": 4760.0, "tax": 560.0, "fees": 280.0, "dep_date": "2026-09-01"},
        {"route_id": "BOM-BLR", "airline": "IndiGo", "advance_window": 15, "total_price": 3800.0, "base_fare": 3230.0, "tax": 380.0, "fees": 190.0, "dep_date": "2026-09-09"},
    ]

    filtered = sample_fares
    if route:
        filtered = [f for f in filtered if f["route_id"] == route.upper()]
    if advance_window:
        filtered = [f for f in filtered if f["advance_window"] == advance_window]
    if airline:
        filtered = [f for f in filtered if f["airline"].lower() == airline.lower()]

    return {
        "status": "success",
        "total_records": len(filtered),
        "data": filtered
    }