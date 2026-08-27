import logging
from datetime import datetime
from typing import Dict, List
import numpy as np
import pandas as pd

logger = logging.getLogger("DataCleaner")


class DataCleaner:
    """Robust data sanitization and statistical outlier removal service."""

    @staticmethod
    def clean_fare_batch(raw_fares: List[Dict]) -> List[Dict]:
        if not raw_fares:
            return []

        df = pd.DataFrame(raw_fares)
        initial_len = len(df)

        # 1. Null / Missing Value Elimination
        critical_cols = ["route_from", "route_to", "total_price", "departure_date"]
        df = df.dropna(subset=critical_cols)

        # 2. Strict Boundary Checks (Prices between Rs 800 and Rs 80,000)
        df = df[(df["total_price"] >= 800.0) & (df["total_price"] <= 80000.0)]

        # 3. Deduplication (Same route, date, source & price)
        df = df.drop_duplicates(
            subset=["source", "route_from", "route_to", "departure_date", "total_price", "advance_window"],
            keep="first"
        )

        # 4. Statistical Outlier Removal using Interquartile Range (IQR) per route
        valid_indices = []
        for (r_from, r_to), group in df.groupby(["route_from", "route_to"]):
            if len(group) >= 4:
                q1 = group["total_price"].quantile(0.25)
                q3 = group["total_price"].quantile(0.75)
                iqr = q3 - q1
                lower_limit = q1 - (1.5 * iqr)
                upper_limit = q3 + (1.5 * iqr)
                inliers = group[(group["total_price"] >= lower_limit) & (group["total_price"] <= upper_limit)].index
                valid_indices.extend(inliers)
            else:
                valid_indices.extend(group.index)

        df = df.loc[valid_indices]

        # 5. Add route_id and standardized fields
        df["route_id"] = df["route_from"].str.upper() + "-" + df["route_to"].str.upper()
        df["cleaned_at"] = datetime.utcnow()

        cleaned_records = df.to_dict("records")
        logger.info(f"[DataCleaner] Processed {initial_len} records -> {len(cleaned_records)} high-integrity records.")
        return cleaned_records