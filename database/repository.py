from sqlalchemy.orm import Session
from database.models import User, FinancialProfile, Income, Expense, Debt, FinancialAnalysis, RecoveryPlan, Progress, ChatHistory
from datetime import datetime

# Helper: Get or Create default user (since this is a single user app, we default to username 'default_user')
def get_default_user(db: Session) -> User:
    user = db.query(User).filter(User.username == "default_user").first()
    if not user:
        user = User(username="default_user")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# --- PROFILE CRUD ---
def get_profile(db: Session, user_id: int) -> FinancialProfile:
    return db.query(FinancialProfile).filter(FinancialProfile.user_id == user_id).first()

def save_profile(db: Session, user_id: int, name: str, age_range: str, employment_status: str, financial_goal: str, planning_period: int) -> FinancialProfile:
    profile = get_profile(db, user_id)
    if profile:
        profile.name = name
        profile.age_range = age_range
        profile.employment_status = employment_status
        profile.financial_goal = financial_goal
        profile.planning_period = planning_period
    else:
        profile = FinancialProfile(
            user_id=user_id,
            name=name,
            age_range=age_range,
            employment_status=employment_status,
            financial_goal=financial_goal,
            planning_period=planning_period
        )
        db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

# --- INCOME CRUD ---
def get_incomes(db: Session, user_id: int):
    return db.query(Income).filter(Income.user_id == user_id).all()

def add_income(db: Session, user_id: int, source: str, amount: float, frequency: str = "Monthly") -> Income:
    income = Income(user_id=user_id, source=source, amount=amount, frequency=frequency)
    db.add(income)
    db.commit()
    db.refresh(income)
    return income

def update_income(db: Session, income_id: int, source: str, amount: float, frequency: str = "Monthly") -> Income:
    income = db.query(Income).filter(Income.id == income_id).first()
    if income:
        income.source = source
        income.amount = amount
        income.frequency = frequency
        db.commit()
        db.refresh(income)
    return income

def delete_income(db: Session, income_id: int) -> bool:
    income = db.query(Income).filter(Income.id == income_id).first()
    if income:
        db.delete(income)
        db.commit()
        return True
    return False

# --- EXPENSE CRUD ---
def get_expenses(db: Session, user_id: int):
    return db.query(Expense).filter(Expense.user_id == user_id).all()

def add_expense(db: Session, user_id: int, category: str, amount: float, classification: str) -> Expense:
    expense = Expense(user_id=user_id, category=category, amount=amount, classification=classification)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

def update_expense(db: Session, expense_id: int, category: str, amount: float, classification: str) -> Expense:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense:
        expense.category = category
        expense.amount = amount
        expense.classification = classification
        db.commit()
        db.refresh(expense)
    return expense

def delete_expense(db: Session, expense_id: int) -> bool:
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if expense:
        db.delete(expense)
        db.commit()
        return True
    return False

# --- DEBT CRUD ---
def get_debts(db: Session, user_id: int):
    return db.query(Debt).filter(Debt.user_id == user_id).all()

def add_debt(db: Session, user_id: int, name: str, debt_type: str, outstanding_balance: float, 
             original_principal: float, interest_rate: float, minimum_payment: float, emi: float, 
             due_date: str, remaining_tenure: int, status: str = "Active") -> Debt:
    debt = Debt(
        user_id=user_id, name=name, debt_type=debt_type, outstanding_balance=outstanding_balance,
        original_principal=original_principal, interest_rate=interest_rate, minimum_payment=minimum_payment,
        emi=emi, due_date=due_date, remaining_tenure=remaining_tenure, status=status
    )
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt

def update_debt(db: Session, debt_id: int, name: str, debt_type: str, outstanding_balance: float, 
                original_principal: float, interest_rate: float, minimum_payment: float, emi: float, 
                due_date: str, remaining_tenure: int, status: str) -> Debt:
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if debt:
        debt.name = name
        debt.debt_type = debt_type
        debt.outstanding_balance = outstanding_balance
        debt.original_principal = original_principal
        debt.interest_rate = interest_rate
        debt.minimum_payment = minimum_payment
        debt.emi = emi
        debt.due_date = due_date
        debt.remaining_tenure = remaining_tenure
        debt.status = status
        db.commit()
        db.refresh(debt)
    return debt

def delete_debt(db: Session, debt_id: int) -> bool:
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if debt:
        db.delete(debt)
        db.commit()
        return True
    return False

# --- FINANCIAL ANALYSIS CACHE ---
def get_latest_analysis(db: Session, user_id: int) -> FinancialAnalysis:
    return db.query(FinancialAnalysis).filter(FinancialAnalysis.user_id == user_id).order_by(FinancialAnalysis.created_at.desc()).first()

def save_analysis(db: Session, user_id: int, total_debt: float, total_monthly_payment: float, 
                  debt_to_income_ratio: float, expense_to_income_ratio: float, disposable_income: float, 
                  savings_rate: float, health_score: float, risk_level: str) -> FinancialAnalysis:
    analysis = FinancialAnalysis(
        user_id=user_id,
        total_debt=total_debt,
        total_monthly_payment=total_monthly_payment,
        debt_to_income_ratio=debt_to_income_ratio,
        expense_to_income_ratio=expense_to_income_ratio,
        disposable_income=disposable_income,
        savings_rate=savings_rate,
        health_score=health_score,
        risk_level=risk_level
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

# --- RECOVERY PLAN CACHE ---
def get_latest_recovery_plan(db: Session, user_id: int) -> RecoveryPlan:
    return db.query(RecoveryPlan).filter(RecoveryPlan.user_id == user_id).order_by(RecoveryPlan.created_at.desc()).first()

def save_recovery_plan(db: Session, user_id: int, plan_content: str, strategy_type: str) -> RecoveryPlan:
    plan = RecoveryPlan(
        user_id=user_id,
        plan_content=plan_content,
        strategy_type=strategy_type
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

# --- PROGRESS LOGS ---
def get_progress_logs(db: Session, user_id: int):
    return db.query(Progress).filter(Progress.user_id == user_id).order_by(Progress.month_year.asc()).all()

def add_progress_log(db: Session, user_id: int, month_year: str, debt_paid: float, 
                     remaining_debt: float, savings_added: float, milestones_achieved: str = None) -> Progress:
    log = db.query(Progress).filter(Progress.user_id == user_id, Progress.month_year == month_year).first()
    if log:
        log.debt_paid = debt_paid
        log.remaining_debt = remaining_debt
        log.savings_added = savings_added
        if milestones_achieved:
            log.milestones_achieved = milestones_achieved
    else:
        log = Progress(
            user_id=user_id,
            month_year=month_year,
            debt_paid=debt_paid,
            remaining_debt=remaining_debt,
            savings_added=savings_added,
            milestones_achieved=milestones_achieved
        )
        db.add(log)
    db.commit()
    db.refresh(log)
    return log

# --- CHAT HISTORY ---
def get_chat_history(db: Session, user_id: int, limit: int = 50):
    return db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.asc()).limit(limit).all()

def add_chat_message(db: Session, user_id: int, sender: str, message: str) -> ChatHistory:
    chat = ChatHistory(user_id=user_id, sender=sender, message=message)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

def clear_chat_history(db: Session, user_id: int):
    db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete()
    db.commit()
