from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UserProfileSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="User's name")
    age_range: str = Field(..., description="Age group (e.g., 18-25, 26-35)")
    employment_status: str = Field(..., description="Employment type")
    financial_goal: str = Field(..., description="Primary financial objective")
    planning_period: int = Field(default=12, ge=1, le=120, description="Planning period in months")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Name cannot be empty or just whitespace.")
        return value.strip()


class IncomeSchema(BaseModel):
    source: str = Field(..., description="Source of income")
    amount: float = Field(..., ge=0.0, description="Income amount")
    frequency: str = Field(default="Monthly", description="How often income is earned")

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Income source cannot be empty.")
        return value.strip()


class ExpenseSchema(BaseModel):
    category: str = Field(..., description="Category of expense")
    amount: float = Field(..., ge=0.0, description="Monthly expense amount")
    classification: str = Field(..., description="Essential or Discretionary")

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, value: str) -> str:
        if value not in ["Essential", "Discretionary"]:
            raise ValueError("Classification must be 'Essential' or 'Discretionary'")
        return value
