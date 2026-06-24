"""Initialize database schema and seed data."""
from sqlalchemy import create_engine
from db.models import Base, Country, Commodity
from db.session import SessionLocal
from config import COUNTRIES, COMMODITIES, DATABASE_URL

def init_db():
    """Create all tables and seed initial data."""
    from db.session import engine
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    
    db = SessionLocal()
    
    # Check if data already exists
    if db.query(Country).first():
        print("⚠️ Data already exists, skipping seed.")
        db.close()
        return
    
    # Seed countries
    for country_data in COUNTRIES:
        country = Country(
            country_name=country_data["name"],
            iso_code=country_data["iso_code"],
            region=country_data["region"]
        )
        db.add(country)
    
    db.commit()
    print(f"✅ Added {len(COUNTRIES)} countries.")
    
    # Seed commodities
    for commodity_data in COMMODITIES:
        commodity = Commodity(
            commodity_name=commodity_data["name"],
            hs_code=commodity_data["hs_code"],
            unit=commodity_data["unit"]
        )
        db.add(commodity)
    
    db.commit()
    print(f"✅ Added {len(COMMODITIES)} commodities.")
    
    db.close()
    print("\n✅ Database initialization complete!")


if __name__ == "__main__":
    init_db()
