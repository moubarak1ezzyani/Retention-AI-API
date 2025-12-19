from sqlalchemy.orm import Session
from . import models, schemas, security

# --- retenir l'utilsateur
def get_user_by_email(db: Session, email: str):
    # SQL: SELECT * FROM users WHERE email = email LIMIT 1
    return db.query(models.User).filter(models.User.email == email).first()     # on verifie si l'email existe : login & register

# --- Créer l'utilisateur
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)     
    
    # --- On prépare l'objet DB
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    
    # --- On l'ajoute et on valide
    db.add(db_user)
    db.commit()
    db.refresh(db_user)     # Récupère l'ID généré et le created_at
    return db_user