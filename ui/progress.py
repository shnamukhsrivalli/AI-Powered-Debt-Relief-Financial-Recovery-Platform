import streamlit as st
import pandas as pd
import plotly.express as px
from database.repository import get_debts, get_progress_logs, add_progress_log

def show_progress(db, user):
    st.title("📈 Progress Tracking")
    st.write("Log your monthly payoff amounts and watch your liabilities shrink and savings grow over time.")
    
    # 1. Fetch active debts and progress logs
    debts = get_debts(db, user.id)
    active_debts = [d for d in debts if d.status == "Active"]
    logs = get_progress_logs(db, user.id)
    
    # Check if debts exist
    if not active_debts and not logs:
        st.warning("⚠️ Please configure your debts in **💳 Debt Management** first to initialize progress tracking.")
        return
        
    # Calculate initial stats
    starting_debt = sum(d.original_principal for d in active_debts)
    current_debt = sum(d.outstanding_balance for d in active_debts)
    total_paid_from_db = starting_debt - current_debt
    
    # Override/refine stats if logs exist
    if logs:
        latest_log = logs[-1]
        current_debt = latest_log.remaining_debt
        
    completion_percentage = (total_paid_from_db / starting_debt * 100) if starting_debt > 0 else 0.0
    completion_percentage = min(100.0, max(0.0, completion_percentage))
    
    # ------------------ TOP SUMMARY PROGRESS METRICS ------------------
    st.subheader("Debt Elimination Lifecycle")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown(
            f"<div class='metric-card'>"
            f"<h4>Starting Debt Load</h4>"
            f"<h2>{starting_debt:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom: 0;'>Total original borrowings</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_p2:
        st.markdown(
            f"<div class='risk-card'>"
            f"<h4>Current Outstanding Debt</h4>"
            f"<h2>{current_debt:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom: 0;'>Payoff Completion: {completion_percentage:.1f}%</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_p3:
        st.markdown(
            f"<div class='success-card'>"
            f"<h4>Debt Paid Off</h4>"
            f"<h2>{total_paid_from_db:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom: 0;'>Reduced via principal payments</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # Streamlit progress bar
    st.progress(completion_percentage / 100.0)
    
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    
    # ------------------ MONTHLY PROGRESS LOGGING FORM ------------------
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.markdown("#### Log Monthly Status")
        with st.form("progress_log_form", clear_on_submit=True):
            month_year = st.text_input("Month/Year", placeholder="e.g. 2026-08")
            debt_paid = st.number_input("Principal Paid This Month ($ / ₹)", min_value=0.0, step=100.0)
            remaining_debt = st.number_input("Remaining Total Debt Balance ($ / ₹)", min_value=0.0, value=current_debt, step=500.0)
            savings_added = st.number_input("Amount Added to Savings ($ / ₹)", min_value=0.0, step=100.0)
            milestones = st.text_input("Milestone Achieved (Optional)", placeholder="e.g. Paid off Visa Card!")
            
            submit_log = st.form_submit_button("Log Progress")
            if submit_log:
                if not month_year.strip():
                    st.error("Month/Year is required (e.g. YYYY-MM).")
                else:
                    try:
                        add_progress_log(
                            db,
                            user_id=user.id,
                            month_year=month_year.strip(),
                            debt_paid=debt_paid,
                            remaining_debt=remaining_debt,
                            savings_added=savings_added,
                            milestones_achieved=milestones.strip() if milestones.strip() else None
                        )
                        st.success(f"Log for {month_year} saved successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to save progress log: {str(e)}")
                        
    with col_f2:
        st.markdown("#### Historical Progress Log")
        if not logs:
            st.info("No progress log history logged yet. Log your first month using the form.")
        else:
            log_rows = []
            for l in logs:
                log_rows.append({
                    "Month": l.month_year,
                    "Paid": l.debt_paid,
                    "Remaining Balance": l.remaining_debt,
                    "Savings Added": l.savings_added,
                    "Milestones": l.milestones_achieved if l.milestones_achieved else "None"
                })
            df_logs = pd.DataFrame(log_rows)
            st.dataframe(df_logs[["Month", "Paid", "Remaining Balance", "Savings Added", "Milestones"]], use_container_width=True)
            
            # Progress over time Plotly charts
            fig_hist = px.line(
                df_logs,
                x="Month",
                y="Remaining Balance",
                title="Debt Reduction Timeline",
                markers=True
            )
            fig_hist.update_traces(line_color="#f85149", marker=dict(size=8))
            fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
            st.plotly_chart(fig_hist, use_container_width=True)
            
    # Milestones list
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    st.subheader("🏆 Completed Milestones Timeline")
    
    has_milestones = False
    if logs:
        for l in logs:
            if l.milestones_achieved:
                has_milestones = True
                st.markdown(
                    f"<div style='border-left: 3px solid #2ea043; padding-left: 15px; margin-bottom: 12px;'>"
                    f"📅 <b>{l.month_year}</b>: {l.milestones_achieved}"
                    f"</div>",
                    unsafe_allow_html=True
                )
                
    if not has_milestones:
        st.info("No milestones achieved yet. Log your monthly progress details to build your timeline achievements.")
