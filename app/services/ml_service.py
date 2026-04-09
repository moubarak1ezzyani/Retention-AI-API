import pandas as pd
import numpy as np
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE

# --- 1. CONFIGURATION & ABSOLUTE PATHS ---
# ml_process.py is in app/services/ -> .parent.parent.parent gets us to Retention-AI-API/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Input Data
DATA_PATH = BASE_DIR / "data" / "df_RetentionAI.csv"

# Output Model Folders
MODELS_ROOT = BASE_DIR / "models"
BASELINE_DIR = MODELS_ROOT / "baseline"
SMOTE_DIR = MODELS_ROOT / "smote"
PREPROCESS_DIR = MODELS_ROOT / "encode_scale"

# Automatically create all required directories
for folder in [BASELINE_DIR, SMOTE_DIR, PREPROCESS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Feature Configuration
COLS_TO_DROP = ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber', 'JobLevel']
CAT_ORDINAL = ["BusinessTravel", "OverTime", "Gender"]
CAT_NOMINAL = ["Department", "EducationField", "JobRole", "MaritalStatus"]

# REMOVED 'JobLevel' FROM THIS LIST BECAUSE IT WAS DROPPED ABOVE
ORDINAL_RANKS = [
    'Education', 'EnvironmentSatisfaction', 'JobInvolvement', 
    'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction', 
    'StockOptionLevel', 'WorkLifeBalance'
]
def run_ml_pipeline():
    print(f"--- 🚀 Starting ML Pipeline ---")
    print(f"Project Root: {BASE_DIR}")

    # --- 2. LOAD DATA ---
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    # --- 3. CLEANING & TARGET ENCODING ---
    df_clean = df.drop(columns=[c for c in COLS_TO_DROP if c in df.columns])
    df_clean['Attrition'] = df_clean['Attrition'].map({'Yes': 1, 'No': 0})
    
    # --- 4. DATA SPLITTING ---
    X = df_clean.drop('Attrition', axis=1)
    y = df_clean['Attrition'].astype(int)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=45, stratify=y
    )

    # --- 5. PREPROCESSING (Fit on Train, Transform Test) ---
    num_cols = X_train_raw.select_dtypes(include=[np.number]).columns.tolist()
    num_cols = [c for c in num_cols if c not in ORDINAL_RANKS]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_raw[num_cols])
    X_test_scaled = scaler.transform(X_test_raw[num_cols])

    oe = OrdinalEncoder()
    X_train_oe = oe.fit_transform(X_train_raw[CAT_ORDINAL])
    X_test_oe = oe.transform(X_test_raw[CAT_ORDINAL])

    ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_train_ohe = ohe.fit_transform(X_train_raw[CAT_NOMINAL])
    X_test_ohe = ohe.transform(X_test_raw[CAT_NOMINAL])

    def rebuild(scaled, ord_enc, nom_enc, original_raw):
        d1 = pd.DataFrame(scaled, columns=num_cols, index=original_raw.index)
        d2 = pd.DataFrame(ord_enc, columns=CAT_ORDINAL, index=original_raw.index)
        d3 = pd.DataFrame(nom_enc, columns=ohe.get_feature_names_out(), index=original_raw.index)
        d4 = original_raw[ORDINAL_RANKS].reset_index(drop=True)
        return pd.concat([d1.reset_index(drop=True), d2.reset_index(drop=True), 
                          d3.reset_index(drop=True), d4], axis=1)

    X_train = rebuild(X_train_scaled, X_train_oe, X_train_ohe, X_train_raw)
    X_test = rebuild(X_test_scaled, X_test_oe, X_test_ohe, X_test_raw)

    # SAVE TO: encode_scale/
    joblib.dump(scaler, PREPROCESS_DIR / 'scaler.pkl')
    joblib.dump(oe, PREPROCESS_DIR / 'ordinal_encoder.pkl')
    joblib.dump(ohe, PREPROCESS_DIR / 'ohe_encoder.pkl')
    print(f"✅ Encoders saved to: {PREPROCESS_DIR}")

    # --- 6. BASELINE TRAINING ---
    print("--- 📉 Training Baseline Models ---")
    lr_baseline = LogisticRegression(random_state=45, max_iter=1000).fit(X_train, y_train)
    rf_baseline = RandomForestClassifier(random_state=45).fit(X_train, y_train)

    # SAVE TO: baseline/
    joblib.dump(lr_baseline, BASELINE_DIR / 'LogisticRegression_optimized_model.pkl')
    joblib.dump(rf_baseline, BASELINE_DIR / 'RandomForest_optimized_model.pkl')

    # --- 7. SMOTE TRAINING & OPTIMIZATION ---
    print("--- ⚖️ Training SMOTE Models ---")
    smote = SMOTE(random_state=45)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    # RF SMOTE Optimization
    rf_params = {'n_estimators': [100, 200], 'max_depth': [None, 10]}
    rf_grid = GridSearchCV(RandomForestClassifier(random_state=45), rf_params, cv=3, scoring='f1')
    rf_grid.fit(X_train_res, y_train_res)
    
    # LR SMOTE Optimization
    lr_params = {'C': [0.1, 1.0, 10.0]}
    lr_grid = GridSearchCV(LogisticRegression(random_state=45, max_iter=1000), lr_params, cv=3, scoring='f1')
    lr_grid.fit(X_train_res, y_train_res)

    # SAVE TO: smote/
    joblib.dump(lr_grid.best_estimator_, SMOTE_DIR / 'LogisticRegression_SMOTE_optimized.pkl')
    joblib.dump(rf_grid.best_estimator_, SMOTE_DIR / 'RandomForest_SMOTE_optimized.pkl')
    
    print(f"✅ Baseline models saved to: {BASELINE_DIR}")
    print(f"✅ SMOTE models saved to: {SMOTE_DIR}")
    print("\n--- Pipeline Complete! ---")

if __name__ == "__main__":
    run_ml_pipeline()