from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import UserDB
from app.db.schemas import RetentionPlanRequest, RetentionPlanResponse
from app.db.crud import create_prediction_record
from app.api.dependencies import get_db, get_current_user
from app.services.ml_service import predict_churn
from app.services.llm_service import generate_plan

router = APIRouter()  

@router.post("/generate-retention-plan", response_model=RetentionPlanResponse, summary="Generate an AI retention plan")
def generate_retention_plan(
    employee: RetentionPlanRequest,
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

    if proba <= 0.50:
        return RetentionPlanResponse(
            churn_probability=round(proba, 4),
            retention_plan=[
                "Churn probability is below 50% — no urgent retention action required.",
                "Continue regular 1-on-1 check-ins to maintain engagement.",
                "Monitor key satisfaction metrics at next quarterly review.",
            ],
        )

    try:
        plan = generate_plan(features_dict, proba)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini generation error: {exc}",
        )

    create_prediction_record(db, current_user.id, employee.employee_id, proba)

    return RetentionPlanResponse(
        churn_probability=round(proba, 4),
        retention_plan=plan,
    )