"""
Pydantic models for data validation and serialization.
"""
from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class MarketPerformance(BaseModel):
    """Market performance metrics for a specific date."""
    date: date
    avg_rent_per_sqft: float
    avg_occupancy_rate: float
    renewal_rate: float
    new_deal_rate: float
    avg_lease_term_months: int
    avg_time_to_lease_days: int


class Market(BaseModel):
    """Market data model."""
    market_id: int
    market_name: str
    city: str
    state: str
    market_type: str
    performance: List[MarketPerformance]


class Property(BaseModel):
    """Property data model."""
    id: int
    name: str
    address: str
    market_id: int
    area_sqft: int
    year_built: int
    property_class: str
    current_occupancy_rate: float
    current_avg_rent_per_sqft: Optional[float] = None
    renewal_rate_ytd: Optional[float] = None
    avg_lease_term_months: Optional[int] = None
    avg_time_to_lease_days: Optional[int] = None


# Response models
class MarketTrend(BaseModel):
    """Market trend analysis."""
    metric_name: str
    latest_value: float
    previous_value: Optional[float] = None
    change_percentage: Optional[float] = None
    trend_direction: str  # "up", "down", "stable"


class MarketOverviewResponse(BaseModel):
    """Response model for market overview endpoint."""
    market_id: int
    market_name: str
    city: str
    state: str
    market_type: str
    latest_performance: MarketPerformance
    trends: Optional[List[MarketTrend]] = None
    performance_history: Optional[List[MarketPerformance]] = None


class PerformanceVariance(BaseModel):
    """Variance between property and market metrics."""
    metric_name: str
    property_value: Optional[float] = None
    market_value: float
    variance_percentage: Optional[float] = None
    performance_indicator: str  # "outperforming", "underperforming", "at-market", "no-data"


class PropertyMarketPerformanceResponse(BaseModel):
    """Response model for single property market performance."""
    property: Property
    market_benchmark: MarketPerformance
    variance_analysis: List[PerformanceVariance]
    overall_performance_summary: str


class PropertySummary(BaseModel):
    """Summary of property performance vs market."""
    property_id: int
    property_name: str
    property_class: str
    current_occupancy_rate: float
    current_avg_rent_per_sqft: Optional[float] = None
    occupancy_vs_market: Optional[float] = None
    rent_vs_market: Optional[float] = None
    overall_performance: str  # "outperforming", "underperforming", "at-market"


class MarketPropertiesResponse(BaseModel):
    """Response model for multi-asset market performance."""
    market_id: int
    market_name: str
    market_benchmark: MarketPerformance
    properties: List[PropertySummary]
    total_count: int
    pagination: dict
