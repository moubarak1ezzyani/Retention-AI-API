from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import UserDB
from app.db.schemas import EmployeeFeatures, PredictResponse
from app.db.crud import create_prediction_record
from app.api.dependencies import get_db, get_current_user
from app.services.ml_service import predict_churn


router = APIRouter(tags=["Prediction & AI"])

@router.post("/predict", response_model=PredictResponse, summary="Predict employee churn probability")
def predict(
    employee: EmployeeFeatures,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    try:
        features_dict = employee.model_dump(exclude={"employee_id"})
        proba = predict_churn(features_dict)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Preprocessing / inference error: {exc}",
        )

    create_prediction_record(db, current_user.id, employee.employee_id, proba)

    risk = "High" if proba > 0.66 else "Medium" if proba > 0.33 else "Low"
    return PredictResponse(
        employee_id=employee.employee_id,
        churn_probability=round(proba, 4),
        risk_level=risk,
    )

