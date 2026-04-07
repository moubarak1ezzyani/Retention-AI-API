from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- AUTH 
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

# --- ML INPUT 
class EmployeeInput(BaseModel):
    # Emp : unique id  
    EmployeeNumber : int
    Age : int
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

    # conversion en DataFrame
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
    plan: str       # gemini : Texte HTML/Markdown 
