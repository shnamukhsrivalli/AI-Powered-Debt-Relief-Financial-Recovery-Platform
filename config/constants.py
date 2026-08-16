# Income types
INCOME_CATEGORIES = [
    "Salary",
    "Freelance / Contract",
    "Business / Self-Employment",
    "Investments",
    "Other Income"
]

# Expense categories & classifications
EXPENSE_CATEGORIES = {
    "Rent / Mortgage": "Essential",
    "Groceries & Food": "Essential",
    "Utilities (Electricity, Water, Internet)": "Essential",
    "Transportation / Fuel / Transit": "Essential",
    "Healthcare & Insurance": "Essential",
    "Education & Tuition": "Essential",
    "Minimum Debt Payments": "Essential",  # Handled separately in calculations but logged
    "Dining Out / Delivery": "Discretionary",
    "Subscriptions & Streaming": "Discretionary",
    "Entertainment & Hobbies": "Discretionary",
    "Shopping & Lifestyle": "Discretionary",
    "Travel & Vacation": "Discretionary",
    "Miscellaneous / Other": "Discretionary"
}

# Debt types
DEBT_TYPES = [
    "Credit Card",
    "Personal Loan",
    "Home Loan / Mortgage",
    "Auto Loan",
    "Student Loan",
    "Medical Debt",
    "Business Loan",
    "Other Debt"
]

# Debt status
DEBT_STATUS_ACTIVE = "Active"
DEBT_STATUS_PAID = "Paid"

# Risk Assessment Thresholds (DTI, Expense ratios)
DTI_LOW_THRESHOLD = 20.0        # <20% is low risk
DTI_MODERATE_THRESHOLD = 36.0   # 20%-36% is moderate risk
DTI_HIGH_THRESHOLD = 50.0       # 36%-50% is high risk, >50% is critical risk

EXPENSE_RATIO_SAFE = 50.0       # <=50% of income spent on essential/discretionary
EXPENSE_RATIO_WARN = 75.0       # >75% of income spent is high risk

# Financial Safety Disclaimer
DISCLAIMER_TEXT = (
    "Disclaimer: This platform provides educational and informational financial guidance "
    "based on the information supplied by the user. It does not replace professional financial, "
    "legal, tax, credit, or investment advice. Results are estimates and actual outcomes may vary."
)
