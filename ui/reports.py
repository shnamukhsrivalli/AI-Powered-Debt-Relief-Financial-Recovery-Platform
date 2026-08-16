import streamlit as st
import pandas as pd
from database.repository import (
    get_profile, get_incomes, get_expenses, get_debts,
    get_latest_analysis, get_latest_recovery_plan, get_progress_logs
)
from financial.analyzer import calculate_financial_metrics
from financial.payoff_calculator import simulate_payoff
from config.constants import DISCLAIMER_TEXT

def compile_report_text(db, user) -> str:
    """Compiles all database and calculation metrics into a unified plain-text report."""
    profile = get_profile(db, user.id)
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    debts = get_debts(db, user.id)
    analysis = get_latest_analysis(db, user.id)
    latest_plan = get_latest_recovery_plan(db, user.id)
    progress = get_progress_logs(db, user.id)
    
    active_debts = [d for d in debts if d.status == "Active"]
    metrics = calculate_financial_metrics(incomes, expenses, debts)
    
    report = []
    report.append("==========================================================================")
    report.append("            PERSONAL FINANCIAL RECOVERY & DEBT RELIEF REPORT")
    report.append("==========================================================================\n")
    
    # 1. Profile Section
    report.append("--- 1. USER PROFILE ---")
    if profile:
        report.append(f"Name: {profile.name}")
        report.append(f"Age Range: {profile.age_range}")
        report.append(f"Employment Status: {profile.employment_status}")
        report.append(f"Primary Goal: {profile.financial_goal}")
        report.append(f"Planning Horizon: {profile.planning_period} Months")
    else:
        report.append("No profile configured.")
    report.append("")
    
    # 2. Income & Expenses
    report.append("--- 2. CASH FLOW SUMMARY ---")
    report.append(f"Total Monthly Income: {metrics['total_income']:,.2f}")
    report.append(f"Estimated Annual Income: {metrics['total_income'] * 12:,.2f}")
    report.append(f"Monthly Expenses (Essential): {metrics['essential_expenses']:,.2f}")
    report.append(f"Monthly Expenses (Discretionary): {metrics['discretionary_expenses']:,.2f}")
    report.append(f"Total Expenses: {metrics['total_expenses']:,.2f}")
    report.append(f"Expense-to-Income Ratio: {metrics['expense_to_income_ratio']:.1f}%")
    report.append(f"Disposable Cash Flow (before debt): {metrics['total_income'] - metrics['total_expenses']:,.2f}")
    report.append("")
    
    # 3. Debt ledger
    report.append("--- 3. DEBT LEDGER ---")
    if not active_debts:
        report.append("No active debts.")
    else:
        for d in active_debts:
            report.append(
                f"- {d.name} ({d.debt_type}): Balance: {d.outstanding_balance:,.2f}, "
                f"APR: {d.interest_rate}%, Minimum: {d.minimum_payment:,.2f}, EMI: {d.emi:,.2f}"
            )
        report.append(f"Total Outstanding Debt: {metrics['total_debt']:,.2f}")
        report.append(f"Monthly Debt Payment (Minimums): {metrics['total_monthly_debt_payment']:,.2f}")
        report.append(f"Debt-to-Income (DTI) Ratio: {metrics['dti_ratio']:.1f}%")
        report.append(f"Net Disposable Income: {metrics['disposable_income']:,.2f}")
    report.append("")
    
    # 4. Scores & ML
    report.append("--- 4. SCORES & RISK ASSESSMENT ---")
    if analysis:
        report.append(f"Financial Health Score: {analysis.health_score} / 100")
        report.append(f"Risk Assessment Level: {analysis.risk_level}")
    else:
        report.append("No scores calculated yet.")
    report.append("")
    
    # 5. Payoff Simulations
    report.append("--- 5. REPAYMENT METHOD Projections ---")
    if active_debts:
        # Run default simulation (disposable cash surplus)
        surplus = max(0.0, metrics["disposable_income"])
        res_av = simulate_payoff(active_debts, "avalanche", surplus)
        res_sb = simulate_payoff(active_debts, "snowball", surplus)
        
        report.append(f"Avalanche Strategy Payoff Time: {res_av['total_months']} Months (Interest: {res_av['total_interest']:,.2f})")
        report.append(f"Snowball Strategy Payoff Time: {res_sb['total_months']} Months (Interest: {res_sb['total_interest']:,.2f})")
    else:
        report.append("No active debts to project.")
    report.append("")
    
    # 6. AI Plan
    report.append("--- 6. AI RECOVERY PLAN RECOMMENDATIONS ---")
    if latest_plan:
        report.append(f"Chosen Strategy: {latest_plan.strategy_type}")
        report.append(latest_plan.plan_content)
    else:
        report.append("No AI Recovery Plan generated yet.")
    report.append("")
    
    # 7. Progress Logs
    report.append("--- 7. HISTORICAL PROGRESS LOGS ---")
    if not progress:
        report.append("No historical monthly logs recorded.")
    else:
        for p in progress:
            report.append(
                f"- Month {p.month_year}: Principal Paid: {p.debt_paid:,.2f}, "
                f"Remaining Debt: {p.remaining_debt:,.2f}, Savings Added: {p.savings_added:,.2f}"
            )
    report.append("")
    
    # 8. Disclaimer
    report.append("==========================================================================")
    report.append("                      IMPORTANT SAFETY DISCLAIMER")
    report.append("==========================================================================")
    report.append(DISCLAIMER_TEXT)
    report.append("==========================================================================")
    
    return "\n".join(report)

def show_reports(db, user):
    st.title("📄 Financial Recovery Report")
    st.write("Compile all details, scores, projections, and progress metrics into a single exportable statement.")
    
    profile = get_profile(db, user.id)
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    
    if not profile and not incomes:
        st.warning("⚠️ No data available to compile a report. Please configure your profile, income, and expenses first.")
        return
        
    with st.spinner("Compiling database records and formatting statement..."):
        report_text = compile_report_text(db, user)
        
    st.subheader("Statement Preview")
    st.text_area("Recovery Statement File Preview", value=report_text, height=450)
    
    # File download
    file_name = f"financial_recovery_report_{user.username}.txt"
    st.download_button(
        label="💾 Download Statement as Plain Text",
        data=report_text,
        file_name=file_name,
        mime="text/plain"
    )
