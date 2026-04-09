from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
# --- CONFIGURATION ---
MODEL_PATH = Path("../../models/smote/RandomForest_SMOTE_optimized_script.pkl")
SCALER_PATH = Path("../../models/encode_scale/standard_scaler.pkl")
OE_PATH = Path("../../models/encode_scale/ordinal_encoder.pkl")
OHE_PATH = Path("../../models/encode_scale/ohe_encoder.pkl")

# Security
secret_key = os.getenv("secret_key_env")
algo = os.getenv("algo_env")
access_token_expire_minutes = int(os.getenv("access_token_expire_minutes_env", "30"))