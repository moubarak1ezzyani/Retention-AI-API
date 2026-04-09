from pathlib import Path

# --- CONFIGURATION ---
DATA_PATH = "../../data/df_RetentionAI.csv"
MODEL_DIR = Path("../../models/smote")

from pathlib import Path

# Paths to artifacts saved by your train.py script
MODEL_PATH = Path("../../models/smote/RandomForest_SMOTE_optimized_script.pkl")
SCALER_PATH = Path("../../models/encode_scale/standard_scaler.pkl")
OE_PATH = Path("../../models/encode_scale/ordinal_encoder.pkl")
OHE_PATH = Path("../../models/encode_scale/ohe_encoder.pkl")
