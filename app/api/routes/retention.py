# (Generative AI Endpoints: /generate-retention-plan)from fastapi import APIRouter, Depends
from app.db import models
from app.api import dependencies
from app.db.schemas import prediction as pred_schema
from app.services.ml_service import ml_service
from app.services.llm_service import llm_service
from fastapi import APIRouter, Depends

router = APIRouter()

@router.post("/generate-retention-plan")
async def generate_retention_plan(
    data: pred_schema.EmployeeData,
    current_user: models.UserDB = Depends(dependencies.get_current_user)
):
    prob = ml_service.predict(data.dict())
    
    if prob < 0.50:
        return {
            "churn_probability": prob,
            "status": "Safe",
            "retention_plan": "No plan required. Employee risk is low."
        }

    prompt = f"""
    Agis comme un expert RH. Voici les informations sur l’employé :
    - Age : {data.Age}
    - Département : {data.Department}
    - Rôle : {data.JobRole}
    - Satisfaction : {data.JobSatisfaction}/4
    - Équilibre vie pro : {data.WorkLifeBalance}/4
    
    Contexte : ce salarié a un risque de {prob*100}% de départ.
    Tâche : propose 3 actions concrètes et opérationnelles pour le retenir.
    """
    
    plan = await llm_service.generate_text(prompt)
    
    return {
        "churn_probability": prob,
        "retention_plan": plan
    }