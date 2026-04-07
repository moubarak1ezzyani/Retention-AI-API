import os
import joblib
import pandas as pd
# import google.genai as genai
from google import genai  
from app.db.schemas import EmployeeInput 
from dotenv import load_dotenv 

# --- GEMINI SETUP 
load_dotenv()
genai_api_key = os.getenv("genai_api_key_env")
 
# --- configurer globalement => creation d'un CLIENT
client = genai.Client(api_key=genai_api_key)

# Appel à l'IA : client.models.generate_content()
def generate_analysis_with_gemini(prompt_text):
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        print(f"Erreur Gemini: {e}")
        return "Analyse indisponible."

# --- ML MODEL SETUP 
model_ml_name = ["RandomForestClassifier", "LogisticRegression"]

for m in model_ml_name:
    model_path = f"../models/{m}_model.pkl"

pipeline = None

try:
    # chargeement du modèle
    if os.path.exists(model_path):
        pipeline = joblib.load(model_path)
        print("Modèle ML chargé avec succès.")
    else:
        print(f" Fichier {model_path} introuvable. Mode Mock activé.")
except Exception as e:
    print(f"Erreur chargement modèle : {e}")

# --- fct gemini 
def generate_retention_plan(employee: EmployeeInput, churn_probability: float) -> str:
    if not genai_api_key:
        return "Erreur: Clé API Gemini non configurée."

    prompt = f"""
    Agis comme un expert RH. 
    Voici les informations sur l'employé :
    - Département : {employee.Department}
    - Age : {employee.Age}
    - Role : {employee.JobRole}
    - Satisfaction au travail : {employee.JobSatisfaction}/4
    - Heures Supplémentaires : {employee.OverTime}
    - Niveau Stock Option : {employee.StockOptionLevel}
    - Années dans l'entreprise : {employee.YearsAtCompany}

    Contexte : ce salarié a un risque élevé de {churn_probability * 100:.1f}% de départ.
    Tache : propose 3 actions concrètes pour le retenir.
    """

    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text 
    
    except Exception as e:
        return f"Erreur Gemini : {str(e)}"

# --- fct prediction 
def predict_attrition(data: EmployeeInput):

    # --- Modele ML : input pydantic --> dataframe
    df = pd.DataFrame([data.to_dict()])
    
    if pipeline:
        
        try:
            # --- pipeline : manuqe du Preprocessing => colonnes text plantent   
            probability = pipeline.predict_proba(df)[0][1]      # Proba de la classe 1 (Départ)
            prediction = 1 if probability > 0.5 else 0
            return prediction, probability
        except Exception as e:
            print(f"Erreur lors de la prédiction : {e}")
            return 0, 0.0
    else:
        # Mock - Logique bidon : tester frontend si le modèle n'est pas là
        mock_prob = 0.85 if data.OverTime == "Yes" else 0.25
        return (1 if mock_prob > 0.5 else 0), mock_prob
