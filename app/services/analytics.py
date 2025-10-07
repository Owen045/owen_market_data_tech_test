"""
Analytics service for calculating performance metrics and comparisons.
"""
from typing import List, Optional, Tuple

from app.models.schemas import (
    MarketPerformance,
    MarketTrend,
    PerformanceVariance,
    Property,
    PropertySummary,
)


class AnalyticsService:
    """Service for calculating analytical metrics."""

    @staticmethod
    def calculate_variance(
        property_value: Optional[float],
        market_value: float
    ) -> Tuple[Optional[float], str]:
        """
        Calculate variance percentage and performance indicator.

        Returns:
            Tuple of (variance_percentage, performance_indicator)
        """
        if property_value is None:
            return None, "no-data"

        variance_pct = ((property_value - market_value) / market_value) * 100

        # Determine performance indicator based on variance
        # Using 5% threshold for "at-market" classification
        if abs(variance_pct) < 5:
            indicator = "at-market"
        elif variance_pct > 0:
            indicator = "outperforming"
        else:
            indicator = "underperforming"

        return variance_pct, indicator

    @staticmethod
    def analyze_property_performance(
        property_: Property,
        market_benchmark: MarketPerformance
    ) -> List[PerformanceVariance]:
        """
        Analyze property performance against market benchmarks.

        Returns list of variance analyses for each metric.
        """
        variances = []

        # Occupancy rate
        variance_pct, indicator = AnalyticsService.calculate_variance(
            property_.current_occupancy_rate,
            market_benchmark.avg_occupancy_rate
        )
        variances.append(PerformanceVariance(
            metric_name="occupancy_rate",
            property_value=property_.current_occupancy_rate,
            market_value=market_benchmark.avg_occupancy_rate,
            variance_percentage=variance_pct,
            performance_indicator=indicator
        ))

        # Rent per sqft
        variance_pct, indicator = AnalyticsService.calculate_variance(
            property_.current_avg_rent_per_sqft,
            market_benchmark.avg_rent_per_sqft
        )
        variances.append(PerformanceVariance(
            metric_name="rent_per_sqft",
            property_value=property_.current_avg_rent_per_sqft,
            market_value=market_benchmark.avg_rent_per_sqft,
            variance_percentage=variance_pct,
            performance_indicator=indicator
        ))

        # Renewal rate
        variance_pct, indicator = AnalyticsService.calculate_variance(
            property_.renewal_rate_ytd,
            market_benchmark.renewal_rate
        )
        variances.append(PerformanceVariance(
            metric_name="renewal_rate",
            property_value=property_.renewal_rate_ytd,
            market_value=market_benchmark.renewal_rate,
            variance_percentage=variance_pct,
            performance_indicator=indicator
        ))

        # Lease term
        variance_pct, indicator = AnalyticsService.calculate_variance(
            float(property_.avg_lease_term_months) if property_.avg_lease_term_months else None,
            float(market_benchmark.avg_lease_term_months)
        )
        variances.append(PerformanceVariance(
            metric_name="lease_term_months",
            property_value=float(property_.avg_lease_term_months) if property_.avg_lease_term_months else None,
            market_value=float(market_benchmark.avg_lease_term_months),
            variance_percentage=variance_pct,
            performance_indicator=indicator
        ))

        # Time to lease
        variance_pct, indicator = AnalyticsService.calculate_variance(
            float(property_.avg_time_to_lease_days) if property_.avg_time_to_lease_days else None,
            float(market_benchmark.avg_time_to_lease_days)
        )
        # Note: Lower time to lease is better, so we invert the indicator
        if indicator == "outperforming":
            indicator = "underperforming"
        elif indicator == "underperforming":
            indicator = "outperforming"

        variances.append(PerformanceVariance(
            metric_name="time_to_lease_days",
            property_value=float(property_.avg_time_to_lease_days) if property_.avg_time_to_lease_days else None,
            market_value=float(market_benchmark.avg_time_to_lease_days),
            variance_percentage=variance_pct,
            performance_indicator=indicator
        ))

        return variances

    @staticmethod
    def generate_performance_summary(variances: List[PerformanceVariance]) -> str:
        """Generate a text summary of overall property performance."""
        # Count performance indicators (excluding no-data)
        indicators = [v.performance_indicator for v in variances if v.performance_indicator != "no-data"]

        if not indicators:
            return "Insufficient data to determine overall performance"

        outperforming_count = indicators.count("outperforming")
        underperforming_count = indicators.count("underperforming")
        at_market_count = indicators.count("at-market")

        # Simple majority voting
        if outperforming_count > underperforming_count:
            return f"Property is generally outperforming the market ({outperforming_count}/{len(indicators)} metrics above market)"
        elif underperforming_count > outperforming_count:
            return f"Property is generally underperforming the market ({underperforming_count}/{len(indicators)} metrics below market)"
        else:
            return f"Property is performing at market levels ({at_market_count}/{len(indicators)} metrics at market)"

    @staticmethod
    def calculate_market_trends(
        performance_history: List[MarketPerformance]
    ) -> List[MarketTrend]:
        """
        Calculate trends from historical performance data.

        Compares latest value to previous period (MoM).
        """
        if len(performance_history) < 2:
            return []

        latest = performance_history[-1]
        previous = performance_history[-2]

        trends = []

        # Helper function to create trend
        def create_trend(name: str, latest_val: float, prev_val: float) -> MarketTrend:
            change_pct = ((latest_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0

            if abs(change_pct) < 1:
                direction = "stable"
            elif change_pct > 0:
                direction = "up"
            else:
                direction = "down"

            return MarketTrend(
                metric_name=name,
                latest_value=latest_val,
                previous_value=prev_val,
                change_percentage=round(change_pct, 2),
                trend_direction=direction
            )

        trends.append(create_trend("rent_per_sqft", latest.avg_rent_per_sqft, previous.avg_rent_per_sqft))
        trends.append(create_trend("occupancy_rate", latest.avg_occupancy_rate, previous.avg_occupancy_rate))
        trends.append(create_trend("renewal_rate", latest.renewal_rate, previous.renewal_rate))
        trends.append(create_trend("lease_term_months", float(latest.avg_lease_term_months), float(previous.avg_lease_term_months)))

        return trends

    @staticmethod
    def create_property_summary(
        property_: Property,
        market_benchmark: MarketPerformance
    ) -> PropertySummary:
        """Create a summary of property performance for multi-asset views."""
        # Calculate key variances
        occupancy_variance = None
        rent_variance = None

        if property_.current_occupancy_rate:
            occupancy_variance = round(
                ((property_.current_occupancy_rate - market_benchmark.avg_occupancy_rate) /
                 market_benchmark.avg_occupancy_rate) * 100,
                2
            )

        if property_.current_avg_rent_per_sqft:
            rent_variance = round(
                ((property_.current_avg_rent_per_sqft - market_benchmark.avg_rent_per_sqft) /
                 market_benchmark.avg_rent_per_sqft) * 100,
                2
            )

        # Determine overall performance (weighted towards occupancy and rent)
        performance_scores = []
        if occupancy_variance is not None:
            performance_scores.append(occupancy_variance)
        if rent_variance is not None:
            performance_scores.append(rent_variance)

        if performance_scores:
            avg_variance = sum(performance_scores) / len(performance_scores)
            if abs(avg_variance) < 5:
                overall_performance = "at-market"
            elif avg_variance > 0:
                overall_performance = "outperforming"
            else:
                overall_performance = "underperforming"
        else:
            overall_performance = "insufficient-data"

        return PropertySummary(
            property_id=property_.id,
            property_name=property_.name,
            property_class=property_.property_class,
            current_occupancy_rate=property_.current_occupancy_rate,
            current_avg_rent_per_sqft=property_.current_avg_rent_per_sqft,
            occupancy_vs_market=occupancy_variance,
            rent_vs_market=rent_variance,
            overall_performance=overall_performance
        )


analytics_service = AnalyticsService()
