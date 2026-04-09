# =============================================================================
#  Retention AI — main.py
#  FastAPI · JWT Auth · PostgreSQL · ML Prediction · Gemini Retention Plans
# =============================================================================

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
# --- FastAPI & HTTP ---
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# --- Pydantic (v2) ---
from pydantic import BaseModel

# --- Security ---
from passlib.context import CryptContext
from jose import JWTError, jwt

# --- Database ---
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, ForeignKey, text
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Generative AI (Google Gemini) ---
import google.generativeai as genai


# =============================================================================
#  CONFIGURATION
# =============================================================================
load_dotenv()
# JWT
SECRET_KEY       = os.getenv("SECRET_KEY", "change-me-in-production-use-a-long-random-string")
ALGORITHM        = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# PostgreSQL  — override DATABASE_URL in your .env
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/retention_ai"
)

# Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Paths (main.py lives in app/, so we need .parent.parent to reach the root)
BASE_DIR       = Path(__file__).resolve().parent.parent
SMOTE_DIR      = BASE_DIR / "models" / "smote"
PREPROCESS_DIR = BASE_DIR / "models" / "encode_scale"

# Feature groups — must match ml_process.py exactly
NUM_COLS = [
    "Age", "DailyRate", "DistanceFromHome", "HourlyRate", "MonthlyIncome",
    "MonthlyRate", "NumCompaniesWorked", "PercentSalaryHike",
    "TotalWorkingYears", "TrainingTimesLastYear", "YearsAtCompany",
    "YearsInCurrentRole", "YearsSinceLastPromotion", "YearsWithCurrManager",
]
CAT_ORDINAL  = ["BusinessTravel", "OverTime", "Gender"]
CAT_NOMINAL  = ["Department", "EducationField", "JobRole", "MaritalStatus"]
ORDINAL_RANKS = [
    "Education", "EnvironmentSatisfaction", "JobInvolvement",
    "JobSatisfaction", "PerformanceRating", "RelationshipSatisfaction",
    "StockOptionLevel", "WorkLifeBalance",
]


# =============================================================================
#  DATABASE SETUP  (SQLAlchemy)
# =============================================================================

engine       = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base         = declarative_base()


