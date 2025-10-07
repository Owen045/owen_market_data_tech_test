"""
Data loader service for loading and accessing market and property data.
"""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.models.schemas import Market, MarketPerformance, Property


class DataStore:
    """In-memory data store for markets and properties."""

    def __init__(self):
        self.markets: Dict[int, Market] = {}
        self.properties: Dict[int, Property] = {}
        self._load_data()

    def _load_data(self):
        """Load data from JSON files."""
        base_path = Path(__file__).parent.parent.parent / "data"

        # Load market data
        with open(base_path / "market_data.json") as f:
            market_data = json.load(f)
            for market_dict in market_data:
                # Convert date strings to date objects
                for perf in market_dict["performance"]:
                    perf["date"] = datetime.strptime(perf["date"], "%Y-%m-%d").date()

                market = Market(**market_dict)
                self.markets[market.market_id] = market

        # Load property data
        with open(base_path / "property_data.json") as f:
            property_data = json.load(f)
            for prop_dict in property_data:
                prop = Property(**prop_dict)
                self.properties[prop.id] = prop

    def get_market(self, market_id: int) -> Optional[Market]:
        """Get market by ID."""
        return self.markets.get(market_id)

    def get_property(self, property_id: int) -> Optional[Property]:
        """Get property by ID."""
        return self.properties.get(property_id)

    def get_market_properties(self, market_id: int) -> List[Property]:
        """Get all properties in a market."""
        return [prop for prop in self.properties.values() if prop.market_id == market_id]

    def get_latest_market_performance(self, market_id: int) -> Optional[MarketPerformance]:
        """Get the latest performance data for a market."""
        market = self.get_market(market_id)
        if not market or not market.performance:
            return None

        # Performance data is already sorted by date in the JSON
        return market.performance[-1]

    def get_market_performance_range(
        self, market_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[MarketPerformance]:
        """Get market performance data within a date range."""
        market = self.get_market(market_id)
        if not market:
            return []

        performance_data = market.performance

        if start_date:
            performance_data = [p for p in performance_data if p.date >= start_date]

        if end_date:
            performance_data = [p for p in performance_data if p.date <= end_date]

        return performance_data

    def get_all_markets(self) -> List[Market]:
        """Get all markets."""
        return list(self.markets.values())


# Global data store instance
data_store = DataStore()


def get_data_store() -> DataStore:
    """Dependency injection function for FastAPI."""
    return data_store
