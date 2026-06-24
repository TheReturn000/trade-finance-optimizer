"""Main Streamlit dashboard for commodity reports."""
import streamlit as st
import pandas as pd
from db.session import SessionLocal
from db.models import Country, Commodity, CommodityPrice, LegalRisk, ClimateRisk, MonthlyReport
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="LatAm Commodity Reports", layout="wide")

st.title("🌍 LatAm & Caribbean Commodity Reports")
st.markdown("**Weekly updates on Oil, Fertilizers, Maize, Poultry, Eggs, Rice, and Beans**")
st.markdown("*Including Legal & Climate Risk Analysis*")

# Sidebar Navigation
with st.sidebar:
    st.header("📋 Navigation")
    page = st.radio("Select Page:", [
        "📊 Overview",
        "🏴 Country Report",
        "🌾 Commodity Analysis",
        "⚖️ Legal Risks",
        "🌦️ Climate Risks",
        "📄 Monthly Reports"
    ])
    
    st.divider()
    st.caption("**Last Updated:** Weekly Monday 9 AM UTC")
    st.caption("**Data Sources:** World Bank, FAO, UN Comtrade, NOAA")

# Database connection
def get_db():
    return SessionLocal()

db = get_db()

if page == "📊 Overview":
    st.header("Global Commodity Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        country_count = db.query(Country).count()
        st.metric("Countries Tracked", country_count)
    with col2:
        commodity_count = db.query(Commodity).count()
        st.metric("Commodities", commodity_count)
    with col3:
        price_count = db.query(CommodityPrice).count()
        st.metric("Price Records", price_count)
    
    st.divider()
    
    st.subheader("Latest Commodity Prices (All Countries)")
    
    # Get latest prices
    prices = db.query(CommodityPrice).order_by(
        CommodityPrice.period_date.desc()
    ).limit(35).all()
    
    price_data = []
    for p in prices:
        price_data.append({
            "Country": p.country.country_name,
            "Commodity": p.commodity.commodity_name,
            "Price (USD)": float(p.price_usd),
            "Change %": float(p.price_change_percent) if p.price_change_percent else 0,
            "Date": p.period_date.isoformat()
        })
    
    if price_data:
        df = pd.DataFrame(price_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No price data available yet. Data populates weekly.")

elif page == "🏴 Country Report":
    st.header("Country Deep Dive Report")
    
    db = get_db()
    countries = db.query(Country).order_by(Country.country_name).all()
    country_options = [c.country_name for c in countries]
    
    selected_country = st.selectbox("Select Country:", country_options)
    
    country = db.query(Country).filter(Country.country_name == selected_country).first()
    
    if country:
        st.subheader(f"{country.country_name} ({country.region})")
        
        # Get all commodities
        commodities = db.query(Commodity).all()
        
        for commodity in commodities:
            with st.expander(f"📦 {commodity.commodity_name}"):
                col1, col2 = st.columns(2)
                
                # Price data
                with col1:
                    st.markdown("**Price Information**")
                    latest_price = db.query(CommodityPrice).filter(
                        CommodityPrice.country_id == country.id,
                        CommodityPrice.commodity_id == commodity.id
                    ).order_by(CommodityPrice.period_date.desc()).first()
                    
                    if latest_price:
                        st.metric("Latest Price", f"${float(latest_price.price_usd):.2f} {commodity.unit}", 
                                 delta=f"{float(latest_price.price_change_percent) if latest_price.price_change_percent else 0}%")
                        st.caption(f"Date: {latest_price.period_date}")
                    else:
                        st.info("No price data available")
                
                # Legal risks
                with col2:
                    st.markdown("**Legal Risks**")
                    legal_risks = db.query(LegalRisk).filter(
                        LegalRisk.country_id == country.id,
                        LegalRisk.commodity_id == commodity.id
                    ).all()
                    
                    if legal_risks:
                        for risk in legal_risks[:3]:
                            st.warning(f"{risk.risk_type} ({risk.severity})")
                            st.caption(risk.description[:100] + "..." if len(risk.description) > 100 else risk.description)
                    else:
                        st.success("No legal risks flagged")
                
                # Climate risks
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown("**Climate Risks**")
                    climate_risks = db.query(ClimateRisk).filter(
                        ClimateRisk.country_id == country.id,
                        ClimateRisk.commodity_id == commodity.id
                    ).all()
                    
                    if climate_risks:
                        for risk in climate_risks[:3]:
                            st.warning(f"{risk.risk_type} ({risk.severity})")
                            st.caption(risk.description[:100] + "..." if len(risk.description) > 100 else risk.description)
                    else:
                        st.success("No climate risks flagged")
                
                with col4:
                    st.markdown("**Production Data**")
                    from db.models import ProductionData
                    prod = db.query(ProductionData).filter(
                        ProductionData.country_id == country.id,
                        ProductionData.commodity_id == commodity.id
                    ).order_by(ProductionData.period_date.desc()).first()
                    
                    if prod:
                        st.metric("Latest Production", f"{prod.production_volume:.0f} {commodity.unit}")
                        st.caption(f"Capacity: {float(prod.capacity_utilization)}%" if prod.capacity_utilization else "Capacity: N/A")
                    else:
                        st.info("No production data")

elif page == "🌾 Commodity Analysis":
    st.header("Commodity Analysis Across All Countries")
    
    db = get_db()
    commodities = db.query(Commodity).all()
    commodity_options = [c.commodity_name for c in commodities]
    
    selected_commodity = st.selectbox("Select Commodity:", commodity_options)
    
    commodity = db.query(Commodity).filter(Commodity.commodity_name == selected_commodity).first()
    
    if commodity:
        st.subheader(f"{commodity.commodity_name} ({commodity.hs_code})")
        st.caption(f"Unit: {commodity.unit}")
        
        # Get all prices for this commodity
        prices = db.query(CommodityPrice).filter(
            CommodityPrice.commodity_id == commodity.id
        ).all()
        
        if prices:
            price_data = []
            for p in prices:
                price_data.append({
                    "Country": p.country.country_name,
                    "Price (USD)": float(p.price_usd),
                    "Date": p.period_date.isoformat()
                })
            
            df = pd.DataFrame(price_data)
            
            # Price trend chart
            fig = px.line(df, x="Date", y="Price (USD)", color="Country", 
                          title=f"{commodity.commodity_name} Price Trends")
            st.plotly_chart(fig, use_container_width=True)
            
            # Price table
            st.dataframe(df.sort_values("Price (USD)", ascending=False), use_container_width=True)
        else:
            st.info("No price data available for this commodity")

elif page == "⚖️ Legal Risks":
    st.header("Legal Risk Assessment")
    
    db = get_db()
    
    tab1, tab2 = st.tabs(["By Country", "Risk Heatmap"])
    
    with tab1:
        countries = db.query(Country).order_by(Country.country_name).all()
        selected_country = st.selectbox("Select Country:", [c.country_name for c in countries], key="legal_country")
        
        country = db.query(Country).filter(Country.country_name == selected_country).first()
        
        if country:
            legal_risks = db.query(LegalRisk).filter(LegalRisk.country_id == country.id).all()
            
            if legal_risks:
                for risk in legal_risks:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.subheader(f"{risk.commodity.commodity_name if risk.commodity else 'General'} - {risk.risk_type}")
                        st.write(risk.description)
                        if risk.tariff_rate:
                            st.caption(f"Tariff Rate: {float(risk.tariff_rate)}%")
                        if risk.export_ban:
                            st.warning("⚠️ Export Ban in Effect")
                        if risk.import_ban:
                            st.warning("⚠️ Import Ban in Effect")
                    with col2:
                        if risk.severity == "Critical":
                            st.error(risk.severity)
                        elif risk.severity == "High":
                            st.warning(risk.severity)
                        else:
                            st.info(risk.severity)
            else:
                st.success("✅ No legal risks flagged for this country")
    
    with tab2:
        st.markdown("**Legal Risk Heatmap (Countries × Commodities)**")
        st.info("Heatmap visualization would show risk severity for each country-commodity combination")

elif page == "🌦️ Climate Risks":
    st.header("Climate Risk Assessment")
    
    db = get_db()
    
    countries = db.query(Country).order_by(Country.country_name).all()
    selected_country = st.selectbox("Select Country:", [c.country_name for c in countries], key="climate_country")
    
    country = db.query(Country).filter(Country.country_name == selected_country).first()
    
    if country:
        climate_risks = db.query(ClimateRisk).filter(ClimateRisk.country_id == country.id).all()
        
        if climate_risks:
            for risk in climate_risks:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{risk.commodity.commodity_name if risk.commodity else 'General'} - {risk.risk_type}")
                    st.write(risk.description)
                    if risk.impact_on_production:
                        st.caption(f"Production Impact: -{float(risk.impact_on_production)}%")
                    if risk.weather_forecast:
                        st.caption(f"Forecast: {risk.weather_forecast}")
                    if risk.esg_carbon_impact:
                        st.warning(f"ESG/Carbon: {risk.esg_carbon_impact}")
                with col2:
                    if risk.severity == "Critical":
                        st.error(risk.severity)
                    elif risk.severity == "High":
                        st.warning(risk.severity)
                    else:
                        st.info(risk.severity)
        else:
            st.success("✅ No climate risks flagged for this country")

elif page == "📄 Monthly Reports":
    st.header("Monthly Reports Archive")
    
    db = get_db()
    countries = db.query(Country).order_by(Country.country_name).all()
    selected_country = st.selectbox("Select Country:", [c.country_name for c in countries], key="reports_country")
    
    country = db.query(Country).filter(Country.country_name == selected_country).first()
    
    if country:
        reports = db.query(MonthlyReport).filter(
            MonthlyReport.country_id == country.id
        ).order_by(MonthlyReport.period_date.desc()).all()
        
        if reports:
            for report in reports:
                with st.expander(f"📅 {report.period_date.strftime('%B %Y')} - {report.report_title}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if report.profit_outlook == "Positive":
                            st.success(f"Profit Outlook: {report.profit_outlook}")
                        elif report.profit_outlook == "Negative":
                            st.error(f"Profit Outlook: {report.profit_outlook}")
                        else:
                            st.info(f"Profit Outlook: {report.profit_outlook}")
                    with col2:
                        if report.risk_rating == "High":
                            st.error(f"Risk: {report.risk_rating}")
                        elif report.risk_rating == "Medium":
                            st.warning(f"Risk: {report.risk_rating}")
                        else:
                            st.success(f"Risk: {report.risk_rating}")
                    with col3:
                        st.caption(f"Generated: {report.generated_at.strftime('%Y-%m-%d')}")
                    
                    if report.summary:
                        st.markdown("**Summary**")
                        st.write(report.summary)
                    
                    if report.key_findings:
                        st.markdown("**Key Findings**")
                        st.write(report.key_findings)
                    
                    if report.pdf_path:
                        st.markdown(f"[📥 Download PDF Report]({report.pdf_path})")
                    if report.csv_export_path:
                        st.markdown(f"[📥 Download CSV Data]({report.csv_export_path})")
        else:
            st.info(f"No reports available for {country.country_name} yet")

db.close()

st.divider()
st.caption("LatAm & Caribbean Commodity Reports v1.0 | Updated Weekly | All Times UTC")
