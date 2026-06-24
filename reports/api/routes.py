"""API routes for commodity reports."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from db.session import get_db
from db.models import Country, Commodity, CommodityPrice, LegalRisk, ClimateRisk, MonthlyReport
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1", tags=["reports"])


@router.get("/commodities")
def list_commodities(db: Session = Depends(get_db)):
    """List all tracked commodities."""
    commodities = db.query(Commodity).all()
    return [
        {
            "id": c.id,
            "name": c.commodity_name,
            "hs_code": c.hs_code,
            "unit": c.unit
        }
        for c in commodities
    ]


@router.get("/countries")
def list_countries(
    region: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List all countries, optionally filtered by region."""
    query = db.query(Country)
    if region:
        query = query.filter(Country.region.ilike(f"%{region}%"))
    
    countries = query.all()
    return [
        {
            "id": c.id,
            "name": c.country_name,
            "iso_code": c.iso_code,
            "region": c.region
        }
        for c in countries
    ]


@router.get("/prices/{country}/{commodity}")
def get_prices(
    country: str,
    commodity: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get recent commodity prices for a country."""
    country_obj = db.query(Country).filter(Country.country_name.ilike(country)).first()
    commodity_obj = db.query(Commodity).filter(Commodity.commodity_name.ilike(commodity)).first()
    
    if not country_obj or not commodity_obj:
        raise HTTPException(status_code=404, detail="Country or commodity not found")
    
    cutoff_date = datetime.utcnow().date() - timedelta(days=days)
    prices = db.query(CommodityPrice).filter(
        CommodityPrice.country_id == country_obj.id,
        CommodityPrice.commodity_id == commodity_obj.id,
        CommodityPrice.period_date >= cutoff_date
    ).order_by(CommodityPrice.period_date.desc()).all()
    
    return {
        "country": country_obj.country_name,
        "commodity": commodity_obj.commodity_name,
        "prices": [
            {
                "date": p.period_date.isoformat(),
                "price_usd": float(p.price_usd),
                "volume": p.volume_traded,
                "change_percent": float(p.price_change_percent) if p.price_change_percent else None
            }
            for p in prices
        ]
    }


@router.get("/legal-risks/{country}")
def get_legal_risks(
    country: str,
    commodity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get legal risks for a country, optionally filtered by commodity."""
    country_obj = db.query(Country).filter(Country.country_name.ilike(country)).first()
    
    if not country_obj:
        raise HTTPException(status_code=404, detail="Country not found")
    
    query = db.query(LegalRisk).filter(LegalRisk.country_id == country_obj.id)
    
    if commodity:
        commodity_obj = db.query(Commodity).filter(Commodity.commodity_name.ilike(commodity)).first()
        if commodity_obj:
            query = query.filter(LegalRisk.commodity_id == commodity_obj.id)
    
    risks = query.all()
    
    return {
        "country": country_obj.country_name,
        "legal_risks": [
            {
                "commodity": r.commodity.commodity_name if r.commodity else None,
                "risk_type": r.risk_type,
                "severity": r.severity,
                "description": r.description,
                "tariff_rate": float(r.tariff_rate) if r.tariff_rate else None,
                "export_ban": r.export_ban,
                "import_ban": r.import_ban,
                "effective_date": r.effective_date.isoformat() if r.effective_date else None,
                "impact_on_profit": r.impact_on_profit
            }
            for r in risks
        ]
    }


@router.get("/climate-risks/{country}")
def get_climate_risks(
    country: str,
    commodity: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get climate risks for a country, optionally filtered by commodity."""
    country_obj = db.query(Country).filter(Country.country_name.ilike(country)).first()
    
    if not country_obj:
        raise HTTPException(status_code=404, detail="Country not found")
    
    query = db.query(ClimateRisk).filter(ClimateRisk.country_id == country_obj.id)
    
    if commodity:
        commodity_obj = db.query(Commodity).filter(Commodity.commodity_name.ilike(commodity)).first()
        if commodity_obj:
            query = query.filter(ClimateRisk.commodity_id == commodity_obj.id)
    
    risks = query.all()
    
    return {
        "country": country_obj.country_name,
        "climate_risks": [
            {
                "commodity": r.commodity.commodity_name if r.commodity else None,
                "risk_type": r.risk_type,
                "severity": r.severity,
                "description": r.description,
                "weather_forecast": r.weather_forecast,
                "impact_on_production_percent": float(r.impact_on_production) if r.impact_on_production else None,
                "esg_carbon_impact": r.esg_carbon_impact,
                "mitigation_strategy": r.mitigation_strategy
            }
            for r in risks
        ]
    }


@router.get("/reports/{country}")
def get_reports(
    country: str,
    limit: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db)
):
    """Get monthly reports for a country."""
    country_obj = db.query(Country).filter(Country.country_name.ilike(country)).first()
    
    if not country_obj:
        raise HTTPException(status_code=404, detail="Country not found")
    
    reports = db.query(MonthlyReport).filter(
        MonthlyReport.country_id == country_obj.id
    ).order_by(MonthlyReport.period_date.desc()).limit(limit).all()
    
    return {
        "country": country_obj.country_name,
        "reports": [
            {
                "id": r.id,
                "period_date": r.period_date.isoformat(),
                "title": r.report_title,
                "summary": r.summary,
                "profit_outlook": r.profit_outlook,
                "risk_rating": r.risk_rating,
                "pdf_url": f"/static{r.pdf_path}" if r.pdf_path else None,
                "csv_url": f"/static{r.csv_export_path}" if r.csv_export_path else None
            }
            for r in reports
        ]
    }


@router.get("/heatmap/legal")
def get_legal_heatmap(db: Session = Depends(get_db)):
    """Get legal risk heatmap (countries × commodities)."""
    countries = db.query(Country).all()
    commodities = db.query(Commodity).all()
    
    heatmap = {}
    for country in countries:
        row = {}
        for commodity in commodities:
            risks = db.query(LegalRisk).filter(
                LegalRisk.country_id == country.id,
                LegalRisk.commodity_id == commodity.id
            ).all()
            
            # Calculate average severity
            if risks:
                severity_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
                avg_severity = sum(severity_map.get(r.severity, 0) for r in risks) / len(risks)
                row[commodity.commodity_name] = avg_severity
            else:
                row[commodity.commodity_name] = 0
        
        heatmap[country.country_name] = row
    
    return {"legal_risk_heatmap": heatmap}


@router.get("/heatmap/climate")
def get_climate_heatmap(db: Session = Depends(get_db)):
    """Get climate risk heatmap (countries × commodities)."""
    countries = db.query(Country).all()
    commodities = db.query(Commodity).all()
    
    heatmap = {}
    for country in countries:
        row = {}
        for commodity in commodities:
            risks = db.query(ClimateRisk).filter(
                ClimateRisk.country_id == country.id,
                ClimateRisk.commodity_id == commodity.id
            ).all()
            
            # Calculate average severity
            if risks:
                severity_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
                avg_severity = sum(severity_map.get(r.severity, 0) for r in risks) / len(risks)
                row[commodity.commodity_name] = avg_severity
            else:
                row[commodity.commodity_name] = 0
        
        heatmap[country.country_name] = row
    
    return {"climate_risk_heatmap": heatmap}
