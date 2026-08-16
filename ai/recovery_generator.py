from ai.gemini_service import GeminiService
from ai.prompt_engine import get_recovery_plan_prompt
from ai.response_validator import validate_ai_response
from financial.analyzer import calculate_financial_metrics
from financial.payoff_calculator import simulate_payoff
from database.repository import save_recovery_plan, get_latest_recovery_plan
from sqlalchemy.orm import Session
from typing import Dict, Any

class RecoveryPlanGenerator:
    """
    Orchestrates the generation, validation, and storage of AI-powered
    personal financial recovery plans.
    """
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = GeminiService()
        
    def generate_plan(self, user_id: int, profile_obj: Any, incomes: list, expenses: list, debts: list, strategy: str, extra_payment: float = 0.0) -> str:
        """
        Runs Python engines to compute metrics and payoff schedules, compiles
        structured prompts, triggers Gemini, validates the response, and caches in DB.
        """
        # 1. Run Python calculations
        metrics = calculate_financial_metrics(incomes, expenses, debts)
        
        # Determine payoff schedule
        payoff_summary = simulate_payoff(debts, strategy, extra_payment)
        
        # Structure profile and debt list for the prompt
        profile_dict = {
            "name": profile_obj.name if profile_obj else "Valued User",
            "employment_status": profile_obj.employment_status if profile_obj else "Active",
            "financial_goal": profile_obj.financial_goal if profile_obj else "Debt Relief",
            "planning_period": profile_obj.planning_period if profile_obj else 12
        }
        
        debts_list = []
        for d in debts:
            if d.status == "Active":
                debts_list.append({
                    "name": d.name,
                    "type": d.debt_type,
                    "balance": d.outstanding_balance,
                    "apr": d.interest_rate,
                    "min_pay": d.minimum_payment,
                    "emi": d.emi,
                    "tenure": d.remaining_tenure
                })
                
        # 2. Compile Prompt
        prompt = get_recovery_plan_prompt(
            profile=profile_dict,
            metrics=metrics,
            debts_list=debts_list,
            strategy=strategy,
            payoff_summary=payoff_summary
        )
        
        # 3. Call Gemini API
        system_instruction = "You are an AI Financial Recovery Planner. Provide supportive, numbers-grounded advice."
        raw_plan = self.ai_service.generate_text(prompt, system_instruction=system_instruction)
        
        # 4. Validate output using response validator
        # Build collection of verified numbers to check for hallucinations
        verified_numbers = {
            "total_income": metrics["total_income"],
            "total_expenses": metrics["total_expenses"],
            "total_debt": metrics["total_debt"],
            "dti_ratio": metrics["dti_ratio"],
            "savings_rate": metrics["savings_rate"],
            "total_months": payoff_summary["total_months"],
            "total_interest": payoff_summary["total_interest"]
        }
        
        validation_results = validate_ai_response(raw_plan, verified_numbers)
        sanitized_plan = validation_results["sanitized_text"]
        
        # 5. Save the generated plan to the database
        save_recovery_plan(self.db, user_id, sanitized_plan, strategy)
        
        return sanitized_plan
