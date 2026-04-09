from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from app.core.config import secret_key, algo, access_token_expire_minutes

# --- bcrypt : algo d'hashage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Register - HACHER password : '1234' --> ''$a#v@'
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- Login - VÉRIFIER password : 123456 --> $2b$12 => (vs) [stocké]
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# --- GÉNÉRER LE TOKEN : badge numérique
def create_access_token(data: dict):
    to_encode = data.copy()

    # definir la date d'exp : now + 30 min
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_expire_minutes)            
    to_encode.update({"exp": expire})

    # signer le tout numériquement
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algo)
    return encoded_jwt
