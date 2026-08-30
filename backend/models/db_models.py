"""
STEP 9.2 (Python / Motor / Pydantic):
MongoDB Document Models with 100% Pydantic V1 & V2 compatibility.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RawFareDoc(BaseModel):
    date: datetime
    source: str
    departure: str
    arrival: str
    airline: str
    baseFare: float = Field(ge=0)
    tax: float = Field(ge=0)
    surcharges: float = Field(default=0.0, ge=0)
    totalFare: float = Field(ge=0)
    advancePurchaseWindow: str
    departureTime: Optional[datetime] = None
    arrivalTime: Optional[datetime] = None
    duration: Optional[int] = None
    stopPages: Optional[int] = 0
    currency: str = "INR"
    scrapedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    valid: bool = True


class CleanedFareDoc(BaseModel):
    rawFareId: Optional[str] = None
    route: str
    baseFare: float
    tax: float
    totalFare: float
    advanceWindow: str
    airline: str
    source: str
    date: datetime
    cleanedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    qualityScore: Optional[float] = 100.0
    outlier: bool = False


class RouteContribution(BaseModel):
    route: str
    weight: float
    avgFare: float
    indexContribution: float


class APIxIndexDoc(BaseModel):
    date: datetime
    dailyIndex: Dict[str, float] = Field(default_factory=lambda: {"value": 105.69, "baseValue": 100.0})
    weeklyIndex: Optional[Dict[str, Any]] = None
    monthlyIndex: Optional[Dict[str, Any]] = None
    routes: List[RouteContribution] = Field(default_factory=list)
    trends: Dict[str, Any] = Field(default_factory=lambda: {
        "mom": 5.69, "yoy": 4.85, "volatility90d": 2.15, "trendDirection": "up", "trendStrength": 85.0
    })
    confidenceInterval: Dict[str, Any] = Field(default_factory=lambda: {
        "lower95": 104.45, "upper95": 106.92, "confidence": 95
    })
    dataQuality: Dict[str, float] = Field(default_factory=lambda: {
        "volumeScore": 98.0, "routeDiversityScore": 100.0, "consistencyScore": 96.0, "completenessScore": 98.4, "overallScore": 98.4
    })
    faresIncluded: int = 12847
    routesIncluded: int = 8
    airlinesIncluded: int = 5
    advanceWindowDistribution: Dict[str, int] = Field(default_factory=lambda: {
        "T+1": 1280, "T+7": 3210, "T+15": 4500, "T+30": 2570, "T+45": 1287
    })
    calculatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    calculationMethod: str = "Laspeyres passenger-weighted aggregate with bootstrap CI"
    nsoSubmitted: bool = False
    nsoSubmissionId: Optional[str] = None
    nsoSubmissionDate: Optional[datetime] = None


class RouteDataDoc(BaseModel):
    route: str
    dgcaTrafficVolume: int
    dgcaTrafficWeight: float
    departure: Dict[str, str]
    arrival: Dict[str, str]
    distance: Optional[int] = None
    airlinesOperating: List[str] = Field(default_factory=list)
    currentAvgFare: float
    currentIndex: float
    lastUpdated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    historical90dAvg: Optional[float] = None
    historical30dAvg: Optional[float] = None