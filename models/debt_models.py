from pydantic import BaseModel, Field, field_validator
from typing import Optional

class DebtSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Name of the debt")
    debt_type: str = Field(..., description="Type of debt")
    outstanding_balance: float = Field(..., ge=0.0, description="Outstanding balance")
    original_principal: float = Field(..., ge=0.0, description="Original principal borrowed")
    interest_rate: float = Field(..., ge=0.0, le=100.0, description="Annual Interest Rate (APR)")
    minimum_payment: float = Field(..., ge=0.0, description="Minimum monthly payment")
    emi: float = Field(..., ge=0.0, description="Equated Monthly Installment")
    due_date: Optional[str] = Field(None, description="Due day of the month")
    remaining_tenure: int = Field(..., ge=0, description="Remaining payoff tenure in months")
    status: str = Field(default="Active", description="Active or Paid")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Debt name cannot be empty.")
        return value.strip()

    @field_validator("minimum_payment")
    @classmethod
    def validate_min_payment(cls, value: float, info) -> float:
        # Check against emi or other calculations if needed, otherwise just validate value
        return value
