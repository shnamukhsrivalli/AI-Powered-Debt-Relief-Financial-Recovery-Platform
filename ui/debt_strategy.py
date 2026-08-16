import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.repository import get_debts, get_incomes, get_expenses
from financial.analyzer import calculate_financial_metrics
from financial.debt_engine import get_avalanche_priority, get_snowball_priority
from financial.payoff_calculator import simulate_payoff

def show_debt_strategy(db, user):
    st.title("🎯 Debt Repayment Strategies")
    st.write("Compare the mathematical projection of the **Debt Avalanche** vs. **Debt Snowball** methods.")
    
    # 1. Fetch active debts
    debts = get_debts(db, user.id)
    active_debts = [d for d in debts if d.status == "Active" and d.outstanding_balance > 0]
    
    if not active_debts:
        st.warning("⚠️ No active liabilities detected. Please add your debts first.")
        st.info("Navigate to the **💳 Debt Management** tab in the sidebar to record your debts.")
        return
        
    # Fetch incomes & expenses to calculate disposable income surplus
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    metrics = calculate_financial_metrics(incomes, expenses, debts)
    disposable_cash = metrics["disposable_income"]
    
    # ------------------ SIDE-BY-SIDE PRIORITIZATION ORDER ------------------
    st.subheader("Priority Payoff Order comparison")
    
    col_str1, col_str2 = st.columns(2)
    
    with col_str1:
        st.markdown(
            "<div style='border: 1px solid #388bfd; border-radius: 8px; padding: 15px; background: rgba(56, 139, 253, 0.05);'>"
            "<h4>🏔️ Debt Avalanche (Highest Interest First)</h4>"
            "<p style='font-size: 0.85rem; color: #8b949e;'>"
            "Directs extra funds to the liability carrying the highest APR. This is mathematically optimal "
            "as it minimizes total interest compounding."
            "</p>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        avalanche_list = get_avalanche_priority(active_debts)
        av_rows = []
        for idx, d in enumerate(avalanche_list, 1):
            av_rows.append({
                "Rank": f"#{idx}",
                "Debt Account": d.name,
                "APR": f"{d.interest_rate}%",
                "Balance": f"{d.outstanding_balance:,.2f}",
                "Strategy Focus": "Targeting high APR" if idx == 1 else "Queued"
            })
        st.table(pd.DataFrame(av_rows))
        
    with col_str2:
        st.markdown(
            "<div style='border: 1px solid #f78166; border-radius: 8px; padding: 15px; background: rgba(247, 129, 102, 0.05);'>"
            "<h4>❄️ Debt Snowball (Smallest Balance First)</h4>"
            "<p style='font-size: 0.85rem; color: #8b949e;'>"
            "Focuses extra cash on the account with the smallest outstanding balance first. "
            "Designed to build momentum and quick psychological wins as accounts close."
            "</p>"
            "</div>",
            unsafe_allow_html=True
        )
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        snowball_list = get_snowball_priority(active_debts)
        sb_rows = []
        for idx, d in enumerate(snowball_list, 1):
            sb_rows.append({
                "Rank": f"#{idx}",
                "Debt Account": d.name,
                "APR": f"{d.interest_rate}%",
                "Balance": f"{d.outstanding_balance:,.2f}",
                "Strategy Focus": "Targeting small balance" if idx == 1 else "Queued"
            })
        st.table(pd.DataFrame(sb_rows))
        
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ INTERACTIVE PAYOFF CALCULATOR ------------------
    st.subheader("Interactive Payoff Amortization Simulator")
    st.write("Determine how adding surplus payments shortens your payoff timeline.")
    
    # Recommend extra payment based on disposable cash
    default_extra = max(0.0, disposable_cash)
    
    col_ctl1, col_ctl2 = st.columns([2, 1])
    with col_ctl1:
        extra_payment = st.slider(
            "Select Monthly Extra Payment ($ / ₹)", 
            min_value=0.0, 
            max_value=max(5000.0, default_extra * 2), 
            value=default_extra, 
            step=50.0,
            help="Additional money added on top of your minimum required debt payments each month."
        )
    with col_ctl2:
        st.metric("Estimated Disposable Income Surplus", f"{disposable_cash:,.2f}")
        
    # Run Simulations
    res_min = simulate_payoff(active_debts, "avalanche", 0.0) # Base projection (min only)
    res_av = simulate_payoff(active_debts, "avalanche", extra_payment)
    res_sb = simulate_payoff(active_debts, "snowball", extra_payment)
    
    # ------------------ COMPARATIVE METRICS Display ------------------
    st.markdown("#### Payoff Summary Comparison")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    
    with m_col1:
        min_months = res_min["total_months"]
        min_interest = res_min["total_interest"]
        st.markdown(
            f"<div class='metric-card' style='border-top: 4px solid #8b949e;'>"
            f"<h4>Minimum Payments Only</h4>"
            f"<h2 style='margin: 5px 0;'>{min_months} Months</h2>"
            f"<p style='color: #8b949e; margin-bottom: 0;'>Total Interest: {min_interest:,.2f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        if res_min["safety_triggered"]:
            st.warning("⚠️ Warning: Balances are growing under minimum payments (Negative Amortization)!")
            
    with m_col2:
        av_months = res_av["total_months"]
        av_interest = res_av["total_interest"]
        interest_saved_av = max(0.0, min_interest - av_interest)
        st.markdown(
            f"<div class='success-card' style='border-top: 4px solid #388bfd;'>"
            f"<h4>Avalanche with Extra</h4>"
            f"<h2 style='margin: 5px 0;'>{av_months} Months</h2>"
            f"<p style='color: #388bfd; font-weight: bold; margin-bottom: 0;'>Interest Saved: {interest_saved_av:,.2f}</p>"
            f"<p style='color: #8b949e; margin-top: 2px; margin-bottom: 0;'>Total Interest: {av_interest:,.2f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        if res_av["safety_triggered"]:
            st.error("🚨 Extra payment is still insufficient to prevent debt expansion.")
            
    with m_col3:
        sb_months = res_sb["total_months"]
        sb_interest = res_sb["total_interest"]
        interest_saved_sb = max(0.0, min_interest - sb_interest)
        st.markdown(
            f"<div class='success-card' style='border-top: 4px solid #f78166;'>"
            f"<h4>Snowball with Extra</h4>"
            f"<h2 style='margin: 5px 0;'>{sb_months} Months</h2>"
            f"<p style='color: #f78166; font-weight: bold; margin-bottom: 0;'>Interest Saved: {interest_saved_sb:,.2f}</p>"
            f"<p style='color: #8b949e; margin-top: 2px; margin-bottom: 0;'>Total Interest: {sb_interest:,.2f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        if res_sb["safety_triggered"]:
            st.error("🚨 Extra payment is still insufficient to prevent debt expansion.")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # ------------------ TIMELINE CHART ------------------
    st.markdown("#### Balance Elimination Over Time")
    
    # Build dataframe for line charts
    chart_data = []
    
    # Extract historical points
    # Min payment timeline
    for step in res_min["payoff_history"]:
        chart_data.append({
            "Month": step["Month"],
            "Outstanding Balance": step["Total Outstanding"],
            "Strategy": "Minimum Payments Only"
        })
    # Avalanche timeline
    for step in res_av["payoff_history"]:
        chart_data.append({
            "Month": step["Month"],
            "Outstanding Balance": step["Total Outstanding"],
            "Strategy": "Debt Avalanche (Extra)"
        })
    # Snowball timeline
    for step in res_sb["payoff_history"]:
        chart_data.append({
            "Month": step["Month"],
            "Outstanding Balance": step["Total Outstanding"],
            "Strategy": "Debt Snowball (Extra)"
        })
        
    df_chart = pd.DataFrame(chart_data)
    
    fig_timeline = px.line(
        df_chart,
        x="Month",
        y="Outstanding Balance",
        color="Strategy",
        title="Amortization Balance Comparison",
        color_discrete_map={
            "Minimum Payments Only": "#8b949e",
            "Debt Avalanche (Extra)": "#388bfd",
            "Debt Snowball (Extra)": "#f78166"
        }
    )
    fig_timeline.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
    st.plotly_chart(fig_timeline, use_container_width=True)
