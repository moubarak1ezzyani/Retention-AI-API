from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.models import UserDB
from app.db.schemas import RegisterRequest, TokenResponse
from app.db.crud import get_user_by_username, create_user
from app.api.dependencies import get_db
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new HR user")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    existing = get_user_by_username(db, body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{body.username}' is already taken.",
        )
    user = UserDB(username=body.username, password_hash=hash_password(body.password))
    user = create_user(db, user)
    return {"message": f"User '{user.username}' registered successfully.", "id": user.id}

@router.post("/login", response_model=TokenResponse, summary="Authenticate and receive a JWT")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token)