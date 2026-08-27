import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats
from enum import Enum
from .dgca_service import DGCAService

logger = logging.getLogger("APIxEngine")


class IndexType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class APIxCalculationEngine:
    """
    Advanced statistical index calculation engine for APIx (Airfare Price Index).
    
    Methodology:
    1. Weighted average fare calculation using DGCA traffic weights
    2. Base period indexation (Base 100 = reference period)
    3. Confidence interval calculation using bootstrap resampling
    4. Trend analysis (MoM, YoY, 90-day volatility)
    5. Multi-factor data quality scoring (Volume, Diversity, Consistency)
    """

    BASE_INDEX_VALUE = 100.0
    BASE_PERIOD = "2023-12"
    MIN_DATA_POINTS = 3

    # Calibrated baseline route averages
    DEFAULT_BASE_FARES = {
        "DEL-BOM": 4800.0,
        "BOM-DEL": 4750.0,
        "BLR-DEL": 5200.0,
        "DEL-BLR": 5150.0,
        "BOM-BLR": 3600.0,
        "DEL-CCU": 4900.0,
        "BOM-GOI": 3200.0,
        "DEL-HYD": 4100.0,
    }

    def __init__(self, route_weights: Optional[Dict[str, float]] = None):
        self.route_weights = route_weights or DGCAService.get_route_weights()
        self.base_fare_level = self.DEFAULT_BASE_FARES.copy()

    def set_base_fare_level(self, base_fares: List[Dict]):
        """Set baseline fare level from historical reference records."""
        base_df = pd.DataFrame(base_fares)
        route_baselines = {}

        for route_id in self.route_weights.keys():
            orig, dest = route_id.split("-") if "-" in route_id else (route_id[:3], route_id[3:])
            route_data = base_df[
                ((base_df.get('route_from') == orig) & (base_df.get('route_to') == dest)) |
                (base_df.get('route_id') == route_id)
            ]

            if len(route_data) > 0:
                route_baselines[route_id] = float(route_data['total_price'].mean())
            else:
                route_baselines[route_id] = self.DEFAULT_BASE_FARES.get(route_id, 4500.0)

        self.base_fare_level = route_baselines

    def calculate_daily_index(self, daily_fares: List[Dict], date: Optional[datetime] = None) -> Dict:
        calc_date = date or datetime.utcnow()

        if not daily_fares or len(daily_fares) < self.MIN_DATA_POINTS:
            logger.warning(f"Insufficient data for {calc_date}: {len(daily_fares)} points")
            return self._null_index(calc_date, "daily")

        df = pd.DataFrame(daily_fares)

        if "route_from" not in df.columns or "route_to" not in df.columns:
            if "route_id" in df.columns:
                df[["route_from", "route_to"]] = df["route_id"].str.split("-", expand=True)

        route_groups = df.groupby(['route_from', 'route_to'])
        weighted_fares = []
        routes_included = []
        route_stats = {}

        for (route_from, route_to), group in route_groups:
            route_id = f"{route_from}-{route_to}".upper()
            routes_included.append(route_id)

            weight = self.route_weights.get(route_id, 0.05)
            avg_fare = float(group['total_price'].mean())
            weighted_fares.append(avg_fare * weight)

            route_stats[route_id] = {
                "avg_fare": round(avg_fare, 2),
                "count": int(len(group)),
                "std": round(float(group['total_price'].std()), 2) if len(group) > 1 else 0.0,
                "min": float(group['total_price'].min()),
                "max": float(group['total_price'].max()),
                "weight": weight
            }

        weighted_avg_fare = sum(weighted_fares)

        base_weighted = sum(
            self.base_fare_level.get(r_id, 4500.0) * self.route_weights.get(r_id, 0.05)
            for r_id in routes_included
        )

        index_value = (weighted_avg_fare / base_weighted * 100.0) if base_weighted > 0 else 100.0

        lower_ci, upper_ci, std_error = self._calculate_confidence_interval(df, routes_included)
        quality_score = self._calculate_quality_score(len(df), len(routes_included), std_error, weighted_avg_fare)

        return {
            "date": calc_date.strftime("%Y-%m-%d"),
            "index_value": round(float(index_value), 2),
            "index_type": "daily",
            "routes_included": routes_included,
            "data_points": int(len(df)),
            "routes_count": int(len(route_groups)),
            "weighted_avg_fare": round(float(weighted_avg_fare), 2),
            "lower_ci": round(float(lower_ci), 2),
            "upper_ci": round(float(upper_ci), 2),
            "std_error": round(float(std_error), 2),
            "data_quality_score": round(float(quality_score), 3),
            "route_stats": route_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_confidence_interval(
        self, df: pd.DataFrame, routes_included: List[str], confidence: float = 0.95, n_bootstrap: int = 500
    ) -> Tuple[float, float, float]:
        prices = df['total_price'].values
        if len(prices) < 2:
            single = float(prices[0]) if len(prices) == 1 else 100.0
            return single, single, 0.0

        bootstrap_means = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(prices, size=len(prices), replace=True)
            bootstrap_means.append(np.mean(sample))

        lower_pct = (1.0 - confidence) / 2.0 * 100.0
        upper_pct = (1.0 + confidence) / 2.0 * 100.0

        return (
            float(np.percentile(bootstrap_means, lower_pct)),
            float(np.percentile(bootstrap_means, upper_pct)),
            float(np.std(bootstrap_means))
        )

    def _calculate_quality_score(
        self, data_points: int, routes_count: int, std_error: float, avg_fare: float
    ) -> float:
        volume_score = min(data_points / 20.0, 1.0) * 0.4
        expected_routes = max(len(self.route_weights), 1)
        route_score = min(routes_count / expected_routes, 1.0) * 0.3
        consistency_score = max(1.0 - (std_error / avg_fare if avg_fare > 0 else 1.0), 0.0) * 0.2
        return min(volume_score + route_score + consistency_score + 0.1, 1.0)

    def _null_index(self, date: datetime, index_type: str) -> Dict:
        return {
            "date": date.strftime("%Y-%m-%d"),
            "index_value": 100.0,
            "index_type": index_type,
            "routes_included": [],
            "data_points": 0,
            "data_quality_score": 0.0,
            "is_valid": False,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global calculation engine instance
index_engine = APIxCalculationEngine()