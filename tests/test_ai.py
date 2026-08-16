import pytest
from ai.prompt_engine import get_recovery_plan_prompt, AI_SAFETY_RULES
from ai.response_validator import validate_ai_response

def test_prompt_engine_formatting():
    profile = {"name": "Alice", "employment_status": "Employed", "financial_goal": "Free", "planning_period": 12}
    metrics = {"total_income": 4000.0, "essential_expenses": 1000.0, "discretionary_expenses": 500.0, "total_expenses": 1500.0, "total_monthly_debt_payment": 200.0, "disposable_income": 2300.0, "dti_ratio": 5.0, "savings_rate": 50.0, "expense_to_income_ratio": 37.5}
    debts = [{"name": "Card A", "type": "Credit Card", "balance": 1000.0, "apr": 18.0, "min_pay": 50.0, "emi": 50.0, "tenure": 24}]
    payoff_summary = {"total_months": 24, "total_interest": 200.0, "safety_triggered": False}
    
    prompt = get_recovery_plan_prompt(profile, metrics, debts, "Avalanche", payoff_summary)
    
    # Assert key tokens are in prompt
    assert "Alice" in prompt
    assert "4000.00" in prompt
    assert "Avalanche" in prompt
    assert "Card A" in prompt


def test_response_validator_valid():
    verified_metrics = {
        "total_income": 5000.0,
        "total_debt": 15000.0,
        "dti_ratio": 10.0,
        "total_months": 24
    }
    
    # Text with valid metrics and no guarantees
    ai_text = (
        "Based on your profile, your total income is $5,000. Your total outstanding debt is $15,000. "
        "Under the selected strategy, it will take you 24 months to become debt free. "
        "We recommend budgeting 3 to 6 months of expenses for emergencies."
    )
    
    res = validate_ai_response(ai_text, verified_metrics)
    assert res["is_valid"] is True
    assert len(res["warnings"]) == 0


def test_response_validator_hallucination():
    verified_metrics = {
        "total_income": 5000.0,
        "total_debt": 15000.0,
        "dti_ratio": 10.0
    }
    
    # Text with incorrect total debt ($95,000 instead of $15,000)
    ai_text_hallucinated = (
        "Your total income is $5,000, but your total debt is currently $95,000, which is extremely heavy. "
        "Also your monthly cash flow is $80,000."
    )
    
    res = validate_ai_response(ai_text_hallucinated, verified_metrics)
    assert res["is_valid"] is False
    assert len(res["warnings"]) > 0
    assert "95000" in str(res["warnings"]) or "80000" in str(res["warnings"])


def test_response_validator_guarantees():
    verified_metrics = {"total_income": 5000.0}
    
    # Text containing a credit repair guarantee
    ai_text_guarantee = (
        "We guarantee debt elimination within 6 months and we will clean up your credit history."
    )
    
    res = validate_ai_response(ai_text_guarantee, verified_metrics)
    assert res["is_valid"] is False
    assert any("guarantee" in w for w in res["warnings"])


def test_financial_assistant_offline():
    from ai.financial_assistant import FinancialAssistant
    from database.models import Base, User
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from unittest.mock import MagicMock
    
    # 1. Setup DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Create mock user
    user = User(username="default_user")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 2. Setup Assistant
    assistant = FinancialAssistant(db)
    
    # Mock Gemini and RAG calls
    assistant.ai_service.generate_text = MagicMock(return_value="Based on your profile, your total income is $0.00. We recommend creating an emergency buffer.")
    assistant.ai_service.is_configured = True
    assistant.rag_pipeline.get_grounded_answer = MagicMock(return_value={"answer": "Mock RAG data", "sources": []})
    
    # 3. Call Chat response
    response = assistant.get_assistant_response(user.id, "Explain emergency funds")
    
    assert "income is $0.00" in response
    
    # Confirm chat logs saved in DB
    from database.repository import get_chat_history
    history = get_chat_history(db, user.id)
    assert len(history) == 2
    assert history[0].sender == "user"
    assert history[1].sender == "assistant"
    
    db.close()

