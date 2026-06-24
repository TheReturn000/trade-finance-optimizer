"""Configuration for Commodity Reports System."""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./commodity_reports.db")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "True") == "True"

# External APIs
WORLD_BANK_API = "https://api.worldbank.org/v2"
FAO_API = "http://fenixservices.fao.org/faostat/api/v1"
WTO_API = "https://www.wto.org"
NOAA_API = "https://www.ncei.noaa.gov/access/metadata/landing-page"
UN_COMTRADE_API = "https://comtradeplus.un.org"

# Scheduler Configuration
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "True") == "True"
WEEKLY_UPDATE_DAY = "monday"  # Day to run weekly updates
WEEKLY_UPDATE_HOUR = 9  # UTC hour
MONTHLY_REPORT_DAY = 1  # Day of month
MONTHLY_REPORT_HOUR = 10  # UTC hour

# Report Configuration
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./static/reports")
EXPORT_OUTPUT_DIR = os.getenv("EXPORT_OUTPUT_DIR", "./static/exports")
PDF_INCLUDE_CHARTS = True
PDF_INCLUDE_TABLES = True

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./logs/reports.log")

# Feature Flags
USE_CACHE = os.getenv("USE_CACHE", "True") == "True"
CACHE_TTL = 3600  # 1 hour in seconds
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"

# Commodities
COMMODITIES = [
    {"name": "Oil", "hs_code": "2709-2710", "unit": "barrel"},
    {"name": "Fertilizers", "hs_code": "3101-3105", "unit": "tonne"},
    {"name": "Maize", "hs_code": "1005", "unit": "tonne"},
    {"name": "Poultry", "hs_code": "0207", "unit": "tonne"},
    {"name": "Eggs", "hs_code": "0407", "unit": "tonne"},
    {"name": "Rice", "hs_code": "1006", "unit": "tonne"},
    {"name": "Beans", "hs_code": "0713", "unit": "tonne"},
]

# Countries (35+)
COUNTRIES = [
    # Central America
    {"name": "Guatemala", "iso_code": "GT", "region": "Central America"},
    {"name": "Honduras", "iso_code": "HN", "region": "Central America"},
    {"name": "El Salvador", "iso_code": "SV", "region": "Central America"},
    {"name": "Nicaragua", "iso_code": "NI", "region": "Central America"},
    {"name": "Costa Rica", "iso_code": "CR", "region": "Central America"},
    {"name": "Panama", "iso_code": "PA", "region": "Central America"},
    {"name": "Belize", "iso_code": "BZ", "region": "Central America"},
    # South America - North
    {"name": "Colombia", "iso_code": "CO", "region": "South America"},
    {"name": "Venezuela", "iso_code": "VE", "region": "South America"},
    {"name": "Guyana", "iso_code": "GY", "region": "South America"},
    {"name": "Suriname", "iso_code": "SR", "region": "South America"},
    {"name": "French Guiana", "iso_code": "GF", "region": "South America"},
    {"name": "Ecuador", "iso_code": "EC", "region": "South America"},
    # South America - Core
    {"name": "Brazil", "iso_code": "BR", "region": "South America"},
    {"name": "Peru", "iso_code": "PE", "region": "South America"},
    {"name": "Bolivia", "iso_code": "BO", "region": "South America"},
    # South America - South Cone
    {"name": "Chile", "iso_code": "CL", "region": "South America"},
    {"name": "Argentina", "iso_code": "AR", "region": "South America"},
    {"name": "Paraguay", "iso_code": "PY", "region": "South America"},
    {"name": "Uruguay", "iso_code": "UY", "region": "South America"},
    # Mexico
    {"name": "Mexico", "iso_code": "MX", "region": "North America"},
    # Caribbean
    {"name": "Cuba", "iso_code": "CU", "region": "Caribbean"},
    {"name": "Dominican Republic", "iso_code": "DO", "region": "Caribbean"},
    {"name": "Haiti", "iso_code": "HT", "region": "Caribbean"},
    {"name": "Jamaica", "iso_code": "JM", "region": "Caribbean"},
    {"name": "Trinidad and Tobago", "iso_code": "TT", "region": "Caribbean"},
    {"name": "Barbados", "iso_code": "BB", "region": "Caribbean"},
    {"name": "St. Lucia", "iso_code": "LC", "region": "Caribbean"},
    {"name": "Grenada", "iso_code": "GD", "region": "Caribbean"},
    {"name": "Antigua and Barbuda", "iso_code": "AG", "region": "Caribbean"},
    {"name": "Dominica", "iso_code": "DM", "region": "Caribbean"},
    {"name": "St. Vincent and the Grenadines", "iso_code": "VC", "region": "Caribbean"},
    {"name": "St. Kitts and Nevis", "iso_code": "KN", "region": "Caribbean"},
    {"name": "Bahamas", "iso_code": "BS", "region": "Caribbean"},
    {"name": "Puerto Rico", "iso_code": "PR", "region": "Caribbean"},
]

# Risk Levels
RISK_LEVELS = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

# Legal Risk Types
LEGAL_RISK_TYPES = [
    "Tariff Change",
    "Export Ban",
    "Import Ban",
    "Quota Reduction",
    "License Required",
    "Environmental Regulation",
    "Labor Law Change",
    "Currency Control",
    "Land Rights Issue",
    "Food Safety Standard",
]

# Climate Risk Types
CLIMATE_RISK_TYPES = [
    "Drought",
    "Flooding",
    "Hurricane/Storm",
    "Temperature Anomaly",
    "Pest Outbreak",
    "Seasonal Shift",
    "Carbon Regulation",
    "Infrastructure Disruption",
]
