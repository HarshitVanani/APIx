import asyncio
from scrapers.indigo_scraper import IndigoScraper


async def test_run():
    print("\n==================================================")
    print("  APIx Scraper Engine Pilot Test (IndiGo Module)  ")
    print("==================================================")
    scraper = IndigoScraper()
    
    # Test multi-window scraping for representative DGCA route (DEL -> BOM)
    results = await scraper.scrape_advance_windows(
        route_from="DEL",
        route_to="BOM",
        windows=[1, 7, 15]
    )

    print(f"\nSuccessfully collected {len(results)} multi-window fare records:")
    for idx, fare in enumerate(results, 1):
        print(f"  [{idx}] T+{fare['advance_window']} Day | Route: {fare['route_from']}->{fare['route_to']} | Airline: {fare['airline']} | Total: ₹{fare['total_price']} (Base: ₹{fare['fare_price']})")
    print("==================================================\n")


if __name__ == "__main__":
    asyncio.run(test_run())