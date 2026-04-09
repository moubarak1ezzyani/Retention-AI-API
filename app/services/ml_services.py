import joblib
import pandas as pd
import numpy as np

class MLService:
    def __init__(self):
        # Load artifacts on startup
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.oe = joblib.load(OE_PATH)
        self.ohe = joblib.load(OHE_PATH)
        
        # Define the exact column order required by the model
        # (This must match the order in your train.py rebuilding step)
        self.cat_ord = ["BusinessTravel", "OverTime", "Gender"]
        self.cat_ohe = ["Department", "EducationField", "JobRole", "MaritalStatus"]
        self.ordinal_ranks = ['Education', 'EnvironmentSatisfaction', 'JobInvolvement', 
                              'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction', 
                              'StockOptionLevel', 'WorkLifeBalance']

    def preprocess(self, raw_data: dict):
        """Transforms a single employee record into a model-ready feature vector."""
        df = pd.DataFrame([raw_data])

        # 1. Scale Numerical
        # List must match the list used in train.py num_cols
        num_cols = self.scaler.feature_names_in_
        scaled_data = self.scaler.transform(df[num_cols])
        df_num = pd.DataFrame(scaled_data, columns=num_cols)

        # 2. Ordinal Encode
        ord_data = self.oe.transform(df[self.cat_ord])
        df_ord = pd.DataFrame(ord_data, columns=self.cat_ord)

        # 3. One-Hot Encode
        ohe_data = self.ohe.transform(df[self.cat_ohe])
        df_ohe = pd.DataFrame(ohe_data, columns=self.ohe.get_feature_names_out())

        # 4. Combine in exact order
        df_final = pd.concat([df_num, df_ord, df_ohe, df[self.ordinal_ranks]], axis=1)
        return df_final

    def predict_churn(self, raw_data: dict) -> float:
        """Returns the probability of attrition."""
        features = self.preprocess(raw_data)
        # model.predict_proba returns [prob_no, prob_yes]
        probability = self.model.predict_proba(features)[0][1]
        return float(round(probability, 4))

ml_service = MLService()