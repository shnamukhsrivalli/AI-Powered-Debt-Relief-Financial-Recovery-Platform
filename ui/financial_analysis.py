import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.repository import get_profile, get_incomes, get_expenses, get_debts, save_analysis, get_latest_analysis
from financial.analyzer import calculate_financial_metrics
from financial.health_score import calculate_health_score

def show_financial_analysis(db, user):
    st.title("📊 Financial Analysis")
    st.write("Examine your debt ratios, monthly budget metrics, and deterministic Financial Health Score.")
    
    # 1. Fetch data
    profile = get_profile(db, user.id)
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    debts = get_debts(db, user.id)
    
    if not incomes and not expenses:
        st.warning("⚠️ No cash flow data. Please add your Income & Expenses first.")
        st.info("Navigate to the **💰 Income & Expenses** tab in the sidebar to add entries.")
        return
        
    # Calculate metrics
    metrics = calculate_financial_metrics(incomes, expenses, debts)
    active_debts = [d for d in debts if d.status == "Active"]
    
    # Calculate Health Score
    hs_data = calculate_health_score(metrics, debts)
    health_score = hs_data["health_score"]
    risk_level = hs_data["risk_level"]
    positive_factors = hs_data["positive_factors"]
    negative_factors = hs_data["negative_factors"]
    improvement_areas = hs_data["improvement_areas"]
    
    # Save analysis in database for tracking/history
    save_analysis(
        db,
        user_id=user.id,
        total_debt=metrics["total_debt"],
        total_monthly_payment=metrics["total_monthly_debt_payment"],
        debt_to_income_ratio=metrics["dti_ratio"],
        expense_to_income_ratio=metrics["expense_to_income_ratio"],
        disposable_income=metrics["disposable_income"],
        savings_rate=metrics["savings_rate"],
        health_score=health_score,
        risk_level=risk_level
    )
    
    # ------------------ TOP HEALTH SCORE CONTAINER ------------------
    st.subheader("Financial Health Assessment")
    
    col_hs1, col_hs2 = st.columns([1, 2])
    
    with col_hs1:
        # Create a beautiful circular gauge chart for the health score
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = health_score,
            title = {'text': "Health Score", 'font': {'size': 20, 'color': '#ffffff'}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#8b949e"},
                'bar': {'color': "#388bfd"},
                'bgcolor': "rgba(30, 37, 53, 0.4)",
                'borderwidth': 2,
                'bordercolor': "#232834",
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(248, 81, 73, 0.2)'},
                    {'range': [40, 60], 'color': 'rgba(218, 165, 32, 0.2)'},
                    {'range': [60, 80], 'color': 'rgba(56, 139, 253, 0.2)'},
                    {'range': [80, 100], 'color': 'rgba(46, 160, 67, 0.2)'}
                ],
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            margin=dict(l=20, r=20, t=40, b=20),
            height=250
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_hs2:
        # Display Risk Level badge and brief summary
        risk_colors = {
            "Low Risk": "rgba(46, 160, 67, 0.25)",
            "Moderate Risk": "rgba(56, 139, 253, 0.25)",
            "High Risk": "rgba(218, 165, 32, 0.25)",
            "Critical Risk": "rgba(248, 81, 73, 0.25)"
        }
        badge_bg = risk_colors.get(risk_level, "rgba(255,255,255,0.1)")
        
        st.markdown(
            f"<div class='metric-card' style='margin-top: 15px; border-left: 5px solid {badge_bg.replace('0.25', '1.0')};'>"
            f"<h4>Assessed Risk Level</h4>"
            f"<span style='background-color: {badge_bg}; color: #ffffff; padding: 4px 10px; border-radius: 6px; font-weight: bold; font-size: 1.1rem;'>{risk_level}</span>"
            f"<p style='margin-top: 15px; font-size: 0.95rem; color: #c9d1d9;'>"
            f"Based on your Debt-to-Income (DTI), savings rate, expense coverage, and interest APR, "
            f"our deterministic algorithm rates your current credit default vulnerability as <b>{risk_level}</b>."
            f"</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # Explainable Factors Tabs
    tab1, tab2, tab3 = st.tabs(["🟢 Positive Factors", "🔴 Vulnerabilities", "💡 Improvement Areas"])
    with tab1:
        for factor in positive_factors:
            st.markdown(f"✅ {factor}")
    with tab2:
        for factor in negative_factors:
            st.markdown(f"⚠️ {factor}")
    with tab3:
        for area in improvement_areas:
            st.markdown(f"⚡ {area}")
            
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ RATIO ANALYTICS ------------------
    st.subheader("Key Ratio Performance")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        dti_val = metrics["dti_ratio"]
        dti_class = "success-card" if dti_val <= 20 else ("risk-card" if dti_val > 36 else "metric-card")
        st.markdown(
            f"<div class='{dti_class}'>"
            f"<h4>Debt-to-Income (DTI)</h4>"
            f"<h2>{dti_val:.1f}%</h2>"
            f"<p style='font-size:0.85rem; color:#8b949e; margin-bottom:0;'>Target: Under 36% (Industry Benchmark)</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_r2:
        exp_val = metrics["expense_to_income_ratio"]
        exp_class = "success-card" if exp_val <= 50 else ("risk-card" if exp_val > 75 else "metric-card")
        st.markdown(
            f"<div class='{exp_class}'>"
            f"<h4>Expense Ratio</h4>"
            f"<h2>{exp_val:.1f}%</h2>"
            f"<p style='font-size:0.85rem; color:#8b949e; margin-bottom:0;'>Essential + discretionary costs</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_r3:
        sav_val = metrics["savings_rate"]
        sav_class = "success-card" if sav_val >= 15 else ("risk-card" if sav_val <= 0 else "metric-card")
        st.markdown(
            f"<div class='{sav_class}'>"
            f"<h4>Savings Rate</h4>"
            f"<h2>{sav_val:.1f}%</h2>"
            f"<p style='font-size:0.85rem; color:#8b949e; margin-bottom:0;'>Target: Over 10% (Reserve buffer)</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ PLOTLY DATA CHARTS ------------------
    st.subheader("Asset & Liability Structure")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Cash flow bar chart (Income vs Expenses vs Debt Payments)
        flow_df = pd.DataFrame({
            "Category": ["Monthly Net Income", "Monthly Expenses", "Monthly Debt Payment"],
            "Amount": [metrics["total_income"], metrics["total_expenses"], metrics["total_monthly_debt_payment"]]
        })
        fig_flow = px.bar(
            flow_df,
            x="Category",
            y="Amount",
            color="Category",
            title="Monthly Cash Flow Allocation",
            color_discrete_map={
                "Monthly Net Income": "#2ea043",
                "Monthly Expenses": "#f78166",
                "Monthly Debt Payment": "#db6d28"
            }
        )
        fig_flow.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
        st.plotly_chart(fig_flow, use_container_width=True)
        
    with chart_col2:
        if active_debts:
            # Debt balances breakdown
            debts_df = pd.DataFrame({
                "Debt Account": [d.name for d in active_debts],
                "Outstanding Balance": [d.outstanding_balance for d in active_debts]
            })
            fig_debts = px.pie(
                debts_df,
                values="Outstanding Balance",
                names="Debt Account",
                title="Debt Balance Distribution",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_debts.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
            st.plotly_chart(fig_debts, use_container_width=True)
        else:
            st.info("Add active liabilities to view outstanding balance distributions.")
            
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ MACHINE LEARNING PREDICTOR SECTION ------------------
    st.subheader("🤖 Machine Learning Default Risk Assessment")
    st.write("Our predictive Random Forest classifier calculates default risk likelihood based on income, DTI, savings, and active debt APR.")
    
    # Import ML components
    from ml.feature_engineering import extract_features
    from ml.predictor import RiskPredictor
    
    try:
        # Extract features
        features = extract_features(metrics, debts)
        
        # Load model and predict (will auto-train if first run)
        predictor = RiskPredictor()
        prediction = predictor.predict_risk(features)
        
        pred_risk = prediction["risk_level"]
        probabilities = prediction["probabilities"]
        
        col_ml1, col_ml2 = st.columns([1, 2])
        
        with col_ml1:
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='metric-card' style='border-top: 4px solid #db6d28; text-align: center;'>"
                f"<h4>ML Risk Category</h4>"
                f"<h2 style='color: #db6d28; margin: 10px 0;'>{pred_risk}</h2>"
                f"<p style='color: #8b949e; font-size: 0.85rem;'>Calculated via Random Forest</p>"
                f"</div>",
                unsafe_allow_html=True
            )
            
        with col_ml2:
            # Create a horizontal bar chart of the class probabilities
            df_probs = pd.DataFrame({
                "Risk Category": list(probabilities.keys()),
                "Probability (%)": list(probabilities.values())
            })
            
            fig_probs = px.bar(
                df_probs,
                x="Probability (%)",
                y="Risk Category",
                orientation='h',
                title="Class Probability Distribution",
                color="Risk Category",
                color_discrete_map={
                    "Low Risk": "#2ea043",
                    "Moderate Risk": "#388bfd",
                    "High Risk": "#dba520",
                    "Critical Risk": "#f85149"
                }
            )
            fig_probs.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#e0e6ed",
                height=220,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_probs, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Could not execute ML risk assessment: {str(e)}")
        
    st.info(
        "⚠️ **Demonstration Model Notice:**\n"
        "This machine learning model is trained on a synthetic demonstration dataset (5,000 samples) "
        "and is intended for educational purposes. It is separate from the deterministic "
        "Financial Health Score shown at the top of the page."
    )

