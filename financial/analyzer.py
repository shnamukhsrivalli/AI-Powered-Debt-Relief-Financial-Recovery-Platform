from typing import List, Dict, Any
from database.models import Income, Expense, Debt

def calculate_financial_metrics(incomes: List[Income], expenses: List[Expense], debts: List[Debt]) -> Dict[str, Any]:
    """
    Calculates primary financial metrics using Python mathematical formulas.
    Handles division-by-zero, empty inputs, and invalid numbers.
    """
    # 1. Total Monthly Income
    total_income = sum(inc.amount for inc in incomes)
    
    # 2. Expenses by classification
    essential_expenses = sum(exp.amount for exp in expenses if exp.classification == "Essential")
    discretionary_expenses = sum(exp.amount for exp in expenses if exp.classification == "Discretionary")
    total_expenses = essential_expenses + discretionary_expenses
    
    # 3. Debt metrics (Active debts only)
    active_debts = [d for d in debts if d.status == "Active"]
    total_debt = sum(d.outstanding_balance for d in active_debts)
    total_monthly_debt_payment = sum(d.minimum_payment for d in active_debts)
    
    # 4. Debt-to-Income (DTI) Ratio
    dti_ratio = (total_monthly_debt_payment / total_income * 100) if total_income > 0 else 0.0
    
    # 5. Expense-to-Income Ratio
    expense_to_income_ratio = (total_expenses / total_income * 100) if total_income > 0 else 0.0
    
    # 6. Disposable Income (Income - Expenses - Debt payments)
    disposable_income = total_income - total_expenses - total_monthly_debt_payment
    
    # 7. Savings Rate
    # Savings are equal to disposable income if positive, otherwise 0.
    savings_rate = (disposable_income / total_income * 100) if (total_income > 0 and disposable_income > 0) else 0.0
    
    return {
        "total_income": total_income,
        "essential_expenses": essential_expenses,
        "discretionary_expenses": discretionary_expenses,
        "total_expenses": total_expenses,
        "total_debt": total_debt,
        "total_monthly_debt_payment": total_monthly_debt_payment,
        "dti_ratio": dti_ratio,
        "expense_to_income_ratio": expense_to_income_ratio,
        "disposable_income": disposable_income,
        "savings_rate": savings_rate
    }
