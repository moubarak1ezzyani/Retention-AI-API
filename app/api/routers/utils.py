from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models import UserDB
from app.db.crud import get_prediction_history
from app.api.dependencies import get_db, get_current_user
from app.services.ml_service import get_model_name

router = APIRouter(tags=["Utility"])

@router.get("/health", summary="Health check")
def health():
    return {"status": "ok", "model": get_model_name()}

@router.get("/history", summary="Fetch prediction history for the authenticated user")
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    rows = get_prediction_history(db, current_user.id, limit)
    return [
        {
            "id": r.id,
            "timestamp": r.timestamp,
            "employee_id": r.employee_id,
            "department": r.department,    
            "role": r.role,                
            "probability": round(r.probability, 4),
            "risk_level": "High" if r.probability > 0.66 else "Medium" if r.probability > 0.33 else "Low",
        }
        for r in rows
    ]