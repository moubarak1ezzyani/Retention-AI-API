import os
import joblib
import pandas as pd
# import google.genai as genai
from google import genai  
from schemas import EmployeeInput 
from dotenv import load_dotenv 

# --- GEMINI SETUP ---
load_dotenv()
genai_api_key = os.getenv("genai_api_key_env")

# On crée un CLIENT au lieu de configurer globalement
client = genai.Client(api_key=genai_api_key)

# Pour appeler l'IA, on utilise client.models.generate_content
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

# --- ML MODEL SETUP ---
model_ml_name = ["RandomForestClassifier", "LogisticRegression"]

for m in model_ml_name:
    model_path = f"../models/{m}_model.pkl"

pipeline = None

try:
    # On essaye de charger le modèle
    if os.path.exists(model_path):
        pipeline = joblib.load(model_path)
        print("✅ Modèle ML chargé avec succès.")
    else:
        print(f"⚠️ Fichier {model_path} introuvable. Mode Mock activé.")
except Exception as e:
    print(f"❌ Erreur chargement modèle : {e}")

# --- FONCTION GEMINI (Version Brute demandée) ---
def generate_retention_plan(employee: EmployeeInput, churn_probability: float) -> str:
    if not genai_api_key:
        return "Erreur: Clé API Gemini non configurée."

    prompt = f"""
    Agis comme un expert RH. 
    Voici les informations sur l'employé :
    - Age : {employee.Age}
    - Département : {employee.Department}
    - Role : {employee.JobRole}
    - Satisfaction au travail : {employee.JobSatisfaction}/4
    - Heures Supplémentaires : {employee.OverTime}
    - Niveau Stock Option : {employee.StockOptionLevel}
    - Années dans l'entreprise : {employee.YearsAtCompany}

    Contexte : ce salarié a un risque élevé de {churn_probability * 100:.1f}% de départ.
    Tache : propose 3 actions concrètes pour le retenir.
    """

    try:
        response = genai_api_key.generate_content(prompt)
        # RETOUR BRUT comme demandé
        return response.text 
    
    except Exception as e:
        return f"Erreur Gemini : {str(e)}"

# --- FONCTION PREDICTION ---
def predict_attrition(data: EmployeeInput):
    """
    Transforme l'input Pydantic en DataFrame et utilise le modèle chargé.
    """
    # Conversion en DataFrame (format attendu par Scikit-Learn)
    df = pd.DataFrame([data.to_dict()])
    
    if pipeline:
        # Prédiction réelle
        try:
            # Note: Le pipeline doit inclure le Preprocessing (OneHotEncoder) 
            # sinon ça plantera sur les colonnes texte (Department, etc.)
            probability = pipeline.predict_proba(df)[0][1] # Proba de la classe 1 (Départ)
            prediction = 1 if probability > 0.5 else 0
            return prediction, probability
        except Exception as e:
            print(f"Erreur lors de la prédiction : {e}")
            return 0, 0.0
    else:
        # Mock pour tester le frontend si le modèle n'est pas là
        # Logique bidon juste pour la démo
        mock_prob = 0.85 if data.OverTime == "Yes" else 0.25
        return (1 if mock_prob > 0.5 else 0), mock_prob
#-----------------------------------
""" import os
import google.generativeai as genai
from schemas import EmployeeInput 
from dotenv import load_dotenv 

# --- CONFIGURATION 
# -> Gemini key
load_dotenv()
genai_api_key = os.getenv("genai_api_key_env")
genai.configure(api_key=genai_api_key)

# -> Initialisation du modèle 
llm_model = genai.GenerativeModel('gemini-1.5-flash')

def generate_retention_plan(employee: EmployeeInput, churn_probability: float) -> str:
    
    # --- preparer le prompt 
    # variables Pydantic --> prompt
    prompt = f
    Agis comme un expert RH. 

    Voici les informations sur l'employé :
    - Age : {employee.Age if hasattr(employee, 'Age') else "Non spécifié"}
    - Département : {employee.Department}
    - Role : {employee.JobRole}
    - Satisfaction au travail : {employee.JobSatisfaction}/4
    - Heures Supplémentaires : {employee.OverTime}
    - Niveau Stock Option : {employee.StockOptionLevel}
    - Années dans l'entreprise : {employee.YearsAtCompany if hasattr(employee, 'YearsAtCompany') else "Non spécifié"}

    Contexte : ce salarié a un risque élevé de {churn_probability * 100:.1f}% de départ selon le modèle ML.  

    Tache : propose 3 actions concrètes et personnalisées pour le retenir dans l’entreprise, en tenant compte de son role, sa satisfaction, sa performance et son équilibre vie professionnelle/personnelle.  
    Rédige les actions de façon claire et opérationnelle pour un manager RH.


    try:
        # --- APPEL À L'API : l'envoie du prompt à Google
        response = llm_model.generate_content(prompt)
        
        # --- récupèrer le texte brut
        raw_text = response.text
        
        return raw_text
    
    except Exception as e:
        print(f"Erreur connexion Gemini : {e}")
        # msg de secours : pour eviter que l'app plante
        return "Le service d'IA est momentanément indisponible. Veuillez contacter les RH manuellement."
    
# --- ML : modele local
def predict_attrition(data):
 """