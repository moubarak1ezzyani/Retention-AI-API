from sqlalchemy.orm import Session
from app.db.models import UserDB, PredictionHistoryDB

def get_user_by_username(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def create_user(db: Session, user: UserDB):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_prediction_record(db: Session, user_id: int, employee_id: str, probability: float):
    record = PredictionHistoryDB(
        user_id=user_id,
        employee_id=employee_id,
        probability=probability,
    )
    db.add(record)
    db.commit()
    return record

def get_prediction_history(db: Session, user_id: int, limit: int = 50):
    return (
        db.query(PredictionHistoryDB)
        .filter(PredictionHistoryDB.user_id == user_id)
        .order_by(PredictionHistoryDB.timestamp.desc())
        .limit(limit)
        .all()
    )