from typing import Dict, Any, List
from database.models import Debt

def calculate_health_score(metrics: Dict[str, Any], debts: List[Debt]) -> Dict[str, Any]:
    """
    Computes a deterministic, explainable Financial Health Score from 0 to 100.
    Returns:
        - health_score (float)
        - risk_level (str)
        - positive_factors (list of str)
        - negative_factors (list of str)
        - improvement_areas (list of str)
    """
    score = 0.0
    positive_factors = []
    negative_factors = []
    improvement_areas = []
    
    total_income = metrics["total_income"]
    annual_income = total_income * 12
    dti = metrics["dti_ratio"]
    savings_rate = metrics["savings_rate"]
    expense_ratio = metrics["expense_to_income_ratio"]
    total_debt = metrics["total_debt"]
    disposable_income = metrics["disposable_income"]
    
    active_debts = [d for d in debts if d.status == "Active"]
    max_apr = max((d.interest_rate for d in active_debts), default=0.0)
    
    # If total income is 0, defaults to critical risk
    if total_income <= 0:
        return {
            "health_score": 0.0,
            "risk_level": "Critical Risk",
            "positive_factors": ["None"],
            "negative_factors": ["Total income is zero or negative.", "No active income streams declared."],
            "improvement_areas": ["Record your monthly income sources to calculate a health score."]
        }
        
    # --- 1. DTI Ratio Component (Max 25 pts) ---
    if dti <= 10.0:
        score += 25
        positive_factors.append("Excellent Debt-to-Income (DTI) ratio (under 10%).")
    elif dti <= 20.0:
        score += 20
        positive_factors.append("Healthy Debt-to-Income (DTI) ratio (under 20%).")
    elif dti <= 36.0:
        score += 15
        positive_factors.append("Manageable Debt-to-Income (DTI) ratio (between 20% and 36%).")
    elif dti <= 50.0:
        score += 8
        negative_factors.append("High Debt-to-Income (DTI) ratio (36% to 50%).")
        improvement_areas.append("Avoid taking on any new debts; focus on paying down current balances.")
    else:
        # DTI > 50%
        negative_factors.append("Critical Debt-to-Income (DTI) ratio (above 50%). More than half of your income is spent on debt repayments.")
        improvement_areas.append("Explore immediate debt relief, consolidation, or refinancing options to lower monthly DTI.")
        
    # --- 2. Savings Rate Component (Max 25 pts) ---
    if savings_rate >= 20.0:
        score += 25
        positive_factors.append("Superb monthly savings rate (above 20%).")
    elif savings_rate >= 10.0:
        score += 18
        positive_factors.append("Good monthly savings rate (between 10% and 20%).")
    elif savings_rate >= 5.0:
        score += 10
        positive_factors.append("Basic monthly savings rate (between 5% and 10%).")
    elif savings_rate > 0.0:
        score += 5
        negative_factors.append("Low monthly savings rate (under 5%). Your emergency buffer is growing very slowly.")
        improvement_areas.append("Try to find monthly expenses to trim in order to increase your savings rate to at least 10%.")
    else:
        # Savings rate <= 0%
        negative_factors.append("No savings. Your expenses and debt obligations exceed or exhaust your total income.")
        improvement_areas.append("Create a tight emergency budget. Cut discretionary costs to avoid sliding further into debt.")
        
    # --- 3. Expense-to-Income Component (Max 20 pts) ---
    if expense_ratio <= 40.0:
        score += 20
        positive_factors.append("Exceptional expense management (spending under 40% of income).")
    elif expense_ratio <= 60.0:
        score += 15
        positive_factors.append("Solid expense management (spending under 60% of income).")
    elif expense_ratio <= 80.0:
        score += 8
        negative_factors.append("Elevated monthly expenses (spending 60% to 80% of income).")
        improvement_areas.append("Perform an expense audit. Audit subscriptions and dining out to increase disposable cash.")
    else:
        # Expense ratio > 80%
        negative_factors.append("Critical monthly expenses (spending over 80% of income). Very little buffer remains.")
        improvement_areas.append("Urgent action: Drastically reduce non-essential categories (entertainment, shopping) immediately.")
        
    # --- 4. Debt Burden Component (Max 20 pts) ---
    debt_to_annual_ratio = (total_debt / annual_income) if annual_income > 0 else 0.0
    if total_debt == 0:
        score += 20
        positive_factors.append("Outstanding debt-free profile! You have zero outstanding liabilities.")
    elif debt_to_annual_ratio <= 0.1:
        score += 18
        positive_factors.append("Minimal overall debt load relative to your annual income.")
    elif debt_to_annual_ratio <= 0.3:
        score += 14
        positive_factors.append("Moderate overall debt load relative to your annual income.")
    elif debt_to_annual_ratio <= 0.5:
        score += 8
        negative_factors.append("Heavy overall debt load relative to your annual income.")
        improvement_areas.append("Adopt an aggressive debt payoff strategy (Avalanche/Snowball) to chip away at principal balances.")
    else:
        # > 0.5
        negative_factors.append("Critical overall debt load (debt is more than 50% of your annual income).")
        improvement_areas.append("Prioritize debt reduction above all secondary financial goals.")
        
    # --- 5. Interest Rate / APR Health Component (Max 10 pts) ---
    if not active_debts:
        score += 10
        positive_factors.append("No interest costs. You are not paying any APR penalties.")
    elif max_apr <= 10.0:
        score += 8
        positive_factors.append("Low average interest rates (all APRs are below 10%).")
    elif max_apr <= 18.0:
        score += 4
        negative_factors.append("Moderate interest rates. You have debts costing up to 18% APR.")
        improvement_areas.append("Refinance or transfer balances of moderate-APR accounts where possible.")
    else:
        # max_apr > 18%
        negative_factors.append("High interest rate penalty. You have active debts exceeding 18% APR (e.g. credit cards).")
        improvement_areas.append("Prioritize paying off high-interest credit cards first to stop interest compounding.")
        
    # Set Risk Level based on overall score
    if score >= 80.0:
        risk_level = "Low Risk"
    elif score >= 60.0:
        risk_level = "Moderate Risk"
    elif score >= 40.0:
        risk_level = "High Risk"
    else:
        risk_level = "Critical Risk"
        
    return {
        "health_score": round(score, 1),
        "risk_level": risk_level,
        "positive_factors": positive_factors if positive_factors else ["None"],
        "negative_factors": negative_factors if negative_factors else ["None"],
        "improvement_areas": improvement_areas if improvement_areas else ["Keep up the great financial habits!"]
    }
