from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- AUTH ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserOutput(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- ML INPUT ---
# Fichier: app/schemas.py
# Localisation: Vers la ligne 26 (remplace la classe EmployeeInput entière)

class EmployeeInput(BaseModel):
    # Ajout CRUCIAL suite au CSV : L'identifiant unique de l'employé
    EmployeeNumber: int 
    
    # Variables utilisées pour le Prompt IA (présentes dans le CSV)
    Age: int
    YearsAtCompany: int 
    
    # Vos variables features (déjà validées)
    EnvironmentSatisfaction: int
    JobInvolvement: int
    JobLevel: int
    JobSatisfaction: int
    StockOptionLevel: int
    BusinessTravel: str    
    Department: str
    EducationField: str
    JobRole: str 
    MaritalStatus: str 
    OverTime: str

    # Pour faciliter la conversion en DataFrame
    def to_dict(self):
        return self.model_dump()
    
# --- OUTPUTS ---
class PredictionOutput(BaseModel):
    prediction: int    # 0 (Reste) ou 1 (Part)
    probability: float # ex: 0.78

class RetentionPlanInput(BaseModel):
    employee_data: EmployeeInput
    churn_probability: float

class RetentionPlanOutput(BaseModel):
    plan: str # Texte brut (HTML/Markdown) retourné par Gemini
# __________________
""" from pydantic import BaseModel, EmailStr
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
        orm_mode = True """