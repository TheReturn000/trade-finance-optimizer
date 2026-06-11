from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from db.session import get_db
from db.models import (
    Recommendation, TradeLane, Country, Commodity,
    CommodityTimeSeries, CountryRiskIndicators,
    TradeFeasibility, ComplianceFlag, StressTestResult,
    EvidenceSource, ComplianceChecklist
)
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1", tags=["trade-finance"])


@router.get("/opportunities/top-25")
def get_top_25(
    commodity: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    risk_tolerance: str = Query("balanced"),
    db: Session = Depends(get_db)
):
    """
    Returns top 25 ranked lending opportunities (180-day tenor LC).
    Optional filters: commodity, direction (Export/Import), risk tolerance.
    """
    query = db.query(Recommendation).filter(Recommendation.rank <= 25)
    
    if commodity:
        query = query.join(TradeLane).join(Commodity).filter(
            Commodity.commodity_name.ilike(f"%{commodity}%")
        )
    
    if direction:
        query = query.join(TradeLane).filter(
            TradeLane.direction.ilike(f"%{direction}%")
        )
    
    # Risk tolerance filter (simplistic example)
    if risk_tolerance == "conservative":
        query = query.filter(Recommendation.confidence_level.in_(["HIGH"]))
    elif risk_tolerance == "aggressive":
        query = query.filter(Recommendation.confidence_level.in_(["HIGH", "MEDIUM", "LOW"]))
    else:  # balanced
        query = query.filter(Recommendation.confidence_level.in_(["HIGH", "MEDIUM"]))
    
    recommendations = query.order_by(Recommendation.rank).all()
    
    return [
        {
            "rank": r.rank,
            "origin_country": r.lane.origin_country.country_name,
            "destination_country": r.lane.destination_country.country_name,
            "commodity": r.lane.commodity.commodity_name,
            "direction": r.lane.direction,
            "final_score": r.final_score,
            "commodity_strength": r.commodity_repayment_strength,
            "trade_feasibility": r.trade_feasibility,
            "geo_macro_stability": r.geo_macro_stability,
            "operational_compliance": r.operational_compliance,
            "confidence_level": r.confidence_level,
            "recommended_tenor_days": r.recommended_tenor_days,
            "lc_structure": r.lc_structure_hint,
            "why": r.why_explanation,
            "period_date": r.period_date.isoformat()
        }
        for r in recommendations
    ]


