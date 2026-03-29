from sqlalchemy.orm import Session
import models, schemas, security

# --- retenir l'utilsateur
def get_user_by_username(db: Session, username: str):
    # SQL: SELECT * FROM users WHERE usernme = username LIMIT 1
    return db.query(models.UserDB).filter(models.UserDB.username == username).first()     # user exists? login & register

# --- Créer l'utilisateur
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)     
    
    # --- On prépare l'objet DB
    db_user = models.UserDB(username=user.username, password_hash=hashed_password)
    
    # --- db_user : add & validate
    db.add(db_user)
    db.commit()
    db.refresh(db_user)     # get :  ID generated & created_at
    return db_user

def create_prediction_history(db: Session, user_id: int, probability: float, prediction: int, emp_id: str):
    db_prediction = models.prediction_history(
        user_id=user_id,
        employee_number=emp_id, 
        prediction=prediction,
        probability=probability
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction