import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Database configurations
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/debt_relief.db")

# Gemini API Configurations
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory paths
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
ML_MODEL_DIR = DATA_DIR / "models"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
ML_MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Application settings
APP_TITLE = "AI Powered Debt Relief & Financial Recovery Platform"
APP_ICON = "💰"