@router.get("/heatmap")
def get_heatmap(
    direction: Optional[str] = Query(None),
    commodity_filter: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Returns country × commodity opportunity matrix for heatmap visualization.
    Color represents final_score (0-100).
    """
    countries = db.query(Country).all()
    commodities = db.query(Commodity).all()
    
    heatmap = {}
    
    for country in countries:
        row = {}
        for commodity in commodities:
            # Get best score for this country-commodity pair
            query = db.query(Recommendation).join(TradeLane).filter(
                ((TradeLane.origin_country_id == country.id) |
                 (TradeLane.destination_country_id == country.id)),
                TradeLane.commodity_id == commodity.id
            )
            
            if direction:
                query = query.filter(TradeLane.direction.ilike(f"%{direction}%"))
            
            if commodity_filter:
                query = query.filter(Commodity.commodity_name.ilike(f"%{commodity_filter}%"))
            
            best_rec = query.order_by(Recommendation.final_score.desc()).first()
            row[commodity.commodity_name] = best_rec.final_score if best_rec else None
        
        heatmap[country.country_name] = row
    
    return {"heatmap": heatmap, "timestamp": datetime.utcnow().isoformat()}


@router.get("/country/{country_name}/deep-dive")
def country_deep_dive(
    country_name: str,
    db: Session = Depends(get_db)
):
    """
    Detailed analysis for a specific country across all 6 commodities.
    Returns commodity cards with trends, volatility, feasibility, and stress tests.
    """
    country = db.query(Country).filter(
        Country.country_name.ilike(f"%{country_name}%")
    ).first()
    
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    
    # Get risk indicators
    risk = db.query(CountryRiskIndicators).filter(
        CountryRiskIndicators.country_id == country.id
    ).order_by(CountryRiskIndicators.period_date.desc()).first()
    
    # Get lanes for this country
    lanes = db.query(TradeLane).filter(
        (TradeLane.origin_country_id == country.id) |
        (TradeLane.destination_country_id == country.id)
    ).all()
    
    commodity_cards = []
    
    for lane in lanes:
        rec = db.query(Recommendation).filter(
            Recommendation.lane_id == lane.id
        ).order_by(Recommendation.period_date.desc()).first()
        
        commodity_ts = db.query(CommodityTimeSeries).filter(
            CommodityTimeSeries.commodity_id == lane.commodity_id
        ).order_by(CommodityTimeSeries.period_date.desc()).first()
        
        trade_feas = db.query(TradeFeasibility).filter(
            TradeFeasibility.lane_id == lane.id
        ).order_by(TradeFeasibility.period_date.desc()).first()
        
        stress_results = db.query(StressTestResult).filter(
            StressTestResult.recommendation_id == rec.id
        ).all() if rec else []
        
        commodity_cards.append({
            "commodity": lane.commodity.commodity_name,
            "direction": lane.direction,
            "partner": (
                lane.destination_country.country_name 
                if lane.direction == "Export" 
                else lane.origin_country.country_name
            ),
            "score": rec.final_score if rec else 0,
            "confidence": rec.confidence_level if rec else "N/A",
            "lc_structure": rec.lc_structure_hint if rec else None,
            "price_current": float(commodity_ts.price_usd_per_unit) if commodity_ts else None,
            "volatility_30d": float(commodity_ts.volatility_30d) if commodity_ts else None,
            "trend_6m": commodity_ts.trend_6m_direction if commodity_ts else None,
            "demand_season": commodity_ts.demand_season if commodity_ts else None,
            "trade_feasibility_score": trade_feas.feasibility_score if trade_feas else None,
            "tariff_rate": float(trade_feas.tariff_rate) if trade_feas else None,
            "stress_tests": [
                {
                    "scenario": s.scenario_type,
                    "coverage_pct": float(s.repayment_coverage_percent),
                    "passes_threshold": s.passes_threshold
                }
                for s in stress_results
            ]
        })
    
    return {
        "country": country.country_name,
        "region": country.region,
        "iso_code": country.iso_code,
        "governance_stability": risk.governance_stability_percentile if risk else None,
        "fx_volatility_12m": float(risk.fx_volatility_12m) if risk else None,
        "inflation_rate": float(risk.inflation_rate) if risk else None,
        "commodity_cards": commodity_cards
    }


@router.get("/commodity/{commodity_name}/cross-country")
def commodity_cross_country(
    commodity_name: str,
    db: Session = Depends(get_db)
):
    """
    Cross-country view for a specific commodity.
    Returns top exporters, importers, price trend, volatility regime.
    """
    commodity = db.query(Commodity).filter(
        Commodity.commodity_name.ilike(f"%{commodity_name}%")
    ).first()
    
    if not commodity:
        raise HTTPException(status_code=404, detail="Commodity not found")
    
    # Get latest time series
    ts = db.query(CommodityTimeSeries).filter(
        CommodityTimeSeries.commodity_id == commodity.id
    ).order_by(CommodityTimeSeries.period_date.desc()).first()
    
    # Get all lanes for this commodity
    lanes = db.query(TradeLane).filter(
        TradeLane.commodity_id == commodity.id
    ).all()
    
    exporters = {}
    importers = {}
    
    for lane in lanes:
        rec = db.query(Recommendation).filter(
            Recommendation.lane_id == lane.id
        ).order_by(Recommendation.final_score.desc()).first()
        
        if rec:
            if lane.direction == "Export":
                key = lane.origin_country.country_name
                exporters[key] = rec.final_score
            else:
                key = lane.destination_country.country_name
                importers[key] = rec.final_score
    
    return {
        "commodity": commodity_name,
        "unit": commodity.unit,
        "latest_price": float(ts.price_usd_per_unit) if ts else None,
        "price_source": ts.price_source if ts else None,
        "volatility_30d": float(ts.volatility_30d) if ts else None,
        "volatility_regime": "Low" if (ts and float(ts.volatility_30d) < 10) else ("Moderate" if (ts and float(ts.volatility_30d) < 20) else "High"),
        "trend_6m_direction": ts.trend_6m_direction if ts else None,
        "trend_6m_percent": float(ts.trend_6m_percent) if ts else None,
        "demand_season": ts.demand_season if ts else None,
        "top_exporters": sorted(exporters.items(), key=lambda x: x[1], reverse=True)[:5],
        "top_importers": sorted(importers.items(), key=lambda x: x[1], reverse=True)[:5],
        "period_date": ts.period_date.isoformat() if ts else None
    }


@router.get("/compliance/{recommendation_id}")
def compliance_audit_trail(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    Full audit trail and compliance checklist for a recommendation.
    Returns evidence sources, red flags, and compliance status.
    """
    rec = db.query(Recommendation).get(recommendation_id)
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    evidence = db.query(EvidenceSource).filter(
        EvidenceSource.recommendation_id == recommendation_id
    ).all()
    
    checklist = db.query(ComplianceChecklist).filter(
        ComplianceChecklist.recommendation_id == recommendation_id
    ).all()
    
    compliance_flags = db.query(ComplianceFlag).filter(
        ComplianceFlag.lane_id == rec.lane_id,
        ComplianceFlag.is_active == True
    ).all()
    
    return {
        "recommendation_id": recommendation_id,
        "lane": f"{rec.lane.origin_country.country_name} → {rec.lane.destination_country.country_name} ({rec.lane.commodity.commodity_name})",
        "direction": rec.lane.direction,
        "score": rec.final_score,
        "confidence": rec.confidence_level,
        "evidence_sources": [
            {
                "source_name": e.source_name,
                "source_url": e.source_url,
                "last_refreshed": e.last_refreshed.isoformat(),
                "snippet": e.snippet,
                "data_quality": e.data_quality
            }
            for e in evidence
        ],
        "compliance_flags": [
            {
                "flag_type": f.flag_type,
                "severity": f.severity,
                "description": f.description,
                "evidence_url": f.evidence_url
            }
            for f in compliance_flags
        ],
        "compliance_checklist": [
            {
                "item_name": c.item_name,
                "status": c.item_status,
                "notes": c.notes,
                "evidence_url": c.evidence_url,
                "required_action": c.required_action
            }
            for c in checklist
        ]
    }


@router.get("/stress-tests/{recommendation_id}")
def get_stress_tests(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """
    Returns detailed stress test results for a recommendation.
    Shows 3 scenarios: commodity shock, FX shock, trade disruption.
    """
    rec = db.query(Recommendation).get(recommendation_id)
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    stress_results = db.query(StressTestResult).filter(
        StressTestResult.recommendation_id == recommendation_id
    ).all()
    
    scenarios = {
        "commodity_shock": None,
        "fx_depreciation": None,
        "trade_disruption": None
    }
    
    for result in stress_results:
        scenario_key = result.scenario_type.lower().replace(" ", "_")
        if scenario_key in scenarios:
            scenarios[scenario_key] = {
                "description": result.scenario_description,
                "shock_percent": float(result.commodity_shock_percent) if result.commodity_shock_percent else None,
                "repayment_coverage_percent": float(result.repayment_coverage_percent),
                "resilience_score": result.resilience_score,
                "passes_threshold": result.passes_threshold
            }
    
    # Calculate aggregate confidence
    passing_scenarios = sum(1 for s in scenarios.values() if s and s["passes_threshold"])
    if passing_scenarios == 3:
        aggregate_confidence = "HIGH"
    elif passing_scenarios == 2:
        aggregate_confidence = "MEDIUM"
    else:
        aggregate_confidence = "LOW"
    
    return {
        "recommendation_id": recommendation_id,
        "lane": f"{rec.lane.origin_country.country_name} → {rec.lane.destination_country.country_name}",
        "commodity": rec.lane.commodity.commodity_name,
        "final_score": rec.final_score,
        "scenarios": scenarios,
        "passing_scenarios": passing_scenarios,
        "aggregate_confidence": aggregate_confidence,
        "recommendation": "Proceed with caution" if aggregate_confidence == "LOW" else ("Good for balanced portfolios" if aggregate_confidence == "MEDIUM" else "Excellent risk profile")
    }


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns high-level summary for dashboard overview page.
    """
    top_25 = db.query(Recommendation).filter(
        Recommendation.rank <= 25
    ).order_by(Recommendation.rank).all()
    
    avg_score = sum([r.final_score for r in top_25]) / len(top_25) if top_25 else 0
    high_confidence = len([r for r in top_25 if r.confidence_level == "HIGH"])
    medium_confidence = len([r for r in top_25 if r.confidence_level == "MEDIUM"])
    low_confidence = len([r for r in top_25 if r.confidence_level == "LOW"])
    
    # Get last updated timestamp
    latest_rec = db.query(Recommendation).order_by(
        Recommendation.created_at.desc()
    ).first()
    
    return {
        "total_opportunities_ranked": len(top_25),
        "average_score": round(avg_score, 1),
        "confidence_distribution": {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence
        },
        "last_updated": latest_rec.created_at.isoformat() if latest_rec else None,
        "next_update_expected": "First day of next month" if latest_rec else "Pending first run"
    }
