from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os

# Internal Imports (Assuming your repo structure)
from app.db import models, database
from app.core import security
from app.api import dependencies
from app.schemas import user as user_schema
from app.schemas import prediction as pred_schema
from app.services.ml_service import ml_service
from app.services.llm_service import llm_service # Your Gemini/HF logic

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Retention AI API")

# --- 1. AUTHENTICATION ---

@app.post("/register", response_model=user_schema.UserOut)
def register(user: user_schema.UserCreate, db: Session = Depends(dependencies.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_pw = security.get_password_hash(user.password)
    new_user = models.User(username=user.username, password_hash=hashed_pw)
    db.add(new_user)
    db.commit()
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(dependencies.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = security.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- 2. MACHINE LEARNING ---

@app.post("/predict")
def predict(
    data: pred_schema.EmployeeData, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Calculate probability
    prob = ml_service.predict(data.dict())
    
    # Traceability: Store in PostgreSQL
    history = models.PredictionHistory(
        user_id=current_user.id,
        employee_id=data.EmployeeNumber, # Ensure this is in your schema
        probability=prob
    )
    db.add(history)
    db.commit()
    
    return {"churn_probability": prob}

# --- 3. GENERATIVE AI PLAN ---

@app.post("/generate-retention-plan")
async def generate_retention_plan(
    data: pred_schema.EmployeeData,
    current_user: models.User = Depends(dependencies.get_current_user)
):
    # Logic: First, check the probability
    prob = ml_service.predict(data.dict())
    
    if prob < 0.50:
        return {
            "churn_probability": prob,
            "status": "Safe",
            "retention_plan": "No plan required. Employee risk is low."
        }

    # Logic: Dynamic Prompt for high-risk employees
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
    
    # Call GenAI Service
    plan = await llm_service.generate_text(prompt)
    
    return {
        "churn_probability": prob,
        "retention_plan": plan
    }