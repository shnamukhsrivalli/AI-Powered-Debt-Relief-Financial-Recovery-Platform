import pytest
from pydantic import ValidationError
from models.debt_models import DebtSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Debt
from database.repository import add_debt, get_debts, update_debt, delete_debt

# Test Debt validation schema
def test_debt_validation():
    # Valid debt
    data = {
        "name": "Credit Card A",
        "debt_type": "Credit Card",
        "outstanding_balance": 5000.0,
        "original_principal": 10000.0,
        "interest_rate": 18.5,
        "minimum_payment": 200.0,
        "emi": 250.0,
        "due_date": "15th",
        "remaining_tenure": 24,
        "status": "Active"
    }
    debt = DebtSchema(**data)
    assert debt.name == "Credit Card A"
    assert debt.interest_rate == 18.5

    # Negative APR
    invalid_data = data.copy()
    invalid_data["interest_rate"] = -5.0
    with pytest.raises(ValidationError):
        DebtSchema(**invalid_data)

    # Negative balance
    invalid_data2 = data.copy()
    invalid_data2["outstanding_balance"] = -100.0
    with pytest.raises(ValidationError):
        DebtSchema(**invalid_data2)


# Test DB Debt CRUD
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_db_debt_crud(db_session):
    # Add debt
    debt1 = add_debt(
        db_session,
        user_id=1,
        name="Visa Card",
        debt_type="Credit Card",
        outstanding_balance=3000.0,
        original_principal=5000.0,
        interest_rate=24.0,
        minimum_payment=150.0,
        emi=200.0,
        due_date="20",
        remaining_tenure=18
    )
    assert debt1.id is not None
    assert debt1.status == "Active"

    # Get debts
    debts = get_debts(db_session, user_id=1)
    assert len(debts) == 1
    assert debts[0].name == "Visa Card"

    # Update status
    update_debt(
        db_session,
        debt1.id,
        name="Visa Card Premium",
        debt_type="Credit Card",
        outstanding_balance=1000.0,
        original_principal=5000.0,
        interest_rate=24.0,
        minimum_payment=100.0,
        emi=200.0,
        due_date="20",
        remaining_tenure=6,
        status="Active"
    )
    updated = get_debts(db_session, user_id=1)[0]
    assert updated.name == "Visa Card Premium"
    assert updated.outstanding_balance == 1000.0

    # Delete
    delete_debt(db_session, debt1.id)
    debts_after = get_debts(db_session, user_id=1)
    assert len(debts_after) == 0


def test_strategy_sorting():
    from financial.debt_engine import get_avalanche_priority, get_snowball_priority
    
    debts = [
        Debt(name="Card A", outstanding_balance=5000.0, interest_rate=15.0, status="Active"),
        Debt(name="Loan B", outstanding_balance=12000.0, interest_rate=8.0, status="Active"),
        Debt(name="Card C", outstanding_balance=2000.0, interest_rate=24.0, status="Active")
    ]
    
    # Avalanche priority: Card C (24%), Card A (15%), Loan B (8%)
    av_sorted = get_avalanche_priority(debts)
    assert av_sorted[0].name == "Card C"
    assert av_sorted[1].name == "Card A"
    assert av_sorted[2].name == "Loan B"
    
    # Snowball priority: Card C ($2000), Card A ($5000), Loan B ($12000)
    sb_sorted = get_snowball_priority(debts)
    assert sb_sorted[0].name == "Card C"
    assert sb_sorted[1].name == "Card A"
    assert sb_sorted[2].name == "Loan B"


def test_simulate_payoff_calc():
    from financial.payoff_calculator import simulate_payoff
    
    debts = [
        Debt(name="Card X", outstanding_balance=1000.0, interest_rate=12.0, minimum_payment=100.0, status="Active"),
        Debt(name="Card Y", outstanding_balance=2000.0, interest_rate=24.0, minimum_payment=100.0, status="Active")
    ]
    
    # Simulate with extra payment of $100 (total payment = $300/mo)
    res_av = simulate_payoff(debts, "avalanche", extra_payment=100.0)
    
    assert res_av["total_months"] > 0
    assert res_av["total_interest"] > 0.0
    assert len(res_av["payoff_history"]) > 0
    assert not res_av["safety_triggered"]

