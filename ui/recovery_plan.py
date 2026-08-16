import streamlit as st
from database.repository import get_profile, get_incomes, get_expenses, get_debts, get_latest_recovery_plan
from ai.recovery_generator import RecoveryPlanGenerator
from financial.analyzer import calculate_financial_metrics

def show_recovery_plan(db, user):
    st.title("🤖 AI Recovery Plan Generator")
    st.write("Generate a personalized, supportive debt recovery strategy grounded in your numbers using Google Gemini.")
    
    # 1. Fetch user data
    profile = get_profile(db, user.id)
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    debts = get_debts(db, user.id)
    
    # Data check
    active_debts = [d for d in debts if d.status == "Active" and d.outstanding_balance > 0]
    
    if not profile:
        st.warning("⚠️ Profile missing. Please configure your financial profile first.")
        st.info("Navigate to the **👤 Financial Profile** tab in the sidebar.")
        return
    if not incomes and not expenses:
        st.warning("⚠️ Cash flow data missing. Please add your Income & Expenses first.")
        return
    if not active_debts:
        st.success("🎉 You have no active debts! An AI Recovery Plan is not required. Keep saving!")
        return
        
    # Analyze disposable surplus
    metrics = calculate_financial_metrics(incomes, expenses, debts)
    disposable_cash = metrics["disposable_income"]
    
    # 2. Input options for plan generation
    st.subheader("Plan Generation Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        strategy = st.selectbox(
            "Select Repayment Strategy",
            options=["Avalanche", "Snowball"],
            help="Choose 'Avalanche' to save the most interest, or 'Snowball' for quick account-payoff wins."
        )
    with col2:
        extra_payment = st.number_input(
            "Monthly Extra Payment ($ / ₹)",
            min_value=0.0,
            value=max(0.0, disposable_cash),
            step=100.0,
            help="Additional funds added to your repayments. Defaults to your calculated disposable cash flow surplus."
        )
        
    generate_btn = st.button("🚀 Generate AI Recovery Plan")
    
    # 3. Check database for existing plan
    latest_plan = get_latest_recovery_plan(db, user.id)
    
    if generate_btn:
        with st.spinner("Analyzing cash flow metrics and generating your plan via Google Gemini..."):
            try:
                plan_generator = RecoveryPlanGenerator(db)
                plan_text = plan_generator.generate_plan(
                    user_id=user.id,
                    profile_obj=profile,
                    incomes=incomes,
                    expenses=expenses,
                    debts=active_debts,
                    strategy=strategy,
                    extra_payment=extra_payment
                )
                st.success("🎉 New recovery plan generated successfully!")
                latest_plan = get_latest_recovery_plan(db, user.id)  # Refresh plan
            except Exception as e:
                st.error(f"❌ Failed to generate recovery plan: {str(e)}")
                
    # 4. Render Plan
    if latest_plan:
        st.markdown("---")
        st.markdown(f"### Latest Personal Recovery Plan (Strategy: {latest_plan.strategy_type})")
        st.caption(f"Generated on {latest_plan.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        st.markdown(
            f"<div class='metric-card' style='padding: 25px;'>\n"
            f"{latest_plan.plan_content}\n"
            f"</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("No recovery plan has been generated yet. Adjust the settings above and click 'Generate AI Recovery Plan' to begin.")
