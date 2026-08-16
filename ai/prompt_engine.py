from typing import Dict, Any

# Standard disclaimer to inject or remind the user
AI_SAFETY_RULES = """
CRITICAL GUIDELINES FOR YOUR BEHAVIOR:
1. Do not invent missing user information.
2. Use ONLY verified financial context provided in the prompts.
3. Do NOT fabricate numerical values. Any numerical value you write MUST be directly taken from the provided context. If you need to write an estimate, clearly label it as an "Estimate".
4. Do NOT guarantee debt elimination, interest savings, or credit score improvement.
5. Do NOT claim to be a licensed financial adviser. Always maintain that you are providing educational information and guidance.
6. Recommend professional help (like non-profit credit counseling, bankruptcy lawyers) if the user's situation is critical (e.g., disposable income is heavily negative, DTI > 50%).
7. Be supportive, objective, and non-judgmental.
"""

def get_system_instruction() -> str:
    """Returns the core system prompt setting identity and safety guidelines for the chatbot."""
    return f"""
You are the AI Financial Recovery Assistant, an intelligent support tool built into the AI Powered Debt Relief Platform.
Your goal is to explain financial concepts, guide users on budget optimizations, and offer educational answers.
{AI_SAFETY_RULES}
"""

def get_recovery_plan_prompt(profile: Dict[str, Any], metrics: Dict[str, Any], debts_list: list, strategy: str, payoff_summary: Dict[str, Any]) -> str:
    """Formats a highly detailed, structured prompt for generating a recovery plan."""
    
    # Formulate a text ledger of debts
    debts_text = ""
    for d in debts_list:
        debts_text += f"- {d['name']} ({d['type']}): Balance {d['balance']:.2f}, APR {d['apr']}%, Minimum Payment {d['min_pay']:.2f}, EMI {d['emi']:.2f}, Remaining Tenure {d['tenure']} months\n"
        
    prompt = f"""
You are tasked with generating a structured Personal Financial Recovery Plan.
Below is the user's verified financial profile, cash flow metrics, outstanding debts, and calculated payoff projections.

### USER PROFILE
- Name: {profile.get('name', 'User')}
- Employment Status: {profile.get('employment_status', 'Not Provided')}
- Financial Goal: {profile.get('financial_goal', 'Debt Payoff')}
- Planning Horizon: {profile.get('planning_period', 12)} Months

### VERIFIED CASH FLOW METRICS
- Total Monthly Net Income: {metrics['total_income']:.2f}
- Monthly Expenses (Essential): {metrics['essential_expenses']:.2f}
- Monthly Expenses (Discretionary): {metrics['discretionary_expenses']:.2f}
- Monthly Debt Obligations (Minimum Payments): {metrics['total_monthly_debt_payment']:.2f}
- Disposable Surplus Cash: {metrics['disposable_income']:.2f}
- Expense-to-Income Ratio: {metrics['expense_to_income_ratio']:.1f}%
- Debt-to-Income (DTI) Ratio: {metrics['dti_ratio']:.1f}%
- Savings Rate: {metrics['savings_rate']:.1f}%

### ACTIVE DEBT LEDGER
{debts_text if debts_text else "- No active debts."}

### CALCULATED PAYOFF PROJECTIONS (Strategy: {strategy})
- Payoff Duration: {payoff_summary['total_months']} Months
- Total Interest to be Paid: {payoff_summary['total_interest']:.2f}
- Safety Status: {"Negative Amortization Detected (current payments cannot cover interest!)" if payoff_summary['safety_triggered'] else "Stable Payoff Timeline"}

Please compile a comprehensive, highly personalized **Financial Recovery Plan** matching this data. You MUST structure your plan with these exact headings:

#### 1. Financial Summary
Provide a supportive, clear overview of the user's situation based on the numbers. Highlight DTI and Cash Flow health.

#### 2. Key Challenges
Identify the 2-3 biggest obstacles in their current numbers (e.g. high-interest card, high discretionary spending, zero savings rate).

#### 3. Debt Priority Order
Explain how they should prioritize their payments according to the {strategy} strategy. Explicitly call out which account to pay first and why.

#### 4. Budget Recommendations
Offer concrete suggestions on reducing discretionary spending (Dining, Entertainment) to increase their monthly extra payment surplus.

#### 5. Monthly Recovery Plan
Outline a monthly action checklist they can follow (e.g. Pay Min on Accounts B, C; Apply Surplus to Account A).

#### 6. Savings Target & Emergency Fund Goal
Calculate or suggest a realistic emergency fund milestone (e.g. 3-6 months of essential expenses) and how to start building it.

#### 7. Recovery Milestones
Provide a timeline of achievements based on the calculated payoff months (e.g. closing first account by month X, debt-free by month Y).

#### 8. Next Action Step
A single, simple, actionable step they can take today to get started.

REMEMBER: Do not invent or change any numerical values. All calculations must correspond to the verified values provided above. Be supportive, professional, and add the standard educational disclaimer.
"""
    return prompt

def get_what_if_explanation_prompt(scenario_desc: str, base_payoff: Dict[str, Any], scenario_payoff: Dict[str, Any]) -> str:
    """Formats a prompt to explain the difference between a base scenario and a what-if scenario."""
    return f"""
You are the AI Financial Recovery Assistant. Explain the results of a What-If scenario simulation to a user.

### SCENARIO SIMULATED
{scenario_desc}

### CALCULATED COMPARISON
**Base Case (Standard Repayment):**
- Payoff Timeline: {base_payoff['total_months']} Months
- Total Interest Paid: {base_payoff['total_interest']:.2f}
- Safety Status: {"Negative Amortization Detected" if base_payoff['safety_triggered'] else "Stable"}

**Scenario Case (Modified Repayment):**
- Payoff Timeline: {scenario_payoff['total_months']} Months
- Total Interest Paid: {scenario_payoff['total_interest']:.2f}
- Safety Status: {"Negative Amortization Detected" if scenario_payoff['safety_triggered'] else "Stable"}

Please provide a natural language explanation of the results:
1. Explain how much time they save (months shaved off).
2. Explain how much interest expense they save.
3. Offer an encouraging, educational takeaway about the power of extra payments or expense reduction.
4. Keep the explanation brief, friendly, and 100% accurate to the numbers. Do not invent interest savings or months.
"""
