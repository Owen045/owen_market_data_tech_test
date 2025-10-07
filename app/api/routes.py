"""
API route definitions for CRE Analytics API.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.schemas import (
    MarketOverviewResponse,
    MarketPropertiesResponse,
    PropertyMarketPerformanceResponse,
)
from app.services.analytics import analytics_service
from app.services.data_loader import DataStore, get_data_store

router = APIRouter(prefix="/api", tags=["CRE Analytics"])


@router.get("/markets/{market_id}", response_model=MarketOverviewResponse)
def get_market_overview(
    market_id: int,
    start_date: Optional[date] = Query(None, description="Start date for performance history"),
    end_date: Optional[date] = Query(None, description="End date for performance history"),
    include_trends: bool = Query(True, description="Include trend analysis"),
    data_store: DataStore = Depends(get_data_store)
):
    """
    Retrieve market overview with latest performance data.

    - **market_id**: The ID of the market
    - **start_date**: Optional start date for historical data
    - **end_date**: Optional end date for historical data
    - **include_trends**: Whether to include trend analysis (default: True)
    """
    market = data_store.get_market(market_id)
    if not market:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")

    latest_performance = data_store.get_latest_market_performance(market_id)
    if not latest_performance:
        raise HTTPException(
            status_code=404,
            detail=f"No performance data found for market {market_id}"
        )

    # Get performance history if date range specified
    performance_history = None
    if start_date or end_date:
        performance_history = data_store.get_market_performance_range(
            market_id, start_date, end_date
        )

    # Calculate trends
    trends = None
    if include_trends:
        # Use all available data for trend calculation
        all_performance = market.performance
        trends = analytics_service.calculate_market_trends(all_performance)

    return MarketOverviewResponse(
        market_id=market.market_id,
        market_name=market.market_name,
        city=market.city,
        state=market.state,
        market_type=market.market_type,
        latest_performance=latest_performance,
        trends=trends,
        performance_history=performance_history
    )


@router.get(
    "/properties/{property_id}/market-performance",
    response_model=PropertyMarketPerformanceResponse
)
def get_property_market_performance(
    property_id: int,
    data_store: DataStore = Depends(get_data_store)
):
    """
    Compare an individual property against its local market benchmarks.

    - **property_id**: The ID of the property
    """
    property_ = data_store.get_property(property_id)
    if not property_:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found")

    # Get market benchmark
    market_benchmark = data_store.get_latest_market_performance(property_.market_id)
    if not market_benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"No market data found for property's market (market_id: {property_.market_id})"
        )

    # Analyze performance
    variance_analysis = analytics_service.analyze_property_performance(
        property_, market_benchmark
    )

    # Generate summary
    performance_summary = analytics_service.generate_performance_summary(variance_analysis)

    return PropertyMarketPerformanceResponse(
        property=property_,
        market_benchmark=market_benchmark,
        variance_analysis=variance_analysis,
        overall_performance_summary=performance_summary
    )


@router.get("/markets/{market_id}/properties", response_model=MarketPropertiesResponse)
def get_market_properties(
    market_id: int,
    sort_by: Optional[str] = Query(
        None,
        description="Sort by: occupancy_variance, rent_variance, property_name"
    ),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    limit: int = Query(10, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    property_class: Optional[str] = Query(None, description="Filter by property class (A, B, C)"),
    data_store: DataStore = Depends(get_data_store)
):
    """
    Get performance of all properties in a market.

    - **market_id**: The ID of the market
    - **sort_by**: Sort by occupancy_variance, rent_variance, or property_name
    - **sort_order**: Sort order (asc or desc)
    - **limit**: Number of results per page (max 100)
    - **offset**: Number of results to skip for pagination
    - **property_class**: Filter by property class (A, B, C)
    """
    market = data_store.get_market(market_id)
    if not market:
        raise HTTPException(status_code=404, detail=f"Market {market_id} not found")

    market_benchmark = data_store.get_latest_market_performance(market_id)
    if not market_benchmark:
        raise HTTPException(
            status_code=404,
            detail=f"No performance data found for market {market_id}"
        )

    # Get all properties in the market
    properties = data_store.get_market_properties(market_id)

    # Apply property class filter
    if property_class:
        properties = [p for p in properties if p.property_class.upper() == property_class.upper()]

    # Create property summaries
    property_summaries = [
        analytics_service.create_property_summary(prop, market_benchmark)
        for prop in properties
    ]

    # Sort
    if sort_by == "occupancy_variance":
        property_summaries.sort(
            key=lambda x: x.occupancy_vs_market if x.occupancy_vs_market is not None else float('-inf'),
            reverse=(sort_order.lower() == "desc")
        )
    elif sort_by == "rent_variance":
        property_summaries.sort(
            key=lambda x: x.rent_vs_market if x.rent_vs_market is not None else float('-inf'),
            reverse=(sort_order.lower() == "desc")
        )
    elif sort_by == "property_name":
        property_summaries.sort(
            key=lambda x: x.property_name,
            reverse=(sort_order.lower() == "desc")
        )

    # Pagination
    total_count = len(property_summaries)
    paginated_properties = property_summaries[offset:offset + limit]

    return MarketPropertiesResponse(
        market_id=market.market_id,
        market_name=market.market_name,
        market_benchmark=market_benchmark,
        properties=paginated_properties,
        total_count=total_count,
        pagination={
            "limit": limit,
            "offset": offset,
            "total": total_count,
            "has_more": offset + limit < total_count
        }
    )


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "CRE Analytics API"}
