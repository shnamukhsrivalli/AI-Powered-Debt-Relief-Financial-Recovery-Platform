import pytest
import os
import numpy as np
from ml.feature_engineering import extract_features, FEATURE_NAMES
from ml.train import generate_synthetic_data, train_risk_model
from ml.predictor import RiskPredictor
from database.models import Debt

def test_feature_engineering():
    metrics = {
        "total_income": 6000.0,
        "total_debt": 15000.0,
        "dti_ratio": 25.0,
        "expense_to_income_ratio": 40.0,
        "savings_rate": 35.0,
        "disposable_income": 2000.0
    }
    debts = [
        Debt(name="Card", outstanding_balance=5000.0, interest_rate=18.0, status="Active"),
        Debt(name="Loan", outstanding_balance=10000.0, interest_rate=8.0, status="Active")
    ]
    
    features = extract_features(metrics, debts)
    
    assert features.shape == (1, 8)
    assert features[0][0] == 6000.0  # income
    assert features[0][1] == 15000.0  # total_debt
    assert features[0][2] == 25.0  # DTI
    assert features[0][3] == 40.0  # expense ratio
    assert features[0][4] == 35.0  # savings rate
    assert features[0][5] == 2.0  # debts count
    assert features[0][6] == 18.0  # max APR
    assert features[0][7] == 2000.0  # disposable income


def test_synthetic_data_generation():
    df = generate_synthetic_data(num_samples=100)
    assert len(df) == 100
    for name in FEATURE_NAMES:
        assert name in df.columns
    assert "risk_level" in df.columns
    # Check that categories match expected values
    assert df["risk_level"].nunique() <= 4


def test_model_training_and_predictor(tmp_path):
    # Setup model path mock in settings or run normal predictor setup
    # Since we need to test predictor offline, let's verify predictor initializes
    # and returns prediction values successfully.
    predictor = RiskPredictor()
    
    # Extract features for a test profile
    metrics = {
        "total_income": 8000.0,
        "total_debt": 0.0,
        "dti_ratio": 0.0,
        "expense_to_income_ratio": 30.0,
        "savings_rate": 70.0,
        "disposable_income": 5600.0
    }
    
    features = extract_features(metrics, [])
    prediction = predictor.predict_risk(features)
    
    assert "risk_level" in prediction
    assert "probabilities" in prediction
    assert prediction["risk_level"] in ["Low Risk", "Moderate Risk", "High Risk", "Critical Risk"]
    assert len(prediction["probabilities"]) == 4
