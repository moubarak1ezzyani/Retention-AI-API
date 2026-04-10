import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- JWT & Security ---
SECRET_KEY = os.getenv("SECRET_KEY", "secret-key-content")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# --- Database ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/retention_ai")

# --- External APIs ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SMOTE_DIR = BASE_DIR / "models" / "smote"
PREPROCESS_DIR = BASE_DIR / "models" / "encode_scale"

# --- ML Feature Groups ---
NUM_COLS = [
    "Age", "DailyRate", "DistanceFromHome", "HourlyRate", "MonthlyIncome",
    "MonthlyRate", "NumCompaniesWorked", "PercentSalaryHike",
    "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany",
    "YearsInCurrentRole", "YearsSinceLastPromotion", "YearsWithCurrManager",
]
CAT_ORDINAL = ["BusinessTravel", "OverTime", "Gender"]
CAT_NOMINAL = ["Department", "EducationField", "JobRole", "MaritalStatus"]
ORDINAL_RANKS = [
    "Education", "EnvironmentSatisfaction", "JobInvolvement",
    "JobSatisfaction", "PerformanceRating", "RelationshipSatisfaction",
    "StockOptionLevel", "WorkLifeBalance",
]