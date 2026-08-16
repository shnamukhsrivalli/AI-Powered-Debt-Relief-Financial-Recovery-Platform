from typing import List
from database.models import Debt

def get_avalanche_priority(debts: List[Debt]) -> List[Debt]:
    """
    Sorts active debts by interest rate (APR) descending (highest first).
    If interest rates are equal, sorts by outstanding balance descending.
    """
    active_debts = [d for d in debts if d.status == "Active"]
    return sorted(
        active_debts, 
        key=lambda d: (-d.interest_rate, -d.outstanding_balance)
    )

def get_snowball_priority(debts: List[Debt]) -> List[Debt]:
    """
    Sorts active debts by outstanding balance ascending (smallest first).
    If outstanding balances are equal, sorts by interest rate descending.
    """
    active_debts = [d for d in debts if d.status == "Active"]
    return sorted(
        active_debts, 
        key=lambda d: (d.outstanding_balance, -d.interest_rate)
    )
