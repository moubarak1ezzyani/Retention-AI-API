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
* **Generative AI**: API Integration (Gemini / HuggingFace) for text generation.

### DevOps
* **Containerization**: Docker & Docker Compose
* **Testing**: Pytest (Unit & Mocks)

---

## 📂 Project Structure

Here is the backend repository file tree:

```text
RetentionAI-Backend/
├── .github/
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline (GitHub Actions)
├── app/                         # Core FastAPI Application
│   ├── __init__.py
│   ├── main.py                  # App entry point & middleware setup
│   ├── core/                    
│   │   ├── config.py            # Environment variable loading (Pydantic BaseSettings)
│   │   └── security.py          # JWT, password hashing (bcrypt)
│   ├── db/
│   │   ├── database.py          # SQLAlchemy engine & session maker
│   │   └── models.py            # DB schemas (users, predictions_history)
│   ├── api/                     
│   │   ├── dependencies.py      # get_db, get_current_user (Auth middleware)
│   │   └── routes/              # Separated endpoints for cleaner code
│   │       ├── auth.py          # /register, /login
│   │       ├── predict.py       # /predict
│   │       └── retention.py     # /generate-retention-plan
│   ├── schemas/                 # Pydantic models (Input/Output validation)
│   │   ├── user.py
│   │   └── prediction.py
│   └── services/                
│       ├── ml_service.py        # Logic to load .pkl and run predictions
│       └── llm_service.py       # Logic to call Gemini/HuggingFace API
├── ml_dev/                      # Machine Learning Development
│   ├── data/                    # Raw & processed CSV files (Keep out of git)
│   ├── notebooks/               # EDA and experimentation
│   │   └── 01_eda_and_training.ipynb
│   └── train.py                 # Script to train and export the model reproducibly
├── models/                      # Serialized ML models (Used by API)
│   ├── attrition_model.pkl
│   └── scaler.pkl
├── tests/                       # Pytest directory
│   ├── conftest.py              # Test fixtures (test DB, mock clients)
│   ├── test_auth.py
│   ├── test_predict.py
│   └── test_llm.py              # Contains LLM mock tests
├── .env.example                 # Example of required environment variables
├── .gitignore                   # Ignore __pycache__, .env, venv, data/, etc.
├── docker-compose.yml           # Runs API and PostgreSQL together
├── Dockerfile                   # Instructions to build the API image
├── requirements.txt             # Python dependencies
└── README.md
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
GENAI_API_KEY=your_gemini_or_hf_api_key
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

## 🎯 Expected Result Example

Here is the typical flow for detecting departure risk (Churn):

### 1. Input (Employee Data)
The HR manager sends an employee's data via the `/predict` endpoint.

```json
POST /predict
{
  "Age": 35,
  "Department": "Sales",
  "JobRole": "Sales Executive",
  "OverTime": "Yes",
  "MonthlyIncome": 4500,
  "EnvironmentSatisfaction": 1
  // ... other fields
}
```

### 2. Output (Prediction + Action Plan)

The API detects a high probability (**78%**) and automatically triggers the generative AI because the risk exceeds the alert threshold (50%).

**JSON Response:**

```json
{
  "employee_id": "EMP-1024",
  "churn_probability": 0.78,
  "risk_level": "High",
  "suggested_retention_plan": [
    "✅ Propose a hybrid schedule (2 days of remote work) to compensate for overtime.",
    "✅ Review the variable part of the salary to align it with current sales performance.",
    "✅ Organize an HR meeting to discuss the causes of environmental dissatisfaction."
  ]
}
```

> **Note:** If the probability is below 50%, the `suggested_retention_plan` field will return `null` or a message indicating that no immediate action is required.

