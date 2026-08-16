from ai.gemini_service import GeminiService
from ai.prompt_engine import AI_SAFETY_RULES, get_system_instruction
from ai.response_validator import validate_ai_response
from rag.pipeline import RAGPipeline
from database.repository import (
    get_profile, get_incomes, get_expenses, get_debts,
    add_chat_message, get_chat_history
)
from financial.analyzer import calculate_financial_metrics
from sqlalchemy.orm import Session
from typing import Dict, Any, List

class FinancialAssistant:
    """
    Coordinates the chatbot conversation by injecting the user's local database
    financial profile, retrieving RAG grounding context, calling Gemini,
    validating the response, and saving message history.
    """
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = GeminiService()
        self.rag_pipeline = RAGPipeline()
        
    def get_assistant_response(self, user_id: int, query: str) -> str:
        """
        Gathers profile, runs RAG, compiles prompt, queries Gemini, validates response.
        Appends to database chat logs automatically.
        """
        # 1. Fetch user financial statistics
        profile = get_profile(self.db, user_id)
        incomes = get_incomes(self.db, user_id)
        expenses = get_expenses(self.db, user_id)
        debts = get_debts(self.db, user_id)
        
        # Calculate cash flows
        metrics = calculate_financial_metrics(incomes, expenses, debts)
        active_debts = [d for d in debts if d.status == "Active"]
        
        # Format user financial state string
        profile_summary = (
            f"User Profile:\n"
            f"- Name: {profile.name if profile else 'Valued User'}\n"
            f"- Goal: {profile.financial_goal if profile else 'Debt Relief'}\n"
            f"- Net Monthly Income: {metrics['total_income']:.2f}\n"
            f"- Monthly Expenses: {metrics['total_expenses']:.2f}\n"
            f"- Active Debt Balance: {metrics['total_debt']:.2f}\n"
            f"- Monthly Debt Repayment: {metrics['total_monthly_debt_payment']:.2f}\n"
            f"- DTI Ratio: {metrics['dti_ratio']:.1f}%\n"
            f"- Disposable Cash: {metrics['disposable_income']:.2f}\n"
        )
        
        # 2. Retrieve grounded RAG context
        self.rag_pipeline.vector_store.load_index()
        rag_results = self.rag_pipeline.get_grounded_answer(query, k=2)
        rag_context = rag_results["answer"]
        
        # 3. Retrieve database Chat History (last 10 messages for sliding window context)
        db_history = get_chat_history(self.db, user_id, limit=10)
        history_str = ""
        for h in db_history:
            history_str += f"{h.sender.capitalize()}: {h.message}\n"
            
        # 4. Construct prompt injecting profile, RAG, and history
        prompt = f"""
You are the AI Financial Recovery Assistant. Help the user answer their query using their financial profile and RAG grounding material.

### USER'S VERIFIED FINANCIAL SUMMARY
{profile_summary}

### RAG KNOWLEDGE REFERENCE
{rag_context}

### PREVIOUS CONVERSATION HISTORY
{history_str if history_str else "No prior history."}
User: {query}

### GROUNDED ASSISTANT RESPONSE
Answer the query. Refer to their DTI, savings, or specific debts if relevant to their question. 
Answer in a supportive, objective tone. Use bullet points for readability.
"""
        
        system_instruction = f"""
You are the AI Financial Recovery Assistant.
{AI_SAFETY_RULES}
"""
        
        # 5. Call Gemini
        raw_response = self.ai_service.generate_text(prompt, system_instruction=system_instruction, temperature=0.3)
        
        # 6. Validate response
        verified_numbers = {
            "total_income": metrics["total_income"],
            "total_expenses": metrics["total_expenses"],
            "total_debt": metrics["total_debt"],
            "dti_ratio": metrics["dti_ratio"],
            "savings_rate": metrics["savings_rate"]
        }
        validation = validate_ai_response(raw_response, verified_numbers)
        sanitized_response = validation["sanitized_text"]
        
        # 7. Save to DB chat history logs
        add_chat_message(self.db, user_id, sender="user", message=query)
        add_chat_message(self.db, user_id, sender="assistant", message=sanitized_response)
        
        return sanitized_response
