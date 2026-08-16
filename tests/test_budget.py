import pytest
from financial.analyzer import calculate_financial_metrics
from financial.health_score import calculate_health_score
from database.models import Income, Expense, Debt

def test_financial_metrics_calculation():
    # Setup mock records
    incomes = [
        Income(source="Salary", amount=5000.0, frequency="Monthly"),
        Income(source="Bonus", amount=1000.0, frequency="Monthly")
    ]
    expenses = [
        Expense(category="Rent", amount=1500.0, classification="Essential"),
        Expense(category="Utilities", amount=300.0, classification="Essential"),
        Expense(category="Dining Out", amount=400.0, classification="Discretionary")
    ]
    debts = [
        Debt(name="Credit Card A", outstanding_balance=5000.0, minimum_payment=200.0, status="Active"),
        Debt(name="Personal Loan B", outstanding_balance=10000.0, minimum_payment=300.0, status="Active"),
        Debt(name="Paid Card", outstanding_balance=0.0, minimum_payment=0.0, status="Paid")
    ]
    
    metrics = calculate_financial_metrics(incomes, expenses, debts)
    
    assert metrics["total_income"] == 6000.0
    assert metrics["essential_expenses"] == 1800.0
    assert metrics["discretionary_expenses"] == 400.0
    assert metrics["total_expenses"] == 2200.0
    assert metrics["total_debt"] == 15000.0
    assert metrics["total_monthly_debt_payment"] == 500.0
    
    # Ratios
    # DTI = 500 / 6000 * 100 = 8.33%
    assert round(metrics["dti_ratio"], 2) == 8.33
    # Expense Ratio = 2200 / 6000 * 100 = 36.67%
    assert round(metrics["expense_to_income_ratio"], 2) == 36.67
    # Disposable Income = 6000 - 2200 - 500 = 3300.0
    assert metrics["disposable_income"] == 3300.0
    # Savings Rate = 3300 / 6000 * 100 = 55%
    assert metrics["savings_rate"] == pytest.approx(55.0)


def test_health_score_calculation():
    # Perfect financial profile metrics
    metrics = {
        "total_income": 10000.0,
        "dti_ratio": 5.0,
        "savings_rate": 25.0,
        "expense_to_income_ratio": 30.0,
        "total_debt": 2000.0,
        "disposable_income": 5000.0
    }
    # Low APR active debt
    debts = [
        Debt(name="Loan", outstanding_balance=2000.0, interest_rate=5.0, minimum_payment=100.0, status="Active")
    ]
    
    score_data = calculate_health_score(metrics, debts)
    
    assert score_data["health_score"] >= 80.0
    assert score_data["risk_level"] == "Low Risk"
    assert len(score_data["positive_factors"]) > 0
    
    # Zero income profile
    zero_metrics = {
        "total_income": 0.0,
        "dti_ratio": 0.0,
        "savings_rate": 0.0,
        "expense_to_income_ratio": 0.0,
        "total_debt": 0.0,
        "disposable_income": 0.0
    }
    zero_score = calculate_health_score(zero_metrics, [])
    assert zero_score["health_score"] == 0.0
    assert zero_score["risk_level"] == "Critical Risk"


def test_what_if_analysis():
    from financial.what_if_engine import run_what_if_analysis
    
    debts = [
        Debt(name="Card X", outstanding_balance=2000.0, interest_rate=18.0, minimum_payment=100.0, status="Active")
    ]
    
    # Base: extra = $0 (total payment = $100/mo)
    # Scenario: extra = $100 (total payment = $200/mo)
    results = run_what_if_analysis(debts, "avalanche", base_extra_payment=0.0, scenario_extra_payment=100.0)
    
    assert results["months_saved"] > 0
    assert results["interest_saved"] > 0.0
    assert results["base"]["total_months"] > results["scenario"]["total_months"]

