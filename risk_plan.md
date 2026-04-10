Here are the three test profiles you can copy and paste directly into your Swagger UI to test the different behaviors of your ML model and the Hugging Face AI integration.

To use these:
1. Open your `/generate-retention-plan` endpoint in Swagger.
2. Click **Try it out**.
3. Clear the default text entirely and paste one of the JSON blocks below.
4. Click **Execute**.

### 1. The "High Risk" Profile (Triggers the AI)
This employee is overworked, underpaid, and unhappy. The ML model should give a high churn probability (> 0.50), which will trigger Hugging Face to generate a custom 3-step retention plan for a Sales Rep.

```json
{
  "Age": 24,
  "DailyRate": 400,
  "DistanceFromHome": 25,
  "HourlyRate": 45,
  "MonthlyIncome": 2500,
  "MonthlyRate": 10000,
  "NumCompaniesWorked": 4,
  "PercentSalaryHike": 11,
  "TotalWorkingYears": 2,
  "TrainingTimesLastYear": 2,
  "YearsAtCompany": 1,
  "YearsInCurrentRole": 1,
  "YearsSinceLastPromotion": 0,
  "YearsWithCurrManager": 1,
  "BusinessTravel": "Travel_Frequently",
  "OverTime": "Yes",
  "Gender": "Male",
  "Department": "Sales",
  "EducationField": "Marketing",
  "JobRole": "Sales Representative",
  "MaritalStatus": "Single",
  "Education": 2,
  "EnvironmentSatisfaction": 1,
  "JobInvolvement": 2,
  "JobSatisfaction": 1,
  "PerformanceRating": 3,
  "RelationshipSatisfaction": 2,
  "StockOptionLevel": 0,
  "WorkLifeBalance": 1,
  "employee_id": "EMP-001-RISK"
}
```

### 2. The "Happy Lifer" Profile (Tests the Hardcoded Response)
This is a senior manager with great pay, high satisfaction, and no overtime. The ML model should return a low churn probability (< 0.50). This will **bypass** the AI completely and return your hardcoded standard response.

```json
{
  "Age": 45,
  "DailyRate": 1200,
  "DistanceFromHome": 5,
  "HourlyRate": 85,
  "MonthlyIncome": 15000,
  "MonthlyRate": 20000,
  "NumCompaniesWorked": 1,
  "PercentSalaryHike": 18,
  "TotalWorkingYears": 20,
  "TrainingTimesLastYear": 5,
  "YearsAtCompany": 15,
  "YearsInCurrentRole": 10,
  "YearsSinceLastPromotion": 5,
  "YearsWithCurrManager": 8,
  "BusinessTravel": "Non-Travel",
  "OverTime": "No",
  "Gender": "Female",
  "Department": "Research & Development",
  "EducationField": "Life Sciences",
  "JobRole": "Manager",
  "MaritalStatus": "Married",
  "Education": 4,
  "EnvironmentSatisfaction": 4,
  "JobInvolvement": 4,
  "JobSatisfaction": 4,
  "PerformanceRating": 4,
  "RelationshipSatisfaction": 4,
  "StockOptionLevel": 2,
  "WorkLifeBalance": 4,
  "employee_id": "EMP-002-SAFE"
}
```

### 3. The "Burnout" Profile (Tests AI Context)
This is a technical worker who likes their job (`JobInvolvement`: 4) but is doing too much overtime and has a terrible work-life balance (`WorkLifeBalance`: 1). It tests if the AI will specifically address the burnout/overtime in its generated JSON.

```json
{
  "Age": 32,
  "DailyRate": 900,
  "DistanceFromHome": 10,
  "HourlyRate": 75,
  "MonthlyIncome": 7000,
  "MonthlyRate": 15000,
  "NumCompaniesWorked": 2,
  "PercentSalaryHike": 15,
  "TotalWorkingYears": 10,
  "TrainingTimesLastYear": 3,
  "YearsAtCompany": 5,
  "YearsInCurrentRole": 4,
  "YearsSinceLastPromotion": 1,
  "YearsWithCurrManager": 4,
  "BusinessTravel": "Travel_Rarely",
  "OverTime": "Yes",
  "Gender": "Female",
  "Department": "Research & Development",
  "EducationField": "Technical Degree",
  "JobRole": "Laboratory Technician",
  "MaritalStatus": "Single",
  "Education": 3,
  "EnvironmentSatisfaction": 2,
  "JobInvolvement": 4,
  "JobSatisfaction": 3,
  "PerformanceRating": 4,
  "RelationshipSatisfaction": 3,
  "StockOptionLevel": 0,
  "WorkLifeBalance": 1,
  "employee_id": "EMP-003-BURNOUT"
}
```