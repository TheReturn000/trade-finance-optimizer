"""Scoring logic for recommendations."""


def calculate_commodity_repayment_strength(
    trend_score: int,
    volatility_score: int,
    demand_score: int
) -> int:
    """
    Calculate commodity repayment strength (0-100).
    Weighting: 40% trend + 35% volatility + 25% demand
    """
    score = (0.40 * trend_score) + (0.35 * volatility_score) + (0.25 * demand_score)
    return min(100, max(0, int(score)))


def calculate_trade_feasibility(
    licensing_score: int,
    tariff_score: int,
    facilitation_score: int
) -> int:
    """
    Calculate trade feasibility (0-100).
    Weighting: 35% licensing + 35% tariff + 30% facilitation
    """
    score = (0.35 * licensing_score) + (0.35 * tariff_score) + (0.30 * facilitation_score)
    return min(100, max(0, int(score)))


def calculate_geo_macro_stability(
    governance_score: int,
    fx_inflation_score: int,
    disruption_score: int
) -> int:
    """
    Calculate geopolitical & macro stability (0-100).
    Weighting: 40% governance + 30% FX/inflation + 30% disruption
    """
    score = (0.40 * governance_score) + (0.30 * fx_inflation_score) + (0.30 * disruption_score)
    return min(100, max(0, int(score)))


def calculate_final_score(
    commodity_strength: int,
    trade_feasibility: int,
    geo_macro_stability: int,
    operational_compliance: int
) -> int:
    """
    Calculate final recommendation score (0-100).
    Weighting: 35% commodity + 30% trade + 25% geo/macro + 10% operations
    """
    score = (
        (0.35 * commodity_strength) +
        (0.30 * trade_feasibility) +
        (0.25 * geo_macro_stability) +
        (0.10 * operational_compliance)
    )
    return min(100, max(0, int(score)))


def determine_confidence_level(passing_scenarios: int) -> str:
    """
    Determine confidence level based on stress test results.
    passing_scenarios: number of scenarios (out of 3) that pass threshold
    """
    if passing_scenarios == 3:
        return "HIGH"
    elif passing_scenarios == 2:
        return "MEDIUM"
    else:
        return "LOW"
