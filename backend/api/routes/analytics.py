from fastapi import APIRouter
from services.dgca_service import DGCAService

router = APIRouter(prefix="/api/analytics", tags=["Economic Analytics"])


@router.get("/lead-time-curve")
async def get_lead_time_elasticity():
    """Returns price elasticity curves across advance purchase windows."""
    return {
        "status": "success",
        "windows": [
            {"window": "T+1", "label": "1 Day Prior (Emergency)", "avg_fare": 7150, "relative_premium": "+48%"},
            {"window": "T+7", "label": "7 Days Prior", "avg_fare": 5420, "relative_premium": "+12%"},
            {"window": "T+15", "label": "15 Days Prior (Standard)", "avg_fare": 4850, "relative_premium": "0% (Baseline)"},
            {"window": "T+30", "label": "30 Days Prior", "avg_fare": 4400, "relative_premium": "-9%"},
            {"window": "T+45", "label": "45 Days Prior (Early Bird)", "avg_fare": 4150, "relative_premium": "-14%"}
        ]
    }


@router.get("/route-heatmap")
async def get_route_heatmap():
    """Returns route-wise volatility and traffic weights for interactive heatmaps."""
    routes = DGCAService.DGCA_ROUTE_BASKET
    weights = DGCAService.get_route_weights()

    data = []
    for r in routes:
        r_id = r["route_id"]
        data.append({
            "route_id": r_id,
            "origin": r["origin"],
            "destination": r["destination"],
            "traffic_weight": weights[r_id],
            "monthly_passengers": r["monthly_passengers"],
            "volatility_index": "High" if weights[r_id] > 0.15 else "Moderate",
            "avg_fare": 4800 if "DEL" in r_id else 3500
        })

    return {"status": "success", "routes": data}