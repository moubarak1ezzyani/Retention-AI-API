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
Here is the employee information:
- Age                        : {employee.get('Age')}
- Department                 : {employee.get('Department')}
- Role                       : {employee.get('JobRole')}
- Education Level            : {employee.get('Education')}
- Job Satisfaction           : {employee.get('JobSatisfaction')} / 4
- Environment Satisfaction   : {employee.get('EnvironmentSatisfaction')} / 4
- Work-Life Balance          : {employee.get('WorkLifeBalance')} / 4
- Performance Rating         : {employee.get('PerformanceRating')} / 4
- Job Involvement            : {employee.get('JobInvolvement')} / 4
- Overtime                   : {employee.get('OverTime')}
- Business Travel            : {employee.get('BusinessTravel')}
- Years at Company           : {employee.get('YearsAtCompany')}
- Monthly Income             : ${employee.get('MonthlyIncome')}
- Stock Option Level         : {employee.get('StockOptionLevel')} / 3

Context: This employee presents a high risk of departure (churn_probability = {probability:.0%}) according to our predictive model.

Task: Propose EXACTLY 3 concrete, personalized, and actionable steps to retain this employee. Take into account their role, satisfaction, performance, and work-life balance. Write each action clearly in a single sentence. 
IMPORTANT: You must write your entire response strictly in English.

Respond ONLY in this JSON format (do not generate any other text):
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
        {"role": "system", "content": "You are a senior HR expert. You must respond only with a valid JSON object in English."},
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