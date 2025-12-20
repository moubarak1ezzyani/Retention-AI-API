from sqlalchemy.orm import Session
import models, schemas, security

# --- retenir l'utilsateur
def get_user_by_username(db: Session, username: str):
    # SQL: SELECT * FROM users WHERE email = email LIMIT 1
    return db.query(models.UserDB).filter(models.UserDB.username == username).first()     # verifier si l'email existe : login & register

# --- Créer l'utilisateur
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)     
    
    # --- On prépare l'objet DB
    db_user = models.UserDB(username=user.username, password_hash=hashed_password)
    
    # --- On l'ajoute et on valide
    db.add(db_user)
    db.commit()
    db.refresh(db_user)     # Récupère l'ID généré et le created_at
    return db_user