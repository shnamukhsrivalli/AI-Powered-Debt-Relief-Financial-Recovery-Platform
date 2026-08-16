import os
import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any
from config.settings import ML_MODEL_DIR
from ml.train import train_risk_model

MODEL_PATH = ML_MODEL_DIR / "risk_model.joblib"

class RiskPredictor:
    """
    Handles model initialization, loading, and predicting financial risk levels.
    """
    def __init__(self):
        self.model = None
        self._ensure_model_trained()
        
    def _ensure_model_trained(self):
        """Trains the model automatically if joblib file is missing."""
        if not MODEL_PATH.exists():
            print("ML Model file not found. Running training process...")
            train_risk_model()
            
    def load_model(self):
        """Loads model file from disk into memory."""
        if not self.model:
            self._ensure_model_trained()
            self.model = joblib.load(str(MODEL_PATH))
            
    def predict_risk(self, features_array: np.ndarray) -> Dict[str, Any]:
        """
        Runs model prediction on extracted features.
        Returns:
            Dict: {
                "risk_level": str,
                "probabilities": {"Low Risk": float, "Moderate Risk": float, ...}
            }
        """
        self.load_model()
        
        # Run prediction
        risk_level = self.model.predict(features_array)[0]
        
        # Run probability estimation
        prob_vals = self.model.predict_proba(features_array)[0]
        classes = self.model.classes_
        
        probabilities = {}
        for cls, prob in zip(classes, prob_vals):
            probabilities[cls] = round(float(prob) * 100, 1)
            
        return {
            "risk_level": risk_level,
            "probabilities": probabilities
        }
