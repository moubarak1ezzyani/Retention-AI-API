import json
import re
from google import genai
from app.core.config import GEMINI_API_KEY

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

Contexte : ce salarié présente un risque élevé de départ (churn_probability = {probability:.0%}) selon notre modèle prédictif de rétention.

Tâche : propose EXACTEMENT 3 actions concrètes, personnalisées et opérationnelles pour retenir cet employé. Tiens compte de son rôle, sa satisfaction, sa performance et son équilibre vie professionnelle/personnelle. Rédige chaque action de façon claire pour un manager RH, en une seule phrase percutante.

Réponds UNIQUEMENT sous ce format JSON (sans markdown, sans texte autour) :
{{
  "retention_plan": [
    "Action 1",
    "Action 2",
    "Action 3"
  ]
}}
""".strip()

def generate_plan(employee_dict: dict, probability: float) -> list[str]:
    if gemini_model is None:
        raise ValueError("GEMINI_API_KEY is not configured.")
        
    prompt = build_retention_prompt(employee_dict, probability)
    response = gemini_model.generate_content(prompt)
    raw_text = response.text.strip()

    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not json_match:
        raise ValueError("Gemini did not return a valid JSON block.")
        
    parsed = json.loads(json_match.group())
    plan = parsed.get("retention_plan", [])
    if not plan or not isinstance(plan, list):
        raise ValueError("retention_plan key missing or empty.")
        
    return plan