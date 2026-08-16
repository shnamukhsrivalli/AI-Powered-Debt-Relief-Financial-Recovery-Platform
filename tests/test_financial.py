import pytest
from pydantic import ValidationError
from models.financial_models import UserProfileSchema, IncomeSchema, ExpenseSchema
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.repository import save_profile, get_profile, add_income, get_incomes, delete_income

# Test Schemas Validation
def test_profile_validation():
    # Valid data
    data = {
        "name": "Jane Doe",
        "age_range": "26-35",
        "employment_status": "Employed Full-Time",
        "financial_goal": "Become Debt Free",
        "planning_period": 24
    }
    profile = UserProfileSchema(**data)
    assert profile.name == "Jane Doe"
    assert profile.planning_period == 24

    # Invalid name (empty)
    invalid_data = data.copy()
    invalid_data["name"] = "   "
    with pytest.raises(ValidationError):
        UserProfileSchema(**invalid_data)

    # Invalid planning period (too large)
    invalid_data2 = data.copy()
    invalid_data2["planning_period"] = 200
    with pytest.raises(ValidationError):
        UserProfileSchema(**invalid_data2)


def test_income_validation():
    # Valid
    inc = IncomeSchema(source="Freelance", amount=1500.0, frequency="Monthly")
    assert inc.amount == 1500.0

    # Negative amount
    with pytest.raises(ValidationError):
        IncomeSchema(source="Freelance", amount=-100.0)


def test_expense_validation():
    # Valid essential
    exp = ExpenseSchema(category="Rent", amount=1200.0, classification="Essential")
    assert exp.classification == "Essential"

    # Invalid classification
    with pytest.raises(ValidationError):
        ExpenseSchema(category="Rent", amount=1200.0, classification="Luxurious")


# Test Database Operations (In-Memory SQLite)
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_db_profile_crud(db_session):
    # Save a profile
    profile = save_profile(
        db_session,
        user_id=1,
        name="John Doe",
        age_range="36-45",
        employment_status="Self-Employed",
        financial_goal="Improve Savings Rate",
        planning_period=18
    )
    assert profile.user_id == 1
    assert profile.name == "John Doe"

    # Retrieve
    retrieved = get_profile(db_session, user_id=1)
    assert retrieved.name == "John Doe"
    assert retrieved.planning_period == 18


def test_db_income_crud(db_session):
    # Add
    inc1 = add_income(db_session, user_id=1, source="Job", amount=5000.0)
    inc2 = add_income(db_session, user_id=1, source="Dividends", amount=200.0)

    incomes = get_incomes(db_session, user_id=1)
    assert len(incomes) == 2
    assert incomes[0].amount == 5000.0

    # Delete
    delete_income(db_session, inc2.id)
    incomes_after = get_incomes(db_session, user_id=1)
    assert len(incomes_after) == 1
    assert incomes_after[0].source == "Job"


def test_compile_report_text(db_session):
    from ui.reports import compile_report_text
    from database.repository import get_default_user, save_profile
    
    # Setup mock user and profile
    user = get_default_user(db_session)
    save_profile(db_session, user.id, "John Doe", "26-35", "Employed", "Become Debt Free", 12)
    
    # Run report compile
    report_text = compile_report_text(db_session, user)
    
    assert "PERSONAL FINANCIAL RECOVERY & DEBT RELIEF REPORT" in report_text
    assert "John Doe" in report_text
    assert "Become Debt Free" in report_text
    assert "CASH FLOW SUMMARY" in report_text
    assert "DISCLAIMER" in report_text

