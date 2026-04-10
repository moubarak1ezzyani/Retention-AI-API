import json
from huggingface_hub import InferenceClient
from app.core.config import HF_TOKEN

# Initialize the Hugging Face Client
if HF_TOKEN:
    client = InferenceClient(api_key=HF_TOKEN)
    # Using Llama-3-8B as it is highly capable and supported on the free Inference API
    MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
else:
    client = None

def build_retention_prompt(employee: dict, probability: float) -> str:
    return f"""
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

Contexte : ce salarié présente un risque élevé de départ (churn_probability = {probability:.0%}) selon notre modèle prédictif.

Tâche : propose EXACTEMENT 3 actions concrètes, personnalisées et opérationnelles pour retenir cet employé. Tiens compte de son rôle, sa satisfaction, sa performance et son équilibre vie professionnelle/personnelle. Rédige chaque action de façon claire en une seule phrase.

Réponds UNIQUEMENT sous ce format JSON (ne génère aucun autre texte) :
{{
  "retention_plan": [
    "Action 1",
    "Action 2",
    "Action 3"
  ]
}}
""".strip()

def generate_plan(employee_dict: dict, probability: float) -> list[str]:
    if client is None:
        raise ValueError("HF_TOKEN is not configured in .env")
        
    prompt = build_retention_prompt(employee_dict, probability)
    
    # Format messages for the chat completions API
    messages = [
        {"role": "system", "content": "Tu es un expert RH senior. Tu dois répondre uniquement avec un objet JSON valide."},
        {"role": "user", "content": prompt}
    ]
    
    # Call Hugging Face Inference API with JSON format enforcement
    response = client.chat_completion(
        model=MODEL_ID,
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=400,
        temperature=0.7
    )
    
    raw_text = response.choices[0].message.content.strip()
    
    try:
        parsed = json.loads(raw_text)
        plan = parsed.get("retention_plan", [])
        
        if not plan or not isinstance(plan, list):
            raise ValueError("retention_plan key missing or empty.")
            
        return plan
        
    except json.JSONDecodeError:
        raise ValueError(f"Model did not return valid JSON. Raw output: {raw_text}")