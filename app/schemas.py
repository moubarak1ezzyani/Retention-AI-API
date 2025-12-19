from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# ==========================================
#   AUTHENTIFICATION 
# ==========================================

class UserBase(BaseModel):
    email: EmailStr  # Vérifie automatiquement le format "ahmed@gmail.com"

# --- INPUT DATA 
class UserCreate(UserBase):
    password: str

# --- OUTPUT DATA: reponse d'API  
class UserOutput(UserBase):
    id: int
    created_at: datetime
    
    # ligne MAGIQUE : SQLAlchemy db --(auto)--> JSON Pydantic
    class Config:
        orm_mode = True

# ==========================================
#   TOKEN (JWT)
# ==========================================

# Ce que renvoie la route /login
class Token(BaseModel):
    access_token: str
    token_type: str

# Pour décoder le token (interne)
class TokenData(BaseModel):
    email: Optional[str] = None

# ==========================================
#   MACHINE LEARNING (Input/Output)
# ==========================================

# ---- INPUT : data forms --> prediction
class EmployeeInput(BaseModel):
    EnvironmentSatisfaction : int
    JobInvolvement : int
    JobLevel : int
    JobSatisfaction : int
    StockOptionLevel : int
    BusinessTravel : str
    Department: str
    EducationField : str
    JobRole : str 
    MaritalStatus: str 
    OverTime: str

# --- OUTPUT : 
# -> résultat 
class PredictionOutput(BaseModel):
    prediction: int     # 0 ou 1
    probability: float  # ex: 0.85

# -> l'historique 
class HistoryOutput(BaseModel):
    id: int
    timestamp: datetime
    employee_id: Optional[int]
    probability: float
    
    class Config:
        orm_mode = True