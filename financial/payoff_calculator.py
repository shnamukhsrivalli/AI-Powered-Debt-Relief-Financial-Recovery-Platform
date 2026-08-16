from typing import List, Dict, Any, Tuple
from database.models import Debt
from financial.debt_engine import get_avalanche_priority, get_snowball_priority
import copy

def simulate_payoff(
    debts: List[Debt], 
    strategy: str, 
    extra_payment: float = 0.0
) -> Dict[str, Any]:
    """
    Simulates a month-by-month repayment projection.
    
    Args:
        debts: List of active Debt objects.
        strategy: "Avalanche" or "Snowball".
        extra_payment: Additional payment added each month.
        
    Returns:
        - total_months (int): Months until all debts are paid off.
        - total_interest (float): Sum of all interest paid.
        - payoff_history (list of dicts): Amortization table.
        - safety_triggered (bool): True if payments are too low to cover interest.
    """
    active_debts = [d for d in debts if d.status == "Active" and d.outstanding_balance > 0]
    
    if not active_debts:
        return {
            "total_months": 0,
            "total_interest": 0.0,
            "payoff_history": [],
            "safety_triggered": False
        }
        
    # Order debts by priority strategy
    if strategy.lower() == "avalanche":
        priority_debts = get_avalanche_priority(active_debts)
    else:
        priority_debts = get_snowball_priority(active_debts)
        
    # Work on a deep copy of the debts to avoid mutating database state
    sim_debts = []
    for d in priority_debts:
        sim_debts.append({
            "id": d.id,
            "name": d.name,
            "balance": d.outstanding_balance,
            "apr": d.interest_rate,
            "min_pay": d.minimum_payment,
            "interest_paid": 0.0
        })
        
    payoff_history = []
    total_interest_accumulated = 0.0
    month = 0
    max_months_safety = 360  # 30 years cap
    safety_triggered = False
    
    # Store initial state (Month 0)
    initial_balances = {d["name"]: d["balance"] for d in sim_debts}
    initial_balances["Total Outstanding"] = sum(d["balance"] for d in sim_debts)
    initial_balances["Month"] = 0
    initial_balances["Interest Paid This Month"] = 0.0
    payoff_history.append(initial_balances)
    
    while any(d["balance"] > 0 for d in sim_debts):
        month += 1
        month_interest_paid = 0.0
        
        # 1. Accrue interest for this month
        for d in sim_debts:
            if d["balance"] > 0:
                monthly_apr = (d["apr"] / 12.0) / 100.0
                interest_accrued = d["balance"] * monthly_apr
                d["balance"] += interest_accrued
                d["interest_paid"] += interest_accrued
                month_interest_paid += interest_accrued
                total_interest_accumulated += interest_accrued
                
        # 2. Check for negative amortization safety
        # If total outstanding balance grows compared to the starting balance of the month,
        # or if we exceed the safety ceiling, trigger safety
        current_total_balance = sum(d["balance"] for d in sim_debts)
        previous_total_balance = payoff_history[-1]["Total Outstanding"]
        
        # If balance grew and the user is not making progress
        if month > 1 and current_total_balance >= previous_total_balance:
            # Check if this growth is persistent (i.e. even with extra payments, interest exceeds total payments)
            total_min_due = sum(d["min_pay"] for d in sim_debts if d["balance"] > 0)
            if total_min_due + extra_payment <= month_interest_paid:
                safety_triggered = True
                break
                
        if month > max_months_safety:
            safety_triggered = True
            break
            
        # 3. Apply payments
        surplus_rollover = extra_payment
        
        # First pass: Apply minimum payments to each active debt
        for d in sim_debts:
            if d["balance"] > 0:
                payment = min(d["min_pay"], d["balance"])
                d["balance"] -= payment
                
                # If we paid more than the balance (i.e. min payment was larger than final balance),
                # roll over the remaining minimum payment amount to the surplus pool
                if payment < d["min_pay"]:
                    surplus_rollover += (d["min_pay"] - payment)
            else:
                # Debt was already paid off in a previous month, so its minimum payment is now rolled over
                surplus_rollover += d["min_pay"]
                
        # Second pass: Apply surplus rollover to the highest-priority active debt
        for d in sim_debts:
            if d["balance"] > 0:
                if surplus_rollover > 0:
                    payment = min(surplus_rollover, d["balance"])
                    d["balance"] -= payment
                    surplus_rollover -= payment
                else:
                    break  # No more surplus to distribute
                    
        # 4. Record month state
        month_balances = {d["name"]: round(d["balance"], 2) for d in sim_debts}
        month_balances["Total Outstanding"] = round(sum(d["balance"] for d in sim_debts), 2)
        month_balances["Month"] = month
        month_balances["Interest Paid This Month"] = round(month_interest_paid, 2)
        payoff_history.append(month_balances)
        
    return {
        "total_months": month if not safety_triggered else max_months_safety,
        "total_interest": round(total_interest_accumulated, 2),
        "payoff_history": payoff_history,
        "safety_triggered": safety_triggered
    }
