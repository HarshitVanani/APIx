from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"


class FareRecord(BaseModel):
    """Raw fare record directly extracted from scraping sources."""
    source: str = Field(..., description="Source portal: indigo, air_india, makemytrip, etc.")
    route_from: str = Field(..., description="3-letter IATA Origin Code (e.g. DEL)")
    route_to: str = Field(..., description="3-letter IATA Destination Code (e.g. BOM)")
    departure_date: datetime
    fare_price: float = Field(..., description="Base fare extracted")
    tax: float = Field(0.0, description="Mandatory airport taxes and fuel surcharges")
    fees: float = Field(0.0, description="User development & convenience fees")
    total_price: float = Field(..., description="Full mandatory payable price")
    advance_window: int = Field(..., description="Lead time in days (1, 7, 15, 30, 45)")
    cabin_class: CabinClass = CabinClass.ECONOMY
    stops: int = Field(0, description="0 for nonstop, 1+ for layovers")
    airline: str
    flight_number: Optional[str] = None
    scrape_timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_valid: bool = True

    class Config:
        populate_by_name = True


class CleanedFare(BaseModel):
    """Standardized and validated fare record ready for index aggregation."""
    route_id: str = Field(..., description="e.g., DEL-BOM")
    departure_date: datetime
    total_price: float
    advance_window: int
    cabin_class: CabinClass
    stops: int
    airline: str
    source: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class DGCARoute(BaseModel):
    """DGCA route metadata and passenger traffic weights."""
    route_id: str = Field(..., description="e.g., DEL-BOM")
    origin_city: str
    origin_code: str
    destination_city: str
    destination_code: str
    monthly_traffic: int
    traffic_weight: float = Field(..., description="Normalized weight between 0 and 1")
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class APIxIndex(BaseModel):
    """Calculated real-time Airfare Price Index output."""
    date: datetime
    index_value: float = Field(..., description="Calculated index score relative to base period 100")
    index_type: str = Field("daily", description="daily, weekly, or monthly")
    routes_included: List[str]
    data_points_count: int
    mom_change: Optional[float] = None
    yoy_change: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# MongoDB Collection indexing configurations
COLLECTION_INDEXES: Dict[str, List] = {
    "raw_fares": [
        [("source", 1), ("scrape_timestamp", -1)],
        [("route_from", 1), ("route_to", 1), ("departure_date", 1)],
    ],
    "cleaned_fares": [
        [("route_id", 1), ("departure_date", -1)],
        [("departure_date", 1)],
    ],
    "dgca_routes": [
        [("route_id", 1)],
    ],
    "apix_index": [
        [("date", -1)],
        [("index_type", 1), ("date", -1)],
    ],
}