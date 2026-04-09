# (Machine Learning Endpoints: /predict — Imports configurations from ML script)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sys
from pathlib import Path

from app.db import models
from app.api import dependencies
from app.db.schemas import prediction as pred_schema
from app.services.ml_service import ml_service

# Import configurations directly from your ML pipeline script
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent))
from app.services.ml_process import COLS_TO_DROP, CAT_ORDINAL, CAT_NOMINAL, ORDINAL_RANKS

router = APIRouter()

@router.post("/predict")
def predict(
    data: pred_schema.EmployeeData, 
    db: Session = Depends(dependencies.get_db),
    current_user: models.UserDB = Depends(dependencies.get_current_user)
):
    # Pass the data to the ML service
    # (The ml_service will use COLS_TO_DROP, etc. to format the data)
    prob = ml_service.predict(data.dict())
    
    # Traceability: Store in PostgreSQL
    history = models.prediction_history(
        user_id=current_user.id,
        employee_id=data.EmployeeNumber,
        probability=prob
    )
    db.add(history)
    db.commit()
    
    return {"churn_probability": prob}