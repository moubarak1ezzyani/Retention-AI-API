import joblib
import pandas as pd
from pathlib import Path
from app.core.config import (
    SMOTE_DIR, PREPROCESS_DIR, NUM_COLS, 
    CAT_ORDINAL, CAT_NOMINAL, ORDINAL_RANKS
)

def _load_artifact(path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(
            f"{label} not found at {path}. Run your training notebook/script first to generate model artifacts."
        )
    return joblib.load(path)

# Load Encoders
scaler = _load_artifact(PREPROCESS_DIR / "scaler.pkl", "StandardScaler")
ordinal_encoder = _load_artifact(PREPROCESS_DIR / "ordinal_encoder.pkl", "OrdinalEncoder")
ohe_encoder = _load_artifact(PREPROCESS_DIR / "ohe_encoder.pkl", "OneHotEncoder")

# Load Model (Prefers the SMOTE-optimized Random Forest)
_rf_path = SMOTE_DIR / "RandomForest_SMOTE_optimized.pkl"
_lr_path = SMOTE_DIR / "LogisticRegression_SMOTE_optimized.pkl"
model = _load_artifact(_rf_path if _rf_path.exists() else _lr_path, "ML model")

def preprocess(employee: dict) -> pd.DataFrame:
    """Transforms a single employee JSON payload into the format the model expects."""
    raw = pd.DataFrame([employee])

    scaled = scaler.transform(raw[NUM_COLS])
    df_scaled = pd.DataFrame(scaled, columns=NUM_COLS)

    oe_arr = ordinal_encoder.transform(raw[CAT_ORDINAL])
    df_oe = pd.DataFrame(oe_arr, columns=CAT_ORDINAL)

    ohe_arr = ohe_encoder.transform(raw[CAT_NOMINAL])
    df_ohe = pd.DataFrame(ohe_arr, columns=ohe_encoder.get_feature_names_out())

    df_ranks = raw[ORDINAL_RANKS].reset_index(drop=True)

    return pd.concat([df_scaled, df_oe, df_ohe, df_ranks], axis=1)

def predict_churn(employee_dict: dict) -> float:
    """Predicts the probability of an employee churning."""
    X = preprocess(employee_dict)
    return float(model.predict_proba(X)[0][1])

def get_model_name() -> str:
    """Returns the name of the active model for health checks."""
    return type(model).__name__