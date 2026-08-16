import streamlit as st
import pandas as pd
import plotly.express as px
from database.repository import get_debts, get_incomes, get_expenses, get_profile
from financial.analyzer import calculate_financial_metrics
from financial.what_if_engine import run_what_if_analysis
from ai.gemini_service import GeminiService
from ai.prompt_engine import get_what_if_explanation_prompt
from ai.response_validator import validate_ai_response

def show_what_if(db, user):
    st.title("🔮 What-If Scenario Simulator")
    st.write("Simulate changes to your budget and monthly repayments. Python does the math; Gemini explains the impact.")
    
    # 1. Fetch active data
    profile = get_profile(db, user.id)
    incomes = get_incomes(db, user.id)
    expenses = get_expenses(db, user.id)
    debts = get_debts(db, user.id)
    
    active_debts = [d for d in debts if d.status == "Active" and d.outstanding_balance > 0]
    
    if not active_debts:
        st.warning("⚠️ No active debts. Please record your debts to run what-if simulations.")
        return
        
    metrics = calculate_financial_metrics(incomes, expenses, debts)
    disposable_cash = metrics["disposable_income"]
    
    # Strategy settings
    strategy = "Avalanche"
    if profile:
        strategy = profile.financial_goal if profile.financial_goal in ["Avalanche", "Snowball"] else "Avalanche"
        
    st.subheader("Simulate a Budget Adjustment")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        extra_monthly = st.slider(
            "Add Extra Monthly Cash ($ / ₹)",
            min_value=0.0,
            max_value=5000.0,
            value=max(0.0, disposable_cash),
            step=50.0,
            help="Additional cash you can allocate towards debt payoff on top of minimum payments."
        )
    with col_in2:
        expense_cut = st.slider(
            "Trim Discretionary Expenses ($ / ₹)",
            min_value=0.0,
            max_value=max(100.0, metrics["discretionary_expenses"]),
            value=0.0,
            step=25.0,
            help="Trimming this amount from discretionary wants directly increases your extra monthly payment pool."
        )
        
    # Calculate scenario payment
    base_extra = max(0.0, disposable_cash)
    scenario_extra = base_extra + extra_monthly + expense_cut
    
    # 2. Run Python calculations
    analysis = run_what_if_analysis(active_debts, strategy, base_extra, scenario_extra)
    
    base_info = analysis["base"]
    sc_info = analysis["scenario"]
    months_saved = analysis["months_saved"]
    interest_saved = analysis["interest_saved"]
    
    # Display comparison cards
    st.markdown("#### Simulation Outcomes")
    
    col_out1, col_out2, col_out3 = st.columns(3)
    with col_out1:
        st.markdown(
            f"<div class='metric-card' style='border-top: 4px solid #8b949e;'>"
            f"<h4>Base Payoff Duration</h4>"
            f"<h2>{base_info['total_months']} Months</h2>"
            f"<p style='color: #8b949e; margin-bottom: 0;'>Interest: {base_info['total_interest']:,.2f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_out2:
        st.markdown(
            f"<div class='success-card' style='border-top: 4px solid #2ea043;'>"
            f"<h4>Scenario Payoff Duration</h4>"
            f"<h2>{sc_info['total_months']} Months</h2>"
            f"<p style='color: #2ea043; font-weight: bold; margin-bottom: 0;'>Months Saved: {months_saved}</p>"
            f"<p style='color: #8b949e; margin-top:2px; margin-bottom: 0;'>Interest: {sc_info['total_interest']:,.2f}</p>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_out3:
        st.markdown(
            f"<div class='success-card' style='border-top: 4px solid #388bfd;'>"
            f"<h4>Projected Interest Saved</h4>"
            f"<h2>{interest_saved:,.2f}</h2>"
            f"<p style='color: #8b949e; margin-bottom: 0;'>Over repayment lifecycle</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        
    # Graphical visual
    chart_data = []
    for step in base_info["payoff_history"]:
        chart_data.append({
            "Month": step["Month"],
            "Outstanding Balance": step["Total Outstanding"],
            "Scenario": "Base Case"
        })
    for step in sc_info["payoff_history"]:
        chart_data.append({
            "Month": step["Month"],
            "Outstanding Balance": step["Total Outstanding"],
            "Scenario": "Modified Scenario"
        })
        
    df_chart = pd.DataFrame(chart_data)
    fig_comp = px.line(
        df_chart,
        x="Month",
        y="Outstanding Balance",
        color="Scenario",
        title="Repayment Timeline comparison",
        color_discrete_map={"Base Case": "#8b949e", "Modified Scenario": "#2ea043"}
    )
    fig_comp.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e0e6ed")
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # 3. Call Gemini for Natural Language Explanation
    st.markdown("<div class='subtle-divider'></div>", unsafe_allow_html=True)
    st.markdown("#### 💬 AI Financial Impact Summary")
    
    scenario_desc = (
        f"User increases their monthly extra payment by {extra_monthly:.2f} "
        f"and cuts discretionary expenses by {expense_cut:.2f}, increasing "
        f"their surplus debt repayment to {scenario_extra:.2f}."
    )
    
    # Button to request explanation (avates unnecessary API calls)
    explain_btn = st.button("💬 Explain Impact via Gemini")
    
    if explain_btn:
        with st.spinner("Consulting Gemini to synthesize explanations..."):
            try:
                ai_service = GeminiService()
                prompt = get_what_if_explanation_prompt(scenario_desc, base_info, sc_info)
                
                raw_exp = ai_service.generate_text(
                    prompt, 
                    system_instruction="You are a supportive financial coach explaining simulation outcomes.", 
                    temperature=0.2
                )
                
                # Validate response
                verified_numbers = {
                    "base_months": base_info["total_months"],
                    "base_interest": base_info["total_interest"],
                    "sc_months": sc_info["total_months"],
                    "sc_interest": sc_info["total_interest"],
                    "months_saved": months_saved,
                    "interest_saved": interest_saved
                }
                validation = validate_ai_response(raw_exp, verified_numbers)
                sanitized_exp = validation["sanitized_text"]
                
                st.markdown(
                    f"<div class='metric-card' style='padding: 20px;'>\n"
                    f"{sanitized_exp}\n"
                    f"</div>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"❌ Could not retrieve AI explanation: {str(e)}")
