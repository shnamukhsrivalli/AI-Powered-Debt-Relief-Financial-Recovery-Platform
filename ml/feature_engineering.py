import numpy as np
from typing import Dict, Any, List
from database.models import Debt

FEATURE_NAMES = [
    "income",
    "total_debt",
    "dti_ratio",
    "expense_ratio",
    "savings_rate",
    "active_debts_count",
    "max_apr",
    "disposable_income"
]

def extract_features(metrics: Dict[str, Any], debts: List[Debt]) -> np.ndarray:
    """
    Extracts numerical features from cash flow metrics and active debts.
    Returns a numpy array of shape (1, 8) ready for model prediction.
    """
    active_debts = [d for d in debts if d.status == "Active"]
    
    income = float(metrics.get("total_income", 0.0))
    total_debt = float(metrics.get("total_debt", 0.0))
    dti_ratio = float(metrics.get("dti_ratio", 0.0))
    expense_ratio = float(metrics.get("expense_to_income_ratio", 0.0))
    savings_rate = float(metrics.get("savings_rate", 0.0))
    active_debts_count = float(len(active_debts))
    max_apr = float(max((d.interest_rate for d in active_debts), default=0.0))
    disposable_income = float(metrics.get("disposable_income", 0.0))
    
    features = [
        income,
        total_debt,
        dti_ratio,
        expense_ratio,
        savings_rate,
        active_debts_count,
        max_apr,
        disposable_income
    ]
    
    return np.array([features])
