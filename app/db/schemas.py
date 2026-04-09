from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
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
class EmployeeInput(BaseModel):
    # Tracking ID (Dropped before prediction, but needed for DB history)
    EmployeeNumber: int
    
    # Numeric 
    Age: int
    
    # Ordinal Ranks (Typically 1-4 or 1-5 in IBM HR dataset)
    Education: int = Field(..., ge=1, le=5)
    EnvironmentSatisfaction: int = Field(..., ge=1, le=4)
    JobInvolvement: int = Field(..., ge=1, le=4)
    JobSatisfaction: int = Field(..., ge=1, le=4)
    PerformanceRating: int = Field(..., ge=1, le=4)
    RelationshipSatisfaction: int = Field(..., ge=1, le=4)
    StockOptionLevel: int = Field(..., ge=0, le=3)
    WorkLifeBalance: int = Field(..., ge=1, le=4)
    
    # Categorical Ordinal
    BusinessTravel: str    
    OverTime: str
    Gender: str
    
    # Categorical Nominal
    Department: str
    EducationField: str
    JobRole: str 
    MaritalStatus: str 

    # NOTE: If your raw CSV has other numeric columns not listed in your ML script 
    # (e.g., MonthlyIncome, YearsAtCompany, DistanceFromHome), 
    # you MUST add them here so the dictionary matches your scaler's expected input!

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
    plan: str          # Texte HTML/Markdown généré par l'IA