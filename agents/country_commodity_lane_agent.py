"""Agent for mapping country-commodity trade lanes and volumes."""
import asyncio
from agents.base_agent import BaseAgent
from db.models import Country, Commodity, TradeLane
from datetime import datetime


class CountryCommodityLaneAgent(BaseAgent):
    """Maps export/import flows for commodities across countries."""
    
    def __init__(self, db):
        super().__init__(db, "CountryCommodityLaneAgent")
    
    async def execute(self, period_date):
        """Map all possible trade lanes."""
        self.log_info("Starting lane mapping...")
        
        try:
            countries = self.db.query(Country).all()
            commodities = self.db.query(Commodity).all()
            
            lane_count = 0
            
            # For each commodity, create lanes between countries
            for commodity in commodities:
                self.log_info(f"Processing commodity: {commodity.commodity_name}")
                
                for origin in countries:
                    for destination in countries:
                        if origin.id != destination.id:
                            # Export lane
                            export_lane = self.db.query(TradeLane).filter(
                                TradeLane.origin_country_id == origin.id,
                                TradeLane.destination_country_id == destination.id,
                                TradeLane.commodity_id == commodity.id,
                                TradeLane.direction == "Export"
                            ).first()
                            
                            if not export_lane:
                                export_lane = TradeLane(
                                    origin_country_id=origin.id,
                                    destination_country_id=destination.id,
                                    commodity_id=commodity.id,
                                    direction="Export"
                                )
                                self.db.add(export_lane)
                                lane_count += 1
            
            self.db.commit()
            self.log_info(f"Successfully mapped {lane_count} new lanes.")
            return {"status": "success", "lanes_created": lane_count}
        
        except Exception as e:
            self.log_error("Error mapping lanes", e)
            self.db.rollback()
            return {"status": "error", "message": str(e)}
