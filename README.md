# Commercial Real Estate Analytics API

A RESTful API built with FastAPI that provides analytical insights for commercial real estate properties by comparing individual asset performance against market benchmarks.

## Overview

This API enables CRE professionals to assess property performance relative to market averages across geographic regions, supporting data-driven investment decisions.

### Key Features

- **Market Overview**: Retrieve market-level performance metrics with trend analysis
- **Property Performance Analysis**: Compare individual properties against local market benchmarks
- **Multi-Asset Comparison**: Analyze all properties within a market with sorting and filtering
- **Variance Analytics**: Calculate performance indicators (outperforming/underperforming/at-market)
- **Trend Analysis**: Month-over-month trend calculations for key metrics
- **Missing Data Handling**: Graceful handling of incomplete property data

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Python**: 3.8+
- **Data Validation**: Pydantic 2.5.3
- **Web Server**: Uvicorn 0.27.0
- **Data Storage**: In-memory (JSON-based for development)

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoint definitions
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── data_loader.py     # Data access layer
│       └── analytics.py       # Business logic & calculations
├── data/
│   ├── market_data.json       # Market performance data
│   └── property_data.json     # Property information
├── main.py                     # FastAPI application entry point
├── requirements.txt
├── PERFORMANCE_ANALYSIS.md    # Scalability analysis
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (recommended Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/owen_market_data_tech_test.git
cd owen_market_data_tech_test
```

2. Create and activate a virtual environment:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the project and its dependencies:

**Recommended - Install everything in editable mode:**
```bash
uv pip install -e ".[dev]"
```
This single command installs:
- All runtime dependencies (FastAPI, Uvicorn, Pydantic, python-dateutil)
- All development tools (pre-commit, ruff, mypy)
- The project itself in editable mode (so code changes are immediately reflected)

**For production (runtime dependencies only):**
```bash
uv pip install -e .
```

### Running the API

Start the development server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### 1. Market Overview

**Endpoint**: `GET /api/markets/{market_id}`

Retrieve the latest market performance data with optional trend analysis and historical data.

**Parameters**:
- `market_id` (path, required): The ID of the market
- `start_date` (query, optional): Start date for historical data (YYYY-MM-DD)
- `end_date` (query, optional): End date for historical data (YYYY-MM-DD)
- `include_trends` (query, optional): Include trend analysis (default: true)

**Example Request**:
```bash
curl http://localhost:8000/api/markets/1?include_trends=true
```

**Example Response**:
```json
{
  "market_id": 1,
  "market_name": "Chicago Loop Office",
  "city": "Chicago",
  "state": "Illinois",
  "market_type": "office",
  "latest_performance": {
    "date": "2025-09-01",
    "avg_rent_per_sqft": 38.20,
    "avg_occupancy_rate": 89.2,
    "renewal_rate": 75.2,
    "new_deal_rate": 24.8,
    "avg_lease_term_months": 92,
    "avg_time_to_lease_days": 108
  },
  "trends": [
    {
      "metric_name": "rent_per_sqft",
      "latest_value": 38.20,
      "previous_value": 37.40,
      "change_percentage": 2.14,
      "trend_direction": "up"
    }
  ]
}
```

### 2. Property Market Performance

**Endpoint**: `GET /api/properties/{property_id}/market-performance`

Compare an individual property against its local market benchmarks.

**Parameters**:
- `property_id` (path, required): The ID of the property

**Example Request**:
```bash
curl http://localhost:8000/api/properties/1/market-performance
```

**Example Response**:
```json
{
  "property": {
    "id": 1,
    "name": "Willis Tower",
    "address": "233 S Wacker Dr, Chicago, IL",
    "market_id": 1,
    "area_sqft": 4200000,
    "year_built": 1973,
    "property_class": "A",
    "current_occupancy_rate": 92.5,
    "current_avg_rent_per_sqft": 42.80,
    "renewal_rate_ytd": 78.5,
    "avg_lease_term_months": 96,
    "avg_time_to_lease_days": 85
  },
  "market_benchmark": {
    "date": "2025-09-01",
    "avg_rent_per_sqft": 38.20,
    "avg_occupancy_rate": 89.2,
    "renewal_rate": 75.2,
    "new_deal_rate": 24.8,
    "avg_lease_term_months": 92,
    "avg_time_to_lease_days": 108
  },
  "variance_analysis": [
    {
      "metric_name": "occupancy_rate",
      "property_value": 92.5,
      "market_value": 89.2,
      "variance_percentage": 3.70,
      "performance_indicator": "at-market"
    },
    {
      "metric_name": "rent_per_sqft",
      "property_value": 42.80,
      "market_value": 38.20,
      "variance_percentage": 12.04,
      "performance_indicator": "outperforming"
    }
  ],
  "overall_performance_summary": "Property is generally outperforming the market (3/5 metrics above market)"
}
```

### 3. Market Properties

**Endpoint**: `GET /api/markets/{market_id}/properties`

Get performance of all properties in a market with sorting, filtering, and pagination.

**Parameters**:
- `market_id` (path, required): The ID of the market
- `sort_by` (query, optional): Sort by `occupancy_variance`, `rent_variance`, or `property_name`
- `sort_order` (query, optional): `asc` or `desc` (default: desc)
- `limit` (query, optional): Number of results per page (1-100, default: 10)
- `offset` (query, optional): Number of results to skip (default: 0)
- `property_class` (query, optional): Filter by property class (A, B, C)

**Example Request**:
```bash
curl "http://localhost:8000/api/markets/1/properties?sort_by=rent_variance&limit=5"
```

**Example Response**:
```json
{
  "market_id": 1,
  "market_name": "Chicago Loop Office",
  "market_benchmark": {
    "date": "2025-09-01",
    "avg_rent_per_sqft": 38.20,
    "avg_occupancy_rate": 89.2,
    "renewal_rate": 75.2,
    "new_deal_rate": 24.8,
    "avg_lease_term_months": 92,
    "avg_time_to_lease_days": 108
  },
  "properties": [
    {
      "property_id": 3,
      "property_name": "River Point",
      "property_class": "A",
      "current_occupancy_rate": 95.2,
      "current_avg_rent_per_sqft": 45.60,
      "occupancy_vs_market": 6.73,
      "rent_vs_market": 19.37,
      "overall_performance": "outperforming"
    }
  ],
  "total_count": 4,
  "pagination": {
    "limit": 5,
    "offset": 0,
    "total": 4,
    "has_more": false
  }
}
```

### 4. Health Check

**Endpoint**: `GET /api/health`

Check API health status.

**Example Request**:
```bash
curl http://localhost:8000/api/health
```

**Example Response**:
```json
{
  "status": "healthy",
  "service": "CRE Analytics API"
}
```

## Data Models

### Market Performance Metrics

- `avg_rent_per_sqft`: Average rental rate per square foot
- `avg_occupancy_rate`: Average occupancy percentage
- `renewal_rate`: Percentage of lease renewals
- `new_deal_rate`: Percentage of new lease deals
- `avg_lease_term_months`: Average lease duration in months
- `avg_time_to_lease_days`: Average days to lease a space

### Performance Indicators

- **outperforming**: Property metric exceeds market average by >5%
- **at-market**: Property metric within ±5% of market average
- **underperforming**: Property metric below market average by >5%
- **no-data**: Property data not available for comparison

## Business Logic

### Variance Calculation

```
variance_percentage = ((property_value - market_value) / market_value) * 100
```

### Overall Performance Summary

The overall performance classification uses a majority voting system:
- Analyzes 5 key metrics (occupancy, rent, renewal rate, lease term, time to lease)
- Counts outperforming, at-market, and underperforming indicators
- Returns the dominant classification with metric counts
- For mixed performance (no clear majority), returns detailed breakdown of all three categories

### Missing Data Handling

- Properties with missing metrics receive "no-data" indicators
- Variance calculations skip null values gracefully
- Overall performance considers only available metrics
- API returns descriptive messages when data is insufficient

## Development Notes

### Design Decisions

1. **FastAPI over Django REST Framework**: Chosen for lighter weight, better async support, and automatic OpenAPI documentation
2. **In-memory data store**: Suitable for the current dataset size and development speed
3. **Pydantic models**: Strong typing and validation with minimal boilerplate
4. **Separation of concerns**: Clear boundaries between data access, business logic, and API layers
5. **Trend analysis**: Month-over-month comparison provides actionable insights
6. **Code quality tools**: Ruff for linting/formatting, mypy for type checking, pre-commit hooks for automated checks

### Analytical Approach

- **5% threshold for "at-market"**: A reasonable tolerance band chosen for this implementation to classify performance (properties within ±5% of market average are considered "at-market")
- **Inverse indicator for time-to-lease**: Lower values indicate better performance
- **Weighted performance**: Occupancy and rent metrics prioritized in property summaries
- **Trend directions**: Stable (<1% change), up (>1% increase), down (>1% decrease)

### Edge Cases Handled

- Null/missing property metrics (renewal_rate_ytd, avg_lease_term_months, etc.)
- Empty performance history
- Invalid market/property IDs
- Date range queries with no matching data
- Division by zero in variance calculations
- Pagination beyond available results
- Mixed performance scenarios (no clear majority in performance indicators)

## Error Handling

The API returns consistent error responses:

```json
{
  "error": {
    "code": 404,
    "message": "Market 999 not found",
    "type": "http_error"
  }
}
```

Error types:
- `http_error`: Standard HTTP errors (404, 400, etc.)
- `validation_error`: Request validation failures (422)
- `server_error`: Internal server errors (500)

## Future Improvements

- Add unit tests with pytest
- Implement request logging for observability
- Add response compression for large result sets
- Create Docker container for easy deployment
- PostgreSQL database integration
- Redis caching layer for rapid access of often queried results, requires cache invalidation logic for when new data added
- User authentication and API keys
- Historical performance tracking for properties
- Predictive analytics (rent forecasting)
- External data source integrations (economic indicators)
- WebSocket support for real-time updates
- Plotting UI for visualising trend data
