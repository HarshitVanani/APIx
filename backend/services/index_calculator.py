import numpy as np
import pandas as pd
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger("APIx.IndexCalculator")


class AirfarePriceIndexEngine:
    """
    Computes the Stratified Jevons / Weighted Laspeyres Real-Time Airfare Index.
    Integrates advance purchase windows (T+1 to T+45) and DGCA route baskets.
    """

    # Advance purchase window weights (representative of domestic booking patterns)
    WINDOW_WEIGHTS = {
        1: 0.15,   # T+1: Emergency / Business Last-Minute
        7: 0.35,   # T+7: Short-term demand
        15: 0.25,  # T+15: Standard advance booking
        30: 0.15,  # T+30: Vacation / Planned
        45: 0.10,  # T+45: Early bird
    }

    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "apix_db"):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[db_name]

    async def calculate_daily_apix(self, target_date: datetime) -> dict:
        start_bound = datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=timezone.utc)
        end_bound = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=timezone.utc)

        cursor = self.db["raw_fares"].find({
            "scraped_at": {"$gte": start_bound, "$lte": end_bound}
        })
        records = await cursor.to_list(length=100000)

        if not records:
            logger.warning(f"No fare records found for {target_date.date()}. Aborting index calculation.")
            return {}

        df = pd.DataFrame(records)

        # 1. Outlier Removal via Route & Window Interquartile Range (IQR)
        cleaned_frames = []
        for (route, window), group in df.groupby(["origin_iata", "destination_iata", "advance_purchase_window"]):
            q1 = group["total_fare"].quantile(0.25)
            q3 = group["total_fare"].quantile(0.75)
            iqr = q3 - q1
            filtered = group[(group["total_fare"] >= q1 - 1.5 * iqr) & (group["total_fare"] <= q3 + 1.5 * iqr)]
            cleaned_frames.append(filtered)

        clean_df = pd.concat(cleaned_frames, ignore_index=True)

        # 2. Compute Stratified Geometric Means (Jevons Elementary Aggregates)
        strata_means = []
        for (origin, dest, window), group in clean_df.groupby(["origin_iata", "destination_iata", "advance_purchase_window"]):
            geom_mean = np.exp(np.log(group["total_fare"]).mean())
            strata_means.append({
                "route": f"{origin}-{dest}",
                "origin": origin,
                "destination": dest,
                "window": window,
                "geo_mean_fare": geom_mean,
                "sample_size": len(group)
            })

        strata_df = pd.DataFrame(strata_means)

        # 3. Retrieve DGCA Traffic Weights
        dgca_weights = {
            "DEL-BOM": 0.24, "BOM-DEL": 0.24,
            "DEL-BLR": 0.16, "BLR-DEL": 0.16,
            "BOM-BLR": 0.12, "DEL-CCU": 0.10,
            "DEL-HYD": 0.10, "BOM-MAA": 0.08,
            "DEL-AMD": 0.08, "BOM-GOI": 0.06
        }

        # 4. Weighted Aggregation Across Advance Windows & Routes
        route_indices = []
        for route_id, r_group in strata_df.groupby("route"):
            route_weighted_fare = 0.0
            total_window_wt = 0.0
            for _, row in r_group.iterrows():
                w = self.WINDOW_WEIGHTS.get(int(row["window"]), 0.1)
                route_weighted_fare += row["geo_mean_fare"] * w
                total_window_wt += w

            normalized_route_fare = route_weighted_fare / total_window_wt if total_window_wt > 0 else route_weighted_fare
            route_indices.append({
                "route": route_id,
                "composite_fare": normalized_route_fare,
                "dgca_weight": dgca_weights.get(route_id, 0.05)
            })

        composite_df = pd.DataFrame(route_indices)
        national_composite_fare = np.sum(composite_df["composite_fare"] * composite_df["dgca_weight"]) / np.sum(composite_df["dgca_weight"])

        # Base period calibration (Reference Fare = ₹4,850.00 base standard)
        BASE_CALIBRATION_PRICE = 4850.0
        apix_index_value = (national_composite_fare / BASE_CALIBRATION_PRICE) * 100.0

        result_payload = {
            "index_date": start_bound,
            "apix_value": round(float(apix_index_value), 2),
            "composite_price": round(float(national_composite_fare), 2),
            "total_data_points": len(clean_df),
            "routes_calculated": len(route_indices),
            "calculated_at": datetime.now(timezone.utc),
        }

        await self.db["index_history"].update_one(
            {"index_date": start_bound},
            {"$set": result_payload},
            upsert=True
        )

        logger.info(f"Calculated APIx for {target_date.date()}: {apix_index_value:.2f} (from {len(clean_df)} observations)")
        return result_payload 
        # Instantiate global singleton instance for imports
        index_engine = IndexCalculator()