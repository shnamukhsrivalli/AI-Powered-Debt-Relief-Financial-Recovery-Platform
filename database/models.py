from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, default="default_user")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("FinancialProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    incomes = relationship("Income", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("FinancialAnalysis", back_populates="user", cascade="all, delete-orphan")
    recovery_plans = relationship("RecoveryPlan", back_populates="user", cascade="all, delete-orphan")
    progress_logs = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    name = Column(String, nullable=False)
    age_range = Column(String, nullable=False)
    employment_status = Column(String, nullable=False)
    financial_goal = Column(String, nullable=False)
    planning_period = Column(Integer, default=12)  # Months
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    source = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String, default="Monthly")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="incomes")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    classification = Column(String, nullable=False)  # "Essential" or "Discretionary"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="expenses")


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    debt_type = Column(String, nullable=False)
    outstanding_balance = Column(Float, nullable=False)
    original_principal = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)  # Annual percentage
    minimum_payment = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)
    due_date = Column(String, nullable=True)  # Day of the month
    remaining_tenure = Column(Integer, nullable=False)  # Months
    status = Column(String, default="Active")  # "Active" or "Paid"
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="debts")


class FinancialAnalysis(Base):
    __tablename__ = "financial_analysis"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_debt = Column(Float, nullable=False)
    total_monthly_payment = Column(Float, nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)
    expense_to_income_ratio = Column(Float, nullable=False)
    disposable_income = Column(Float, nullable=False)
    savings_rate = Column(Float, nullable=False)
    health_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")


class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_content = Column(Text, nullable=False)  # AI-generated plan JSON or markdown
    strategy_type = Column(String, nullable=False)  # "Avalanche" or "Snowball"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recovery_plans")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month_year = Column(String, nullable=False)  # e.g., "YYYY-MM"
    debt_paid = Column(Float, default=0.0)
    remaining_debt = Column(Float, nullable=False)
    savings_added = Column(Float, default=0.0)
    milestones_achieved = Column(Text, nullable=True)  # Comma-separated or JSON list
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_logs")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender = Column(String, nullable=False)  # "user" or "assistant"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_histories")
