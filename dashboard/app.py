import streamlit as st
import pandas as pd
from db.session import SessionLocal
from db.models import Recommendation, Country, Commodity, TradeLane, EvidenceSource, ComplianceChecklist
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Trade Finance Optimizer", layout="wide")

# Database connection
def get_data():
    db = SessionLocal()
    recs = db.query(Recommendation).filter(
        Recommendation.rank <= 25
    ).order_by(Recommendation.rank).all()
    db.close()
    return recs

st.title("🌍 Trade Finance Optimizer - Multi-Agent System")
st.markdown("**Identifying optimal LC opportunities across Latin America, Central America & Caribbean**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Filters")
    view = st.radio("Select View:", [
        "📊 Overview",
        "🔥 Heatmap",
        "🇧🇷 Country Deep Dive",
        "🌾 Commodity Insights",
        "🏦 Compliance"
    ])

# Load data
recommendations = get_data()

if not recommendations:
    st.warning("⚠️ No recommendations available. Run the monthly job first.")
else:
    # ===== OVERVIEW PAGE =====
    if view == "📊 Overview":
        st.header("Top 25 Lending Opportunities (180-Day Tenor)")
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_score = sum([r.final_score for r in recommendations]) / len(recommendations)
            st.metric("Avg Score", f"{avg_score:.0f}/100")
        with col2:
            high_conf = len([r for r in recommendations if r.confidence_level == "HIGH"])
            st.metric("High Confidence", high_conf)
        with col3:
            med_conf = len([r for r in recommendations if r.confidence_level == "MEDIUM"])
            st.metric("Medium Confidence", med_conf)
        with col4:
            low_conf = len([r for r in recommendations if r.confidence_level == "LOW"])
            st.metric("Low Confidence", low_conf)
        
        st.divider()
        
        # Top 25 table
        st.subheader("Ranked Opportunities")
        table_data = []
        for r in recommendations:
            table_data.append({
                "Rank": r.rank,
                "Origin": r.lane.origin_country.country_name,
                "Destination": r.lane.destination_country.country_name,
                "Commodity": r.lane.commodity.commodity_name,
                "Direction": r.lane.direction,
                "Score": r.final_score,
                "Confidence": r.confidence_level,
                "Commodity Str.": r.commodity_repayment_strength,
                "Trade Feas.": r.trade_feasibility,
                "Geo/Macro": r.geo_macro_stability
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "top_25.csv", "text/csv")
        
        # Score distribution chart
        st.subheader("Score Distribution")
        fig = px.histogram(df, x="Score", nbins=10, title="Distribution of Opportunity Scores")
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== HEATMAP PAGE =====
    elif view == "🔥 Heatmap":
        st.header("Country × Commodity Opportunity Heatmap")
        
        db = SessionLocal()
        countries = db.query(Country).all()
        commodities = db.query(Commodity).all()
        
        # Build heatmap matrix
        heatmap_data = []
        for country in countries:
            row = []
            for commodity in commodities:
                lane = db.query(TradeLane).filter(
                    ((TradeLane.origin_country_id == country.id) |
                     (TradeLane.destination_country_id == country.id)),
                    TradeLane.commodity_id == commodity.id
                ).first()
                
                if lane:
                    rec = db.query(Recommendation).filter(
                        Recommendation.lane_id == lane.id
                    ).order_by(Recommendation.final_score.desc()).first()
                    row.append(rec.final_score if rec else 0)
                else:
                    row.append(0)
            heatmap_data.append(row)
        
        db.close()
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=[c.commodity_name for c in commodities],
            y=[c.country_name for c in countries],
            colorscale="RdYlGn",
            zmid=50
        ))
        fig.update_layout(title="Opportunity Score Heatmap", height=700)
        st.plotly_chart(fig, use_container_width=True)
    
    # ===== COUNTRY DEEP DIVE =====
    elif view == "🇧🇷 Country Deep Dive":
        st.header("Country-Level Deep Dive")
        
        db = SessionLocal()
        countries = db.query(Country).all()
        selected_country = st.selectbox(
            "Select Country:",
            [c.country_name for c in countries]
        )
        
        country = db.query(Country).filter(
            Country.country_name == selected_country
        ).first()
        
        if country:
            st.subheader(f"{country.country_name} ({country.region})")
            
            lanes = db.query(TradeLane).filter(
                (TradeLane.origin_country_id == country.id) |
                (TradeLane.destination_country_id == country.id)
            ).all()
            
            for lane in lanes:
                rec = db.query(Recommendation).filter(
                    Recommendation.lane_id == lane.id
                ).order_by(Recommendation.final_score.desc()).first()
                
                if rec:
                    with st.expander(f"{lane.commodity.commodity_name} ({lane.direction})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Score", rec.final_score, delta="out of 100")
                        with col2:
                            st.metric("Confidence", rec.confidence_level)
                        with col3:
                            st.metric("Tenor", f"{rec.recommended_tenor_days} days")
                        
                        st.markdown("**Why:**")
                        st.write(rec.why_explanation or "No explanation available")
                        
                        st.markdown("**LC Structure:**")
                        st.write(rec.lc_structure_hint or "No structure hint available")
        
        db.close()
    
    # ===== COMMODITY INSIGHTS =====
    elif view == "🌾 Commodity Insights":
        st.header("Cross-Country Commodity Analysis")
        
        db = SessionLocal()
        commodities = db.query(Commodity).all()
        selected_commodity = st.selectbox(
            "Select Commodity:",
            [c.commodity_name for c in commodities]
        )
        
        commodity = db.query(Commodity).filter(
            Commodity.commodity_name == selected_commodity
        ).first()
        
        if commodity:
            st.subheader(f"{commodity.commodity_name}")
            st.write(f"**HS Code:** {commodity.hs_code_range}")
            st.write(f"**Unit:** {commodity.unit}")
            
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
                        exporters[lane.origin_country.country_name] = rec.final_score
                    else:
                        importers[lane.destination_country.country_name] = rec.final_score
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Top Exporters**")
                top_exp = sorted(exporters.items(), key=lambda x: x[1], reverse=True)[:5]
                for country, score in top_exp:
                    st.write(f"{country}: {score}/100")
            
            with col2:
                st.markdown("**Top Importers**")
                top_imp = sorted(importers.items(), key=lambda x: x[1], reverse=True)[:5]
                for country, score in top_imp:
                    st.write(f"{country}: {score}/100")
        
        db.close()
    
    # ===== COMPLIANCE =====
    elif view == "🏦 Compliance":
        st.header("Compliance & Evidence Audit Trail")
        
        selected_rec = st.selectbox(
            "Select Recommendation:",
            [f"#{r.rank}: {r.lane.origin_country.country_name} → {r.lane.destination_country.country_name} ({r.lane.commodity.commodity_name})" for r in recommendations]
        )
        
        rec_idx = int(selected_rec.split(":")[0].replace("#", "")) - 1
        if 0 <= rec_idx < len(recommendations):
            rec = recommendations[rec_idx]
            
            st.subheader(f"Compliance Status: {rec.confidence_level}")
            st.write(f"**Lane:** {rec.lane.origin_country.country_name} → {rec.lane.destination_country.country_name} ({rec.lane.commodity.commodity_name})")
            st.write(f"**Score:** {rec.final_score}/100")
            
            db = SessionLocal()
            
            # Show evidence
            evidence = db.query(EvidenceSource).filter(
                EvidenceSource.recommendation_id == rec.id
            ).all()
            
            if evidence:
                st.subheader("📎 Evidence Sources")
                for e in evidence:
                    st.write(f"[{e.source_name}]({e.source_url})")
            
            db.close()

st.divider()
st.caption("Trade Finance Optimizer v1.0 | Last updated: June 2024")
