import asyncio
import logging
from datetime import datetime
from services.dgca_service import DGCAService
from services.data_cleaner import DataCleaner
from services.index_calculator import index_engine
from services.mongo_service import mongo_db
from scrapers.indigo_scraper import IndigoScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIxScheduler")


async def execute_nightly_batch_run():
    """
    Automated high-frequency scraping, processing, and indexing pipeline.
    Runs across primary DGCA domestic corridors.
    """
    logger.info(f"Starting scheduled automated batch cycle at {datetime.utcnow().isoformat()}...")
    scraper = IndigoScraper()
    raw_harvest = []

    # Selected top representative high-density pairs
    routes = DGCAService.DGCA_ROUTE_BASKET[:4]
    windows = [1, 7, 15, 30, 45]

    for r in routes:
        fares = await scraper.scrape_advance_windows(
            route_from=r["origin"],
            route_to=r["destination"],
            windows=windows
        )
        raw_harvest.extend(fares)

    # 1. Raw Telemetry Storage
    if raw_harvest:
        mongo_db.insert_raw_fares(raw_harvest)
        logger.info(f"Saved {len(raw_harvest)} raw fare points to MongoDB.")

    # 2. Outlier Removal & Cleaning
    cleaned_records = DataCleaner.clean_fare_batch(raw_harvest)
    if cleaned_records:
        mongo_db.insert_cleaned_fares(cleaned_records)
        logger.info(f"Cleaned and retained {len(cleaned_records)} validated fares.")

    # 3. Dynamic Index Computation
    daily_apix = index_engine.calculate_daily_index(cleaned_records, datetime.utcnow())
    logger.info(
        f"Batch Run Finished -> Index Value: {daily_apix['index_value']} | "
        f"Quality Score: {daily_apix['data_quality_score']} | "
        f"95% CI: [{daily_apix['lower_ci']}, {daily_apix['upper_ci']}]"
    )

    return daily_apix


if __name__ == "__main__":
    mongo_db.connect()
    asyncio.run(execute_nightly_batch_run())
 