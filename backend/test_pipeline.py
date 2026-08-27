import asyncio
from scrapers.indigo_scraper import IndigoScraper
from services.data_cleaner import DataCleaner
from services.index_calculator import APIxIndexEngine


async def run_pipeline_test():
    print("\n==================================================")
    print("  Phase 4: Full Pipeline & APIx Index Engine Test ")
    print("==================================================")

    # 1. Scraping Simulation across multiple routes
    scraper = IndigoScraper()
    raw_data = []

    routes_to_test = [("DEL", "BOM"), ("BLR", "DEL"), ("BOM", "BLR")]
    for orig, dest in routes_to_test:
        fares = await scraper.scrape_advance_windows(orig, dest, windows=[1, 7, 15, 30])
        raw_data.extend(fares)

    print(f"\n[1] Raw Data Ingested: {len(raw_data)} records.")

    # 2. Cleaning & Outlier Removal
    cleaned_data = DataCleaner.clean_fare_batch(raw_data)
    print(f"[2] Cleaned Data Retained: {len(cleaned_data)} records.")

    # 3. Calculate Real-Time APIx Index
    index_result = APIxIndexEngine.calculate_daily_apix(cleaned_data)
    print("\n[3] Calculated Real-time Airfare Price Index (APIx):")
    print(f"    • Index Date: {index_result['date']}")
    print(f"    • APIx Score: {index_result['index_value']} (Base = {index_result['base_index']})")
    print(f"    • Data Points Processed: {index_result['data_points']}")
    print(f"    • Status: {index_result['status']}")
    print("==================================================\n")


if __name__ == "__main__":
    asyncio.run(run_pipeline_test())