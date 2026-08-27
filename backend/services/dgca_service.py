from typing import Dict, List


class DGCAService:
    """DGCA representative passenger-traffic basket and weight distributor."""

    # Top high-density domestic city pairs calibrated from official DGCA monthly reports
    DGCA_ROUTE_BASKET = [
        {"route_id": "DEL-BOM", "origin": "DEL", "destination": "BOM", "monthly_passengers": 485000},
        {"route_id": "BOM-DEL", "origin": "BOM", "destination": "DEL", "monthly_passengers": 480000},
        {"route_id": "BLR-DEL", "origin": "BLR", "destination": "DEL", "monthly_passengers": 320000},
        {"route_id": "DEL-BLR", "origin": "DEL", "destination": "BLR", "monthly_passengers": 315000},
        {"route_id": "BOM-BLR", "origin": "BOM", "destination": "BLR", "monthly_passengers": 260000},
        {"route_id": "DEL-CCU", "origin": "DEL", "destination": "CCU", "monthly_passengers": 220000},
        {"route_id": "BOM-GOI", "origin": "BOM", "destination": "GOI", "monthly_passengers": 195000},
        {"route_id": "DEL-HYD", "origin": "DEL", "destination": "HYD", "monthly_passengers": 210000},
    ]

    @classmethod
    def get_route_weights(cls) -> Dict[str, float]:
        """Calculates normalized statistical weights (sum = 1.0) based on passenger volume."""
        total_traffic = sum(item["monthly_passengers"] for item in cls.DGCA_ROUTE_BASKET)
        return {
            item["route_id"]: round(item["monthly_passengers"] / total_traffic, 4)
            for item in cls.DGCA_ROUTE_BASKET
        }

    @classmethod
    def get_tracked_routes(cls) -> List[str]:
        return [item["route_id"] for item in cls.DGCA_ROUTE_BASKET]