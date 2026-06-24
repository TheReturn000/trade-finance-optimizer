"""Database models for commodity reports system."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Country(Base):
    __tablename__ = "countries"
    
    id = Column(Integer, primary_key=True, index=True)
    country_name = Column(String(100), unique=True, nullable=False, index=True)
    iso_code = Column(String(3), unique=True, nullable=False)
    region = Column(String(50), nullable=False)
    currency = Column(String(3), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = relationship("CommodityPrice", back_populates="country")
    production = relationship("ProductionData", back_populates="country")
    legal_risks = relationship("LegalRisk", back_populates="country")
    climate_risks = relationship("ClimateRisk", back_populates="country")
    reports = relationship("MonthlyReport", back_populates="country")


class Commodity(Base):
    __tablename__ = "commodities"
    
    id = Column(Integer, primary_key=True, index=True)
    commodity_name = Column(String(50), unique=True, nullable=False, index=True)
    hs_code = Column(String(20), nullable=True)
    unit = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = relationship("CommodityPrice", back_populates="commodity")
    production = relationship("ProductionData", back_populates="commodity")
    legal_risks = relationship("LegalRisk", back_populates="commodity")
    climate_risks = relationship("ClimateRisk", back_populates="commodity")


class CommodityPrice(Base):
    __tablename__ = "commodity_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    price_usd = Column(Numeric(12, 4), nullable=False)
    volume_traded = Column(Float, nullable=True)  # in commodity units
    price_change_percent = Column(Numeric(6, 2), nullable=True)
    source = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="prices")
    commodity = relationship("Commodity", back_populates="prices")


class ProductionData(Base):
    __tablename__ = "production_data"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    production_volume = Column(Float, nullable=True)  # in commodity units
    capacity_utilization = Column(Numeric(5, 2), nullable=True)  # percentage
    forecast_next_month = Column(Float, nullable=True)
    forecast_confidence = Column(String(20), nullable=True)  # High/Medium/Low
    source = Column(String(100), nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="production")
    commodity = relationship("Commodity", back_populates="production")


class LegalRisk(Base):
    __tablename__ = "legal_risks"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    risk_type = Column(String(50), nullable=False)  # e.g., "Tariff Change", "Export Ban"
    severity = Column(String(20), nullable=False)  # Low/Medium/High/Critical
    description = Column(Text, nullable=False)
    tariff_rate = Column(Numeric(6, 2), nullable=True)  # percentage
    export_ban = Column(Boolean, default=False)
    import_ban = Column(Boolean, default=False)
    effective_date = Column(Date, nullable=True)
    source = Column(String(200), nullable=True)  # URL or reference
    impact_on_profit = Column(String(20), nullable=True)  # Positive/Negative/Neutral
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="legal_risks")
    commodity = relationship("Commodity", back_populates="legal_risks")


class ClimateRisk(Base):
    __tablename__ = "climate_risks"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    risk_type = Column(String(50), nullable=False)  # e.g., "Drought", "Flooding"
    severity = Column(String(20), nullable=False)  # Low/Medium/High/Critical
    description = Column(Text, nullable=False)
    weather_forecast = Column(Text, nullable=True)  # Climate/weather details
    impact_on_production = Column(Numeric(5, 2), nullable=True)  # percentage reduction
    esg_carbon_impact = Column(Text, nullable=True)  # ESG/carbon regulation impact
    mitigation_strategy = Column(Text, nullable=True)
    source = Column(String(200), nullable=True)  # NOAA, weather API, etc.
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="climate_risks")
    commodity = relationship("Commodity", back_populates="climate_risks")


class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    period_date = Column(Date, nullable=False, index=True)
    report_title = Column(String(200), nullable=False)
    summary = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)
    profit_outlook = Column(String(20), nullable=True)  # Positive/Neutral/Negative
    risk_rating = Column(String(20), nullable=True)  # Low/Medium/High
    pdf_path = Column(String(300), nullable=True)
    csv_export_path = Column(String(300), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    country = relationship("Country", back_populates="reports")
