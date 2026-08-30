import json
import logging
from datetime import datetime
from typing import List
from playwright.async_api import Response
from .base import BaseAirfareEngine, RawFarePayload

logger = logging.getLogger("APIx.MakeMyTripEngine")


class MakeMyTripProductionScraper(BaseAirfareEngine):
    def __init__(self, concurrency_limit: int = 2, proxy: str = None):
        super().__init__(name="MakeMyTrip_OTA", concurrency_limit=concurrency_limit, proxy=proxy)

    async def fetch_route_fares(
        self, origin: str, destination: str, travel_date: datetime, advance_window: int
    ) -> List[RawFarePayload]:
        async with self.semaphore:
            context = await self.create_stealth_context()
            page = await context.new_page()
            results: List[RawFarePayload] = []
            captured_api_payloads = []

            async def capture_network(response: Response):
                try:
                    if "flightSearch" in response.url or "air-search-service" in response.url:
                        if response.status == 200:
                            data = await response.json()
                            captured_api_payloads.append(data)
                except Exception:
                    pass

            page.on("response", capture_network)

            try:
                date_formatted = travel_date.strftime("%d/%m/%Y")
                url = f"https://www.makemytrip.com/flight/search?itinerary={origin}-{destination}-{date_formatted}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E"

                logger.info(f"[MMT] Crawling {origin}->{destination} (T+{advance_window} | {date_formatted})")
                await page.goto(url, wait_until="domcontentloaded", timeout=45000)
                await self.jitter_sleep(3.0, 5.0)

                for payload in captured_api_payloads:
                    flight_list = payload.get("data", {}).get("flights", []) or payload.get("flights", [])
                    for flt in flight_list:
                        airline_name = flt.get("airlineName", "Airways")
                        flight_no = flt.get("flightNumber", "FL-000")
                        airline_code = flight_no[:2] if len(flight_no) >= 2 else "XX"
                        
                        price = float(flt.get("fareDetails", {}).get("totalFare", 0.0) or flt.get("totalPrice", 0.0))
                        if price <= 500:
                            continue

                        stops = int(flt.get("stops", 0))
                        dep_str = flt.get("departureTime", travel_date.isoformat())
                        arr_str = flt.get("arrivalTime", travel_date.isoformat())

                        try:
                            dep_dt = datetime.fromisoformat(dep_str.replace("Z", "+00:00"))
                            arr_dt = datetime.fromisoformat(arr_str.replace("Z", "+00:00"))
                        except Exception:
                            dep_dt = travel_date
                            arr_dt = travel_date

                        fare_id = self.generate_fingerprint_id(
                            "MMT", flight_no, origin, destination, dep_dt.isoformat()
                        )

                        results.append(
                            RawFarePayload(
                                fare_id=fare_id,
                                source="MAKEMYTRIP_OTA",
                                airline_code=airline_code,
                                flight_number=flight_no,
                                origin_iata=origin,
                                destination_iata=destination,
                                departure_datetime=dep_dt,
                                arrival_datetime=arr_dt,
                                duration_minutes=int(flt.get("duration", 120)),
                                stops=stops,
                                base_fare=round(price * 0.85, 2),
                                taxes_and_surcharges=round(price * 0.15, 2),
                                total_fare=price,
                                advance_purchase_window=advance_window,
                                cabin_class="ECONOMY",
                            )
                        )

            except Exception as e:
                logger.error(f"[MMT] Extraction failed on {origin}-{destination}: {str(e)}")
            finally:
                await page.close()
                await context.close()

            return results