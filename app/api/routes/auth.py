from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Internal Imports
from app.db import models, database, crud
from app.core import security
from app.db.schemas import user as user_schema

router = APIRouter()

# --- DEPENDENCY ---
# We define get_db here since dependencies.py is deleted
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---

@router.post("/register", response_model=user_schema.UserOut)
def register(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user already exists using our CRUD function
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already exists"
        )
    
    # 2. Create the user using our CRUD function
    new_user = crud.create_user(db, user=user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Fetch user using our CRUD function
    user = crud.get_user_by_username(db, username=form_data.username)
    
    # 2. Verify user exists and password matches
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    
    # 3. Generate JWT Token
    token = security.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}