# 🧠 Retention AI API - Churn Predictor & HR Assistant

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)
![Docker](https://img.shields.io/badge/Docker-Available-2496ED.svg)
![Machine Learning](https://img.shields.io/badge/AI-Scikit--Learn-orange.svg)

> **Intelligent HR decision support engine combining prediction and prescription.**

## 🔗 User Interface
This backend powers the HR dashboard available here:
👉 **[Retention-Decision-Dashboard](https://github.com/moubarak1ezzyani/Retention-Decision-Dashboard.git)**

**Retention AI** is a full-stack decision support application for Human Resources departments. It combines supervised learning (Machine Learning) to predict the risk of employee resignation with generative AI to propose personalized retention plans.

---

## 📋 Project Context

HR departments face high costs related to employee turnover. This project aims to shift from an *a posteriori* analysis to a **predictive** and **prescriptive** approach.

**Main Objectives:**
1.  **Predict**: Estimate the probability of an employee leaving (Churn Prediction).
2.  **Act**: Automatically generate a personalized action plan via Generative AI (LLM).
3.  **Industrialize**: Expose these models through a secure, containerized API.

---

## 🛠️ Architecture & Technologies

### Backend & API
* **Language**: Python
* **Framework**: FastAPI (Asynchronous, Fast)
* **Security**: JWT Authentication (JSON Web Tokens)
* **Database**: PostgreSQL (User storage & prediction history)
* **ORM**: SQLAlchemy (DB Interaction)

### Data Science & ML
* **Exploration**: Pandas, Seaborn
* **Preprocessing**: Scikit-learn (StandardScaler, OneHotEncoder)
* **Modeling**: RandomForestClassifier & LogisticRegression
* **Generative AI**: API Integration (HuggingFace / Llama-3) for text generation.

### DevOps
* **Containerization**: Docker & Docker Compose
* **Testing**: Pytest (Unit & Mocks)

---

## 📂 Project Structure

Here is the backend repository file tree:

```text
RETENTION-AI-API/
├── .github/
│   └── workflows/
│       └── ci.yml                       # CI/CD pipeline (GitHub Actions)
│
├── app/                                 # Core FastAPI Application
│   ├── __init__.py
│   ├── main.py                          # The skinny entry point
│   │
│   ├── core/                            # App-wide settings and security
│   │   ├── __init__.py
│   │   ├── config.py                
│   │   └── security.py              
│   │
│   ├── db/                              # ALL Data Structures & DB Logic
│   │   ├── __init__.py
│   │   ├── database.py                  # Setup engine & session
│   │   ├── models.py                    # SQLAlchemy classes (UserDB, PredictionHistoryDB)
│   │   ├── schemas.py                   # Pydantic classes (EmployeeFeatures, etc.)
│   │   └── crud.py                      # Database query functions
│   │
│   ├── api/                             # API Routing & Endpoints
│   │   ├── __init__.py
│   │   ├── dependencies.py              # get_db, get_current_user
│   │   └── routers/
│   │       ├── auth.py                  # /register, /login
│   │       ├── prediction.py            # /predict, /generate-retention-plan
│   │       └── utils.py                 # /health, /history
│   │
│   └── services/                        # Business logic (ML & AI)
│       ├── __init__.py
│       ├── ml_service.py                # Preprocessing and model inference
│       └── ai_service.py                # LLM prompt logic
│
├── data/                                # Raw & processed data (Keep out of git)
│   └── df_RetentionAI.csv
│
├── models/                              # Serialized ML artifacts (Ignored in Git)
│   ├── baseline/
│   │   ├── LogisticRegression_optimized_model.pkl
│   │   └── RandomForest_optimized_model.pkl
│   ├── encode_scale/
│   │   ├── ohe_encoder.pkl
│   │   ├── ordinal_encoder.pkl
│   │   └── scaler.pkl
│   └── smote/
│       ├── LogisticRegression_SMOTE_optimized.pkl
│       └── RandomForest_SMOTE_optimized.pkl
│
├── notebooks/                           # EDA and experimentation
│   └── lab.ipynb
│
├── tests/                               # Pytest directory
│   ├── __init__.py
│   ├── conftest.py                      # Test fixtures (test DB, mock clients)
│   ├── test_auth.py                     # Tests for registration and login
│   ├── test_predict.py                  # Tests for ML inference endpoint
│   └── test_llm.py                      # Tests for LLM retention plans
│
├── .env.example                         # Example of required environment variables
├── .gitignore                           # Ignore __pycache__, .env, venv, data/, models/, etc.
├── docker-compose.yml                   # Runs API and PostgreSQL together
├── Dockerfile                           # Instructions to build the API image
├── requirements.txt                     # Python dependencies
└── README.md                            # Project documentation
```

---

## 🚀 Installation and Getting Started

### Prerequisites

* Docker & Docker Compose (Recommended)
* **OR** Python 3.9+ and PostgreSQL installed locally.

### Option 1: Quick Start with Docker (Recommended)

1. **Clone the repository**
```bash
git clone [https://github.com/votre-username/RetentionAI.git](https://github.com/votre-username/RetentionAI.git)
cd RetentionAI
```

2. **Configure environment variables**
Create a `.env` file at the root:
```env
DATABASE_URL=postgresql://user:password@db:5432/retention_db
SECRET_KEY=your_secret_jwt_key
ALGORITHM=HS256
HF_TOKEN=your_huggingface_api_key
```

3. **Launch the services**
```bash
docker-compose up --build
```

The API will be accessible at `http://localhost:8000`.

### Option 2: Manual Installation (Local)

1. Create a virtual environment:
```bash
python -m venv RHvenv
source RHvenv/bin/activate  # or RHvenv\Scripts\activate on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

---

## 🔌 API Documentation

Once the application is running, the interactive Swagger documentation is available at:
👉 **http://localhost:8000/docs**

### Key Endpoints

#### 1. Authentication

* `POST /register`: Create an HR Manager account.
* `POST /login`: Obtain an **Access Token**.

#### 2. Prediction (Machine Learning)

* `POST /predict` (JWT Protected)
* **Input**: Employee data (Age, Dept, JobRole, Satisfaction...)
* **Output**: `{"churn_probability": 0.78}`

#### 3. Retention (Generative AI)

* `POST /generate-retention-plan` (JWT Protected)
* **Logic**: If probability > 50%, generates a plan.
* **Output**: Concrete suggestions (Remote work, Training, Salary raise...).

---

## 📊 Machine Learning Pipeline

The model was developed in the `ml_dev/` folder following these steps:

1. **Cleaning**: Removal of zero-variance variables (e.g., Over18).
2. **Encoding**: `OneHotEncoding` for categorical variables (Department, JobRole) and `LabelEncoding` for the target.
3. **Scaling**: `StandardScaler` for numerical variables.
4. **Training**: Comparison between **Logistic Regression** and **Random Forest**.
* *The Random Forest model was selected for its superior performance.*

5. **Export**: Saved via `joblib` in the `models/` folder.

---

## 🧪 Testing Guide (Swagger UI)

To evaluate the performance of the Machine Learning predictive model and the AI integration (Llama-3 via Hugging Face), you can use the interactive Swagger documentation.

### 🧠 How the System Works
* **Low Risk (≤ 50%):** The ML model predicts the employee is safe. The system bypasses the AI and returns a standard, hardcoded retention response.
* **High Risk (> 50%):** The ML model flags the employee as a flight risk. The system dynamically triggers the LLM to generate a customized 3-step retention plan based on their specific pain points.

**Instructions:**
1. Run your backend server and open the Swagger UI (usually at `http://localhost:8000/docs`).
2. Navigate to the `POST /generate-retention-plan` endpoint.
3. Click **Try it out**.
4. Clear the default JSON entirely and paste one of the raw data blocks below.
5. Click **Execute**.

### 🚨 Profile 1: High Risk (Triggers AI Generation)
This employee is overworked, underpaid, and unhappy.
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

### 🛡️ Profile 2: The "Happy Lifer" (Bypasses AI)
This is a senior manager with great pay, high satisfaction, and no overtime.
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

### ⚠️ Profile 3: The "Burnout" (Tests AI Reasoning)
This is a technical worker who generally likes their job but is suffering from severe burnout due to overtime.
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
