import os
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from config.settings import ML_MODEL_DIR

def generate_synthetic_data(num_samples: int = 5000) -> pd.DataFrame:
    """
    Generates a mathematically consistent synthetic dataset representing credit/debt risk profiles.
    Rules mimic real-world risk indicators with injected random noise.
    """
    np.random.seed(42)  # For reproducibility
    
    incomes = np.random.uniform(2000, 15000, num_samples)
    active_debts_counts = np.random.randint(0, 7, num_samples)
    
    # Generate total debt relative to annual income
    debt_to_annual_income_factors = np.random.exponential(scale=0.3, size=num_samples)
    total_debts = incomes * 12 * debt_to_annual_income_factors
    # Zero out debt if active_debts_count is 0
    total_debts = np.where(active_debts_counts == 0, 0.0, total_debts)
    
    # Calculate monthly debt payments (estimate ~2% of total outstanding balance as minimum)
    monthly_debt_payments = total_debts * np.random.uniform(0.015, 0.03, num_samples)
    monthly_debt_payments = np.where(active_debts_counts == 0, 0.0, monthly_debt_payments)
    
    # Generate expense ratios
    expense_ratios = np.random.uniform(30, 95, num_samples)
    monthly_expenses = incomes * (expense_ratios / 100.0)
    
    # Calculate derived features
    dti_ratios = (monthly_debt_payments / incomes) * 100.0
    disposable_incomes = incomes - monthly_expenses - monthly_debt_payments
    savings_rates = np.where(disposable_incomes > 0, (disposable_incomes / incomes) * 100.0, 0.0)
    
    # Max APR estimation
    max_aprs = np.where(
        active_debts_counts > 0,
        np.random.uniform(5.0, 36.0, num_samples),
        0.0
    )
    
    # Classify labels based on heuristics
    labels = []
    for i in range(num_samples):
        # Criteria for Critical Risk
        if dti_ratios[i] > 50.0 or savings_rates[i] <= 0.0 or expense_ratios[i] > 85.0:
            labels.append("Critical Risk")
        # Criteria for High Risk
        elif dti_ratios[i] > 36.0 or expense_ratios[i] > 70.0:
            labels.append("High Risk")
        # Criteria for Moderate Risk
        elif dti_ratios[i] > 20.0 or savings_rates[i] < 10.0:
            labels.append("Moderate Risk")
        else:
            labels.append("Low Risk")
            
    # Add random noise (5% chance of label flipping) to challenge the ML model
    for i in range(num_samples):
        if np.random.rand() < 0.05:
            labels[i] = np.random.choice(["Low Risk", "Moderate Risk", "High Risk", "Critical Risk"])
            
    df = pd.DataFrame({
        "income": incomes,
        "total_debt": total_debts,
        "dti_ratio": dti_ratios,
        "expense_ratio": expense_ratios,
        "savings_rate": savings_rates,
        "active_debts_count": active_debts_counts.astype(float),
        "max_apr": max_aprs,
        "disposable_income": disposable_incomes,
        "risk_level": labels
    })
    
    return df

def train_risk_model():
    """Trains a Random Forest Classifier on synthetic credit risk data and exports model."""
    print("Generating synthetic financial risk dataset...")
    df = generate_synthetic_data(num_samples=5000)
    
    X = df[[
        "income", "total_debt", "dti_ratio", "expense_ratio", 
        "savings_rate", "active_debts_count", "max_apr", "disposable_income"
    ]]
    y = df["risk_level"]
    
    # 80-20 Train-Test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training RandomForest classifier...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model trained successfully. Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    ML_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = ML_MODEL_DIR / "risk_model.joblib"
    joblib.dump(model, str(model_path))
    print(f"Saved trained risk model to: {model_path}")
    
if __name__ == "__main__":
    train_risk_model()
