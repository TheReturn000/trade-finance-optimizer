from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), unique=True, nullable=False, index=True)
    region = Column(String(50), nullable=False)  # "Central America", "South America", "Caribbean"
    iso_code = Column(String(3), unique=True, nullable=True)
    iso_code_3 = Column(String(3), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    origin_lanes = relationship("TradeLane", foreign_keys="TradeLane.origin_country_id", back_populates="origin_country")
    destination_lanes = relationship("TradeLane", foreign_keys="TradeLane.destination_country_id", back_populates="destination_country")
    risk_indicators = relationship("CountryRiskIndicators", back_populates="country")


class Commodity(Base):
    __tablename__ = "commodities"
    
    id = Column(Integer, primary_key=True, index=True)
    commodity_name = Column(String(50), unique=True, nullable=False, index=True)
    hs_code_range = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String(20), nullable=True)  # e.g., "per barrel", "per tonne"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lanes = relationship("TradeLane", back_populates="commodity")
    time_series = relationship("CommodityTimeSeries", back_populates="commodity")


class TradeLane(Base):
    __tablename__ = "trade_lanes"
    
    id = Column(Integer, primary_key=True, index=True)
    origin_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    destination_country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    direction = Column(String(10), nullable=False)  # "Export" or "Import"
    annual_volume_estimate = Column(Float, nullable=True)  # metric tonnes
    annual_value_estimate = Column(Float, nullable=True)  # USD millions
    major_partners_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    origin_country = relationship("Country", foreign_keys=[origin_country_id], back_populates="origin_lanes")
    destination_country = relationship("Country", foreign_keys=[destination_country_id], back_populates="destination_lanes")
    commodity = relationship("Commodity", back_populates="lanes")
    trade_feasibility = relationship("TradeFeasibility", back_populates="lane")
    compliance_flags = relationship("ComplianceFlag", back_populates="lane")
    recommendations = relationship("Recommendation", back_populates="lane")


class CommodityTimeSeries(Base):
    __tablename__ = "commodity_time_series"
    
    id = Column(Integer, primary_key=True, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    price_usd_per_unit = Column(Numeric(10, 4), nullable=True)
    price_source = Column(String(200), nullable=True)
    volatility_30d = Column(Numeric(5, 2), nullable=True)  # annualized %
    volatility_60d = Column(Numeric(5, 2), nullable=True)
    volatility_90d = Column(Numeric(5, 2), nullable=True)
    trend_6m_direction = Column(String(20), nullable=True)  # "Up", "Stable", "Down"
    trend_6m_percent = Column(Numeric(5, 2), nullable=True)
    trend_12m_direction = Column(String(20), nullable=True)
    trend_12m_percent = Column(Numeric(5, 2), nullable=True)
    demand_season = Column(String(20), nullable=True)  # "High", "Moderate", "Low"
    supply_outlook = Column(String(200), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    commodity = relationship("Commodity", back_populates="time_series")


class CountryRiskIndicators(Base):
    __tablename__ = "country_risk_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    governance_stability_percentile = Column(Integer, nullable=True)  # 0-100 from WGI
    rule_of_law_percentile = Column(Integer, nullable=True)
    political_stability_percentile = Column(Integer, nullable=True)
    fx_volatility_12m = Column(Numeric(5, 2), nullable=True)  # annualized %
    inflation_rate = Column(Numeric(5, 2), nullable=True)  # current %
    gdp_growth_rate = Column(Numeric(5, 2), nullable=True)
    currency_code = Column(String(3), nullable=True)
    political_stability_score = Column(Integer, nullable=True)  # 0-100 proxy
    disruption_likelihood_score = Column(Integer, nullable=True)  # 0-100 proxy
    source_wgi_timestamp = Column(DateTime, nullable=True)
    source_imf_timestamp = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="risk_indicators")


class TradeFeasibility(Base):
    __tablename__ = "trade_feasibility"
    
    id = Column(Integer, primary_key=True, index=True)
    lane_id = Column(Integer, ForeignKey("trade_lanes.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    licensing_score = Column(Integer, nullable=True)  # 0-100
    licensing_notes = Column(Text, nullable=True)
    tariff_rate = Column(Numeric(5, 2), nullable=True)  # %
    tariff_friction_score = Column(Integer, nullable=True)  # 0-100
    customs_score = Column(Integer, nullable=True)  # 0-100
    facilitation_score = Column(Integer, nullable=True)  # 0-100
    feasibility_score = Column(Integer, nullable=True)  # 0-100 (blended)
    evidence_url = Column(Text, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lane = relationship("TradeLane", back_populates="trade_feasibility")


class ComplianceFlag(Base):
    __tablename__ = "compliance_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    lane_id = Column(Integer, ForeignKey("trade_lanes.id"), nullable=False, index=True)
    flag_type = Column(String(50), nullable=False)  # "OFAC", "UN_SANCTIONS", "EXPORT_BAN", "POLICY_CHANGE"
    severity = Column(Integer, nullable=False)  # 1-10 (1=minor, 10=critical)
    description = Column(Text, nullable=False)
    evidence_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lane = relationship("TradeLane", back_populates="compliance_flags")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    lane_id = Column(Integer, ForeignKey("trade_lanes.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    commodity_repayment_strength = Column(Integer, nullable=True)  # 0-100
    trade_feasibility = Column(Integer, nullable=True)  # 0-100
    geo_macro_stability = Column(Integer, nullable=True)  # 0-100
    operational_compliance = Column(Integer, nullable=True)  # 0-100
    final_score = Column(Integer, nullable=False)  # 0-100
    rank = Column(Integer, nullable=True)  # 1-25 for top picks
    confidence_level = Column(String(20), nullable=True)  # "High", "Medium", "Low"
    recommended_tenor_days = Column(Integer, default=180)
    lc_structure_hint = Column(Text, nullable=True)
    why_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lane = relationship("TradeLane", back_populates="recommendations")
    stress_tests = relationship("StressTestResult", back_populates="recommendation")
    evidence_sources = relationship("EvidenceSource", back_populates="recommendation")
    compliance_checklist = relationship("ComplianceChecklist", back_populates="recommendation")


class StressTestResult(Base):
    __tablename__ = "stress_test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False, index=True)
    scenario_type = Column(String(50), nullable=False)  # "Commodity_Shock", "FX_Depreciation", "Trade_Disruption"
    scenario_description = Column(Text, nullable=True)
    commodity_shock_percent = Column(Numeric(5, 2), nullable=True)
    fx_shock_percent = Column(Numeric(5, 2), nullable=True)
    repayment_coverage_percent = Column(Numeric(5, 2), nullable=False)
    resilience_score = Column(Integer, nullable=True)  # 0-100
    passes_threshold = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="stress_tests")


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True, index=True)
    trade_feasibility_id = Column(Integer, ForeignKey("trade_feasibility.id"), nullable=True, index=True)
    source_name = Column(String(200), nullable=False)  # "World Bank WGI", "UN Comtrade", etc.
    source_url = Column(Text, nullable=True)
    snippet = Column(Text, nullable=True)
    data_quality = Column(String(20), nullable=True)  # "High", "Medium", "Low"
    last_refreshed = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="evidence_sources")


class ComplianceChecklist(Base):
    __tablename__ = "compliance_checklist"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False, index=True)
    item_name = Column(String(200), nullable=False)
    item_status = Column(String(20), nullable=False)  # "Pass", "Flag", "Review"
    notes = Column(Text, nullable=True)
    evidence_url = Column(Text, nullable=True)
    required_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendation = relationship("Recommendation", back_populates="compliance_checklist")
