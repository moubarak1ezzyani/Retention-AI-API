from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmployeeFeatures(BaseModel):
    Age: float
    DailyRate: float
    DistanceFromHome: float
    HourlyRate: float
    MonthlyIncome: float
    MonthlyRate: float
    NumCompaniesWorked: float
    PercentSalaryHike: float
    TotalWorkingYears: float
    TrainingTimesLastYear: float
    YearsAtCompany: float
    YearsInCurrentRole: float
    YearsSinceLastPromotion: float
    YearsWithCurrManager: float
    BusinessTravel: str
    OverTime: str
    Gender: str
    Department: str
    EducationField: str
    JobRole: str
    MaritalStatus: str
    Education: int
    EnvironmentSatisfaction: int
    JobInvolvement: int
    JobSatisfaction: int
    PerformanceRating: int
    RelationshipSatisfaction: int
    StockOptionLevel: int
    WorkLifeBalance: int
    employee_id: Optional[str] = None

class PredictResponse(BaseModel):
    employee_id: Optional[str]
    department: Optional[str] = None  
    role: Optional[str] = None        
    churn_probability: float
    risk_level: str

class RetentionPlanRequest(EmployeeFeatures):
    pass

class RetentionPlanResponse(BaseModel):
    churn_probability: float
    retention_plan: list[str]