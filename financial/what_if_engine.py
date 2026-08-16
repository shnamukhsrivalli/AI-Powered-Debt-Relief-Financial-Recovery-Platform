from typing import List, Dict, Any
from database.models import Debt
from financial.payoff_calculator import simulate_payoff

def run_what_if_analysis(
    debts: List[Debt], 
    strategy: str,
    base_extra_payment: float,
    scenario_extra_payment: float
) -> Dict[str, Any]:
    """
    Executes a side-by-side comparison of two repayment scenarios using Python calculations.
    """
    # 1. Simulate base scenario
    base_res = simulate_payoff(debts, strategy, base_extra_payment)
    
    # 2. Simulate scenario scenario
    scenario_res = simulate_payoff(debts, strategy, scenario_extra_payment)
    
    # 3. Calculate improvements
    months_saved = max(0, base_res["total_months"] - scenario_res["total_months"])
    interest_saved = max(0.0, base_res["total_interest"] - scenario_res["total_interest"])
    
    return {
        "base": {
            "total_months": base_res["total_months"],
            "total_interest": base_res["total_interest"],
            "payoff_history": base_res["payoff_history"],
            "safety_triggered": base_res["safety_triggered"]
        },
        "scenario": {
            "total_months": scenario_res["total_months"],
            "total_interest": scenario_res["total_interest"],
            "payoff_history": scenario_res["payoff_history"],
            "safety_triggered": scenario_res["safety_triggered"]
        },
        "months_saved": months_saved,
        "interest_saved": round(interest_saved, 2)
    }
