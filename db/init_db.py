"""Initialize database schema and seed initial data."""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from db.models import Base, Country, Commodity
from db.session import SessionLocal

load_dotenv()

def init_db():
    """Create all tables and seed initial data."""
    
    # Create tables
    from db.session import engine
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    
    # Seed countries
    db = SessionLocal()
    
    # Check if countries already exist
    if db.query(Country).first():
        print("⚠️  Countries already exist, skipping seed.")
        db.close()
        return
    
    countries_data = [
        # Central America
        ("Guatemala", "Central America", "GTM", "GT"),
        ("Honduras", "Central America", "HND", "HN"),
        ("El Salvador", "Central America", "SLV", "SV"),
        ("Nicaragua", "Central America", "NIC", "NI"),
        ("Costa Rica", "Central America", "CRI", "CR"),
        ("Panama", "Central America", "PAN", "PA"),
        ("Belize", "Central America", "BLZ", "BZ"),
        
        # South America - North
        ("Colombia", "South America", "COL", "CO"),
        ("Venezuela", "South America", "VEN", "VE"),
        ("Guyana", "South America", "GUY", "GY"),
        ("Suriname", "South America", "SUR", "SR"),
        ("French Guiana", "South America", "GUF", "GF"),
        ("Ecuador", "South America", "ECU", "EC"),
        
        # South America - Core
        ("Brazil", "South America", "BRA", "BR"),
        ("Peru", "South America", "PER", "PE"),
        ("Bolivia", "South America", "BOL", "BO"),
        
        # South America - South Cone
        ("Chile", "South America", "CHL", "CL"),
        ("Argentina", "South America", "ARG", "AR"),
        ("Paraguay", "South America", "PRY", "PY"),
        ("Uruguay", "South America", "URY", "UY"),
        
        # Mexico (also Latin America)
        ("Mexico", "North America", "MEX", "MX"),
        
        # Caribbean - Major Islands
        ("Cuba", "Caribbean", "CUB", "CU"),
        ("Dominican Republic", "Caribbean", "DOM", "DO"),
        ("Haiti", "Caribbean", "HTI", "HT"),
        ("Jamaica", "Caribbean", "JAM", "JM"),
        ("Trinidad and Tobago", "Caribbean", "TTO", "TT"),
        ("Barbados", "Caribbean", "BRB", "BB"),
        ("St. Lucia", "Caribbean", "LCA", "LC"),
        ("Grenada", "Caribbean", "GRD", "GD"),
        ("Antigua and Barbuda", "Caribbean", "ATG", "AG"),
        ("Dominica", "Caribbean", "DMA", "DM"),
        ("St. Vincent and the Grenadines", "Caribbean", "VCT", "VC"),
        ("St. Kitts and Nevis", "Caribbean", "KNA", "KN"),
        ("Bahamas", "Caribbean", "BHS", "BS"),
        ("Puerto Rico", "Caribbean", "PRI", "PR"),
    ]
    
    for country_name, region, iso_3, iso_2 in countries_data:
        country = Country(
            country_name=country_name,
            region=region,
            iso_code_3=iso_3,
            iso_code=iso_2
        )
        db.add(country)
    
    db.commit()
    print(f"✅ Added {len(countries_data)} countries.")
    
    # Seed commodities
    commodities_data = [
        ("Oil", "2709-2710", "Crude oil and petroleum products", "barrel"),
        ("Poultry", "0207", "Poultry meat (chicken, duck, turkey)", "tonne"),
        ("Fertilizer", "3101-3105", "Mineral or chemical fertilizers", "tonne"),
        ("Corn", "1005", "Maize/corn grain", "tonne"),
        ("Soybeans", "1201", "Soybean seeds and products", "tonne"),
        ("Wheat", "1001", "Wheat grain", "tonne"),
    ]
    
    for commodity_name, hs_code, description, unit in commodities_data:
        commodity = Commodity(
            commodity_name=commodity_name,
            hs_code_range=hs_code,
            description=description,
            unit=unit
        )
        db.add(commodity)
    
    db.commit()
    print(f"✅ Added {len(commodities_data)} commodities.")
    
    db.close()
    print("\n✅ Database initialization complete!")


if __name__ == "__main__":
    init_db()
