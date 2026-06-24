# LatAm & Caribbean Commodity Reports System

## 📊 Overview

A comprehensive monthly reporting system that tracks commodity markets (Oil, Fertilizers, Maize, Poultry, Eggs, Rice, Beans) across all Central American, South American, and Caribbean countries.

**Key Features:**
- 📅 Monthly reports with weekly updates
- 🌍 Per-country analysis (35+ countries)
- ⚖️ Legal risk assessment (tariffs, regulations, trade restrictions)
- 🌡️ Climate risk analysis (weather, seasonal patterns, ESG impact)
- 📈 Price trends & production forecasts
- 📥 Downloadable PDF reports
- 🔔 Automated weekly data refresh

## 🌾 Commodities Tracked

1. **Oil** (HS 2709-2710) - Energy/export commodity
2. **Fertilizers** (HS 3101-3105) - Agricultural input
3. **Maize** (HS 1005) - Food staple
4. **Poultry** (HS 0207) - Protein source
5. **Eggs** (HS 0407) - Protein source
6. **Rice** (HS 1006) - Food staple
7. **Beans** (HS 0713) - Food staple/legume

## 🌎 Geographic Scope

### Central America (7)
Guatemala, Honduras, El Salvador, Nicaragua, Costa Rica, Panama, Belize

### South America (14)
Colombia, Venezuela, Guyana, Suriname, French Guiana, Ecuador, Brazil, Peru, Bolivia, Chile, Argentina, Paraguay, Uruguay

### Caribbean (15+)
Cuba, Dominican Republic, Haiti, Jamaica, Trinidad & Tobago, Barbados, St. Lucia, Grenada, Antigua & Barbuda, Dominica, St. Vincent & Grenadines, St. Kitts & Nevis, Bahamas, Puerto Rico

**Total: 35+ countries**

## 🗂️ Project Structure

```
reports/
├── README.md
├── requirements.txt
├── config.py
├── db/
│   ├── __init__.py
│   ├── models.py           # Database models for reports
│   ├── session.py          # DB connection
│   └── init_db.py          # Initialize schema
├── data_sources/
│   ├── __init__.py
│   ├── world_bank.py       # Commodity price API
│   ├── fao.py              # Agricultural production data
│   ├── weather_api.py      # Climate/weather data
│   ├── wto.py              # Trade policy data
│   └── national_stats.py   # Country-specific data
├── agents/
│   ├── __init__.py
│   ├── commodity_collector.py    # Weekly price/volume updater
│   ├── legal_risk_analyzer.py    # Tariff & regulation checker
│   ├── climate_risk_analyzer.py  # Weather & seasonal analysis
│   └── report_generator.py       # Monthly PDF report builder
├── api/
│   ├── __init__.py
│   ├── main.py             # FastAPI app
│   ├── routes.py           # API endpoints
│   └── schemas.py          # Pydantic models
├── dashboard/
│   ├── __init__.py
│   ├── app.py              # Streamlit main dashboard
│   ├── pages/
│   │   ├── 01_Overview.py
│   │   ├── 02_Country_Deep_Dive.py
│   │   ├── 03_Commodity_Analysis.py
│   │   ├── 04_Risk_Assessment.py
│   │   └── 05_Reports.py
│   └── utils.py            # Dashboard utilities
├── tasks/
│   ├── __init__.py
│   ├── weekly_update.py    # Weekly data refresh job
│   ├── monthly_report.py   # Monthly report generator
│   └── scheduler.py        # Task scheduler
├── utils/
│   ├── __init__.py
│   ├── pdf_generator.py    # PDF report creation
│   ├── charts.py           # Chart generation
│   ├── constants.py        # Country/commodity lists
│   └── helpers.py          # Helper functions
└── static/
    ├── reports/            # Generated PDF reports
    └── exports/            # Downloadable data files
```

## 🗄️ Database Schema

### Core Tables

**countries**
- id, country_name, region, iso_code, currency

**commodities**
- id, commodity_name, hs_code, unit

**commodity_prices** (Weekly updates)
- id, country_id, commodity_id, period_date, price_usd, volume_traded, source

**production_data** (Monthly)
- id, country_id, commodity_id, period_date, production_volume, capacity_utilization, forecast_next_month

**legal_risks** (Quarterly review)
- id, country_id, commodity_id, risk_type, description, tariff_rate, export_ban, import_ban, last_updated

**climate_risks** (Real-time)
- id, country_id, commodity_id, risk_type, severity, description, impact_on_production, weather_forecast

**monthly_reports** (Generated monthly)
- id, country_id, period_date, report_content, pdf_path, summary, key_risks

## 📅 Update Schedule

**Weekly (Every Monday 9 AM UTC)**
- Fetch latest commodity prices from World Bank
- Update trade volumes from UN Comtrade
- Refresh weather/climate data from NOAA
- Check for new trade policy announcements