class UserDB(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PredictionHistoryDB(Base):
    __tablename__ = "predictions_history"

    id          = Column(Integer, primary_key=True, index=True)
    timestamp   = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(String, nullable=True)
    probability = Column(Float, nullable=False)


# Create tables at startup (safe to run repeatedly)
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
#  SECURITY  (bcrypt + JWT)
# =============================================================================

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire  = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# =============================================================================
#  ML ARTIFACTS  (loaded once at startup)
# =============================================================================

def _load_artifact(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found at {path}. "
            "Run ml_process.py first to generate model artifacts."
        )
    return joblib.load(path)


# Preprocessors
scaler          = _load_artifact(PREPROCESS_DIR / "scaler.pkl",           "StandardScaler")
ordinal_encoder = _load_artifact(PREPROCESS_DIR / "ordinal_encoder.pkl",  "OrdinalEncoder")
ohe_encoder     = _load_artifact(PREPROCESS_DIR / "ohe_encoder.pkl",      "OneHotEncoder")

# Model  — prefer SMOTE-optimised Random Forest; fall back to LR
_rf_path = SMOTE_DIR / "RandomForest_SMOTE_optimized.pkl"
_lr_path = SMOTE_DIR / "LogisticRegression_SMOTE_optimized.pkl"
model = _load_artifact(_rf_path if _rf_path.exists() else _lr_path, "ML model")


def preprocess(employee: dict) -> pd.DataFrame:
    """
    Replicates the exact feature pipeline from ml_process.py:
      1. Scale continuous columns
      2. Ordinal-encode relational categoricals (BusinessTravel, OverTime, Gender)
      3. One-hot-encode nominal categoricals (Department, EducationField, JobRole, MaritalStatus)
      4. Pass ordinal rank columns through unchanged
    Returns a single-row DataFrame ready for model.predict_proba().
    """
    raw = pd.DataFrame([employee])

    # 1 — Scale
    scaled = scaler.transform(raw[NUM_COLS])
    df_scaled = pd.DataFrame(scaled, columns=NUM_COLS)

    # 2 — Ordinal encode
    oe_arr = ordinal_encoder.transform(raw[CAT_ORDINAL])
    df_oe  = pd.DataFrame(oe_arr, columns=CAT_ORDINAL)

    # 3 — One-hot encode
    ohe_arr = ohe_encoder.transform(raw[CAT_NOMINAL])
    df_ohe  = pd.DataFrame(ohe_arr, columns=ohe_encoder.get_feature_names_out())

    # 4 — Ordinal ranks (pass-through)
    df_ranks = raw[ORDINAL_RANKS].reset_index(drop=True)

    return pd.concat([df_scaled, df_oe, df_ohe, df_ranks], axis=1)


# =============================================================================
#  GENERATIVE AI  (Google Gemini)
# =============================================================================

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None


def build_retention_prompt(employee: dict, probability: float) -> str:
    return f"""
Agis comme un expert RH senior.

Voici les informations sur l'employé :
- Âge                        : {employee.get('Age')}
- Département                : {employee.get('Department')}
- Rôle                       : {employee.get('JobRole')}
- Niveau d'éducation         : {employee.get('Education')}
- Satisfaction au travail    : {employee.get('JobSatisfaction')} / 4
- Satisfaction environnement : {employee.get('EnvironmentSatisfaction')} / 4
- Équilibre vie pro/perso    : {employee.get('WorkLifeBalance')} / 4
- Performance                : {employee.get('PerformanceRating')} / 4
- Implication au travail     : {employee.get('JobInvolvement')} / 4
- Heures supplémentaires     : {employee.get('OverTime')}
- Voyages professionnels     : {employee.get('BusinessTravel')}
- Années dans l'entreprise   : {employee.get('YearsAtCompany')}
- Revenu mensuel             : {employee.get('MonthlyIncome')} $
- Option d'achat d'actions   : {employee.get('StockOptionLevel')} / 3

Contexte : ce salarié présente un risque élevé de départ (churn_probability = {probability:.0%}) \
selon notre modèle prédictif de rétention.

Tâche : propose EXACTEMENT 3 actions concrètes, personnalisées et opérationnelles pour retenir \
cet employé. Tiens compte de son rôle, sa satisfaction, sa performance et son équilibre \
vie professionnelle/personnelle. Rédige chaque action de façon claire pour un manager RH, \
en une seule phrase percutante.

Réponds UNIQUEMENT sous ce format JSON (sans markdown, sans texte autour) :
{{
  "retention_plan": [
    "Action 1",
    "Action 2",
    "Action 3"
  ]
}}
""".strip()


# =============================================================================
#  PYDANTIC SCHEMAS
# =============================================================================

class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class EmployeeFeatures(BaseModel):
    # Continuous
    Age: float
    DailyRate: float
    DistanceFromHome: float
    HourlyRate: float
    MonthlyIncome: float
    MonthlyRate: float
    NumCompaniesWorked: float
    PercentSalaryHike: float
    TotalWorkingYears: float
    TrainingTimesLastYear: float
    YearsAtCompany: float
    YearsInCurrentRole: float
    YearsSinceLastPromotion: float
    YearsWithCurrManager: float
    # Categorical — ordinal (relational)
    BusinessTravel: str           # "Non-Travel" | "Travel_Rarely" | "Travel_Frequently"
    OverTime: str                 # "Yes" | "No"
    Gender: str                   # "Male" | "Female"
    # Categorical — nominal (OHE)
    Department: str               # "Sales" | "Research & Development" | "Human Resources"
    EducationField: str           # "Life Sciences" | "Medical" | ...
    JobRole: str                  # "Sales Executive" | "Research Scientist" | ...
    MaritalStatus: str            # "Single" | "Married" | "Divorced"
    # Pre-encoded ordinal ranks (pass-through)
    Education: int                # 1–5
    EnvironmentSatisfaction: int  # 1–4
    JobInvolvement: int           # 1–4
    JobSatisfaction: int          # 1–4
    PerformanceRating: int        # 3–4
    RelationshipSatisfaction: int # 1–4
    StockOptionLevel: int         # 0–3
    WorkLifeBalance: int          # 1–4
    # Optional identifier
    employee_id: Optional[str] = None


class PredictResponse(BaseModel):
    employee_id: Optional[str]
    churn_probability: float
    risk_level: str               # "Low" | "Medium" | "High"


class RetentionPlanRequest(EmployeeFeatures):
    pass


class RetentionPlanResponse(BaseModel):
    churn_probability: float
    retention_plan: list[str]


# =============================================================================
#  FASTAPI APP
# =============================================================================

app = FastAPI(
    title="Retention AI API",
    description=(
        "Predict employee attrition risk and generate personalised "
        "HR retention plans powered by ML + Gemini."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
#  AUTH ENDPOINTS
# ---------------------------------------------------------------------------

@app.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new HR user",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(UserDB).filter(UserDB.username == body.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{body.username}' is already taken.",
        )
    user = UserDB(
        username=body.username,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": f"User '{user.username}' registered successfully.", "id": user.id}


@app.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token)


# ---------------------------------------------------------------------------
#  ML PREDICTION ENDPOINT  (protected)
# ---------------------------------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictResponse,
    summary="Predict employee churn probability",
)
def predict(
    employee: EmployeeFeatures,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    try:
        features_dict = employee.model_dump(exclude={"employee_id"})
        X = preprocess(features_dict)
        proba = float(model.predict_proba(X)[0][1])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Preprocessing / inference error: {exc}",
        )

    # Persist to history
    record = PredictionHistoryDB(
        user_id=current_user.id,
        employee_id=employee.employee_id,
        probability=proba,
    )
    db.add(record)
    db.commit()

    risk = "High" if proba > 0.66 else "Medium" if proba > 0.33 else "Low"
    return PredictResponse(
        employee_id=employee.employee_id,
        churn_probability=round(proba, 4),
        risk_level=risk,
    )


# ---------------------------------------------------------------------------
#  GENERATIVE AI  — RETENTION PLAN ENDPOINT  (protected)
# ---------------------------------------------------------------------------

@app.post(
    "/generate-retention-plan",
    response_model=RetentionPlanResponse,
    summary="Generate a personalised HR retention plan (Gemini)",
)
def generate_retention_plan(
    employee: RetentionPlanRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    # 1 — Get churn probability first
    try:
        features_dict = employee.model_dump(exclude={"employee_id"})
        X    = preprocess(features_dict)
        proba = float(model.predict_proba(X)[0][1])
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Preprocessing / inference error: {exc}",
        )

    # 2 — Only generate a plan when risk is meaningful (> 50 %)
    if proba <= 0.50:
        return RetentionPlanResponse(
            churn_probability=round(proba, 4),
            retention_plan=[
                "Churn probability is below 50% — no urgent retention action required.",
                "Continue regular 1-on-1 check-ins to maintain engagement.",
                "Monitor key satisfaction metrics at next quarterly review.",
            ],
        )

    # 3 — Generate with Gemini
    if gemini_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GEMINI_API_KEY is not configured. Set the environment variable to enable AI plans.",
        )

    prompt = build_retention_prompt(employee.model_dump(), proba)
    try:
        response   = gemini_model.generate_content(prompt)
        raw_text   = response.text.strip()

        # Safely parse the JSON the model returns
        import json, re
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("Gemini did not return a valid JSON block.")
        parsed       = json.loads(json_match.group())
        plan: list   = parsed.get("retention_plan", [])
        if not plan or not isinstance(plan, list):
            raise ValueError("retention_plan key missing or empty.")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation error: {exc}",
        )

    # 4 — Persist prediction to history
    record = PredictionHistoryDB(
        user_id=current_user.id,
        employee_id=employee.employee_id,
        probability=proba,
    )
    db.add(record)
    db.commit()

    return RetentionPlanResponse(
        churn_probability=round(proba, 4),
        retention_plan=plan,
    )


# ---------------------------------------------------------------------------
#  UTILITY ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "model": type(model).__name__}


@app.get(
    "/history",
    summary="Fetch prediction history for the authenticated user",
)
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    rows = (
        db.query(PredictionHistoryDB)
        .filter(PredictionHistoryDB.user_id == current_user.id)
        .order_by(PredictionHistoryDB.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id":          r.id,
            "timestamp":   r.timestamp,
            "employee_id": r.employee_id,
            "probability": round(r.probability, 4),
            "risk_level":  "High" if r.probability > 0.66 else "Medium" if r.probability > 0.33 else "Low",
        }
        for r in rows
    ]


# =============================================================================
#  ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)