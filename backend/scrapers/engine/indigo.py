import json
import logging
from datetime import datetime, timezone
from typing import Dict, List
from playwright.async_api import Response
from .base import BaseAirfareEngine, RawFarePayload

logger = logging.getLogger("APIx.IndiGoEngine")


class IndigoProductionScraper(BaseAirfareEngine):
    def __init__(self, concurrency_limit: int = 3, proxy: str = None):
        super().__init__(name="IndiGo_Direct", concurrency_limit=concurrency_limit, proxy=proxy)
        self.portal_url = "https://www.goindigo.in/"

    async def fetch_route_fares(
        self, origin: str, destination: str, travel_date: datetime, advance_window: int
    ) -> List[RawFarePayload]:
        async with self.semaphore:
            context = await self.create_stealth_context()
            page = await context.new_page()
            scraped_records: List[RawFarePayload] = []
            captured_api_payloads: List[Dict] = []

            # Intercept XHR/Fetch responses
            async def handle_response(response: Response):
                try:
                    url = response.url
                    # Filter for internal fare pricing and availability API endpoints
                    if any(endpoint in url for endpoint in ["/booking/flightSearch", "/api/availability", "fares", "flightSelect"]):
                        if response.status == 200 and "application/json" in response.headers.get("content-type", ""):
                            json_data = await response.json()
                            captured_api_payloads.append(json_data)
                except Exception:
                    pass

            page.on("response", handle_response)

            try:
                date_str = travel_date.strftime("%Y-%m-%d")
                deep_link = (
                    f"https://www.goindigo.in/flight-booking.html?"
                    f"from={origin}&to={destination}&date={date_str}&adults=1&currency=INR"
                )

                logger.info(f"[IndiGo] Initiating extraction for {origin}->{destination} (T+{advance_window} | {date_str})")
                await page.goto(deep_link, wait_until="networkidle", timeout=45000)
                await self.jitter_sleep(2.0, 4.0)

                # Fallback extraction from page state if direct network interception is empty
                if not captured_api_payloads:
                    json_state = await page.evaluate("""() => {
                        return window.__INITIAL_STATE__ || window.preloadedData || null;
                    }""")
                    if json_state:
                        captured_api_payloads.append(json_state)

                # Ingestion parser
                for payload in captured_api_payloads:
                    extracted = self._parse_json_wire(payload, origin, destination, travel_date, advance_window)
                    scraped_records.extend(extracted)

                # Fallback: DOM Parsing for resilient extraction
                if not scraped_records:
                    scraped_records = await self._parse_dom_fallback(page, origin, destination, travel_date, advance_window)

                logger.info(f"[IndiGo] Completed {origin}->{destination} (T+{advance_window}): Parsed {len(scraped_records)} valid fares.")

            except Exception as e:
                logger.error(f"[IndiGo] Extraction failed on route {origin}-{destination} @ {travel_date}: {str(e)}")
            finally:
                await page.close()
                await context.close()

            return scraped_records

    def _parse_json_wire(
        self, data: Dict, origin: str, dest: str, travel_date: datetime, advance_window: int
    ) -> List[RawFarePayload]:
        results: List[RawFarePayload] = []
        try:
            # Traversal strategy matching standard IndiGo flight graph schema
            trips = data.get("trips", []) or data.get("journeys", []) or [data]
            for trip in trips:
                flights = trip.get("flights", []) or trip.get("segments", [])
                for flt in flights:
                    flight_no = str(flt.get("flightNumber", flt.get("identifier", "6E-UNKNOWN")))
                    if not flight_no.startswith("6E"):
                        flight_no = f"6E-{flight_no}"

                    dep_time_raw = flt.get("departureTime", travel_date.isoformat())
                    arr_time_raw = flt.get("arrivalTime", travel_date.isoformat())
                    
                    try:
                        dep_dt = datetime.fromisoformat(dep_time_raw.replace("Z", "+00:00"))
                        arr_dt = datetime.fromisoformat(arr_time_raw.replace("Z", "+00:00"))
                    except Exception:
                        dep_dt = travel_date
                        arr_dt = travel_date

                    fares_block = flt.get("fares", {}) or flt.get("fareClasses", [])
                    total_fare = 0.0
                    if isinstance(fares_block, list) and len(fares_block) > 0:
                        total_fare = float(fares_block[0].get("amount", fares_block[0].get("totalFare", 0.0)))
                    elif isinstance(fares_block, dict):
                        total_fare = float(fares_block.get("amount", fares_block.get("total", 0.0)))

                    if total_fare <= 500:
                        continue

                    # Unbundle Fare Structure (DGCA/CPI Standard Breakdown)
                    base_fare = round(total_fare * 0.82, 2)
                    taxes_fees = round(total_fare - base_fare, 2)

                    fare_id = self.generate_fingerprint_id(
                        "INDIGO", flight_no, origin, dest, dep_dt.isoformat()
                    )

                    payload = RawFarePayload(
                        fare_id=fare_id,
                        source="INDIGO_DIRECT",
                        airline_code="6E",
                        flight_number=flight_no,
                        origin_iata=origin,
                        destination_iata=dest,
                        departure_datetime=dep_dt,
                        arrival_datetime=arr_dt,
                        duration_minutes=int(flt.get("durationMinutes", 120)),
                        stops=int(flt.get("stops", 0)),
                        base_fare=base_fare,
                        taxes_and_surcharges=taxes_fees,
                        total_fare=total_fare,
                        advance_purchase_window=advance_window,
                        cabin_class="ECONOMY",
                    )
                    results.append(payload)
        except Exception as e:
            logger.debug(f"[IndiGo Wire] Wire traversal bypass: {e}")
        return results

    async def _parse_dom_fallback(
        self, page, origin: str, dest: str, travel_date: datetime, advance_window: int
    ) -> List[RawFarePayload]:
        dom_records = []
        try:
            flight_cards = await page.query_selector_all("[data-flight-card], .flight-row, .fare-card")
            for card in flight_cards:
                text_content = await card.inner_text()
                # Parse price patterns
                import re
                prices = re.findall(r"₹\s*([0-9,]+)", text_content)
                if prices:
                    raw_val = float(prices[0].replace(",", ""))
                    if raw_val > 500:
                        flight_no_match = re.search(r"6E[\s-]?\d{3,4}", text_content)
                        flight_no = flight_no_match.group(0).replace(" ", "-") if flight_no_match else "6E-GENERIC"

                        dep_dt = travel_date
                        fare_id = self.generate_fingerprint_id(
                            "INDIGO_DOM", flight_no, origin, dest, f"{dep_dt.isoformat()}_{raw_val}"
                        )
                        dom_records.append(
                            RawFarePayload(
                                fare_id=fare_id,
                                source="INDIGO_DIRECT",
                                airline_code="6E",
                                flight_number=flight_no,
                                origin_iata=origin,
                                destination_iata=dest,
                                departure_datetime=dep_dt,
                                arrival_datetime=dep_dt,
                                duration_minutes=120,
                                stops=0,
                                base_fare=round(raw_val * 0.82, 2),
                                taxes_and_surcharges=round(raw_val * 0.18, 2),
                                total_fare=raw_val,
                                advance_purchase_window=advance_window,
                                cabin_class="ECONOMY",
                            )
                        )
        except Exception as err:
            logger.error(f"[IndiGo DOM Fallback] Failed: {err}")
        return dom_records