**Monthly (1st of each month)**
- Compile comprehensive monthly report
- Analyze trends & anomalies
- Generate country-specific PDF reports
- Calculate risk scores
- Email alerts to stakeholders

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python db/init_db.py
```

### 3. Run API
```bash
python -m uvicorn api.main:app --reload
```

### 4. Run Dashboard
```bash
streamlit run dashboard/app.py
```

### 5. Start Scheduler
```bash
python tasks/scheduler.py
```

## 📊 Dashboard Pages

### 1. Overview
- Global commodity price index
- Top 5 price movers (up/down)
- Risk heat map (legal + climate)
- Latest news/alerts

### 2. Country Deep Dive
- Select any LatAm/Caribbean country
- 7 commodity cards with:
  - Current price & trend
  - Production forecast
  - Legal risks specific to that commodity in that country
  - Climate risks & weather alerts
  - Export/import feasibility

### 3. Commodity Analysis
- Select any of 7 commodities
- Price trends across all countries
- Top producers/exporters
- Top importers
- Price volatility by country
- Supply/demand outlook

### 4. Risk Assessment
- Legal risk matrix (countries × commodities)
- Climate risk severity map
- Red flags & alerts
- Regulatory changes
- Trade policy updates

### 5. Reports
- Download monthly PDF reports
- Filter by country & commodity
- Historical reports archive
- Export as CSV/Excel

## 🔌 API Endpoints

```
GET  /api/v1/commodities               # List all commodities
GET  /api/v1/countries                 # List all countries
GET  /api/v1/prices/{country}/{commodity}  # Latest prices
GET  /api/v1/production/{country}/{commodity}  # Production data
GET  /api/v1/legal-risks/{country}     # Legal risks for country
GET  /api/v1/climate-risks/{country}   # Climate risks for country
GET  /api/v1/reports/{country}/{date}  # Download monthly report
GET  /api/v1/heatmap/legal             # Legal risk heatmap
GET  /api/v1/heatmap/climate           # Climate risk heatmap
POST /api/v1/export/csv                # Export data to CSV
```

## ⚖️ Legal Risk Categories

Per country & commodity:

1. **Tariffs** - Import/export duties
2. **Trade Restrictions** - Bans, quotas, licenses
3. **Environmental Regulations** - ESG compliance
4. **Food Safety Standards** - Health certifications
5. **Labor Regulations** - Worker protections
6. **Currency Controls** - FX restrictions on repatriation
7. **Land Rights** - Tenure & property issues
8. **Recent Policy Changes** - New laws affecting trade

## 🌍 Climate Risk Categories

Per country & commodity:

1. **Drought Risk** - Water scarcity
2. **Flooding Risk** - Heavy rainfall
3. **Hurricane/Storm Risk** - Seasonal storms
4. **Temperature Anomalies** - Unusual heat/cold
5. **Pest Outbreaks** - Crop diseases
6. **Seasonal Timing** - Planting/harvest impact
7. **ESG/Carbon Impact** - Regulatory carbon costs
8. **Infrastructure Disruption** - Port/transport impacts

## 📈 Report Contents (Monthly PDF)

Per country:

1. **Executive Summary**
   - Key findings
   - Risk rating (Low/Medium/High)
   - Profit outlook

2. **Commodity Analysis**
   - Price trends (6M, 12M)
   - Production forecast
   - Supply/demand outlook
   - Volatility assessment

3. **Legal Risk Assessment**
   - Tariff analysis
   - Trade restrictions
   - Policy changes
   - Compliance requirements

4. **Climate Risk Assessment**
   - Weather forecasts
   - Seasonal impacts
   - Production risks
   - Mitigation strategies

5. **Profit Impact Analysis**
   - Scenarios (base, upside, downside)
   - Margin pressure points
   - Hedging recommendations

6. **Recommendations**
   - Best opportunities
   - Risk mitigation strategies
   - Timing recommendations

## 🔄 Data Sources

| Source | Data | Update Frequency |
|--------|------|------------------|
| World Bank | Commodity prices | Weekly |
| FAO | Production volumes | Monthly |
| UN Comtrade | Trade flows | Weekly |
| NOAA | Weather/climate | Daily |
| WTO | Trade policies | As published |
| National Stats | Country-specific | Monthly |
| Bloomberg | Market sentiment | Real-time |

## 🛡️ Security

- Environment variables for API keys
- Database encryption for sensitive data
- PDF reports password-protected (optional)
- Access control for premium reports

## 📧 Notifications

- Email alerts for:
  - Price spikes (>10% move)
  - New trade restrictions
  - Climate warnings
  - Policy changes
  - Monthly report ready

## 📱 Future Enhancements

- [ ] Mobile app (iOS/Android)
- [ ] Real-time price streaming
- [ ] ML-based price forecasting
- [ ] Portfolio optimization tool
- [ ] Integration with trading platforms
- [ ] SMS alerts
- [ ] Chatbot Q&A

## 📞 Support

For issues or feature requests, open an issue on GitHub.

---

**Version:** 1.0.0  
**Last Updated:** June 2024  
**Maintained by:** TheReturn000
