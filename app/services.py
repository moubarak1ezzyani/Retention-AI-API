import os
import joblib
import pandas as pd
import google.generativeai as genai
from .schemas import EmployeeInput 
from dotenv import load_dotenv 

load_dotenv()

# --- GEMINI SETUP ---
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    llm_model = None
    print("⚠️ ATTENTION: Pas de clé API Gemini trouvée.")

# --- ML MODEL SETUP ---
MODEL_PATH = "model.pkl" 
pipeline = None

try:
    # On essaye de charger le modèle
    if os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH)
        print("✅ Modèle ML chargé avec succès.")
    else:
        print(f"⚠️ Fichier {MODEL_PATH} introuvable. Mode Mock activé.")
except Exception as e:
    print(f"❌ Erreur chargement modèle : {e}")

# --- FONCTION GEMINI (Version Brute demandée) ---
def generate_retention_plan(employee: EmployeeInput, churn_probability: float) -> str:
    if not llm_model:
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
        response = llm_model.generate_content(prompt)
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