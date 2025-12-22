import pytest
import os
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch



# --------------------------------------------------------
#   CONFGI PATH
# --------------------------------------------------------
# 1. On récupère le chemin du dossier courant (tests)
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. On remonte d'un cran pour obtenir le chemin de la racine (rep)
root_dir = os.path.dirname(current_dir)

# 3. On ajoute la racine aux chemins que Python surveille
sys.path.append(root_dir)

sys.path.append(os.path.join(root_dir, "app"))

from app.main import app
from app.database import get_db, MyBase
from app import services, schemas



# --------------------------------------------------------
#   CONFIGURATION DE LA BDD DE TEST (SQLite en mémoire)
# --------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- db temporaire :  creation tables  
MyBase.metadata.create_all(bind=engine)

# --- get_db : overriding --> db de test
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --------------------------------------------------------
#   TESTS
# --------------------------------------------------------

def test_read_main():
    response = client.get("/")      # homepage
    assert response.status_code == 200
    assert response.json() == {"message": "RetentionAI API is running"}

# --- sign Up
def test_register_user():
    response = client.post("/register", json={
        "username": "youssef",
        "password": "securepassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "youssef"
    assert "id" in data

# --- sign In
def test_login_user():
    # --- Création
    client.post("/register", json={"username": "youssef", "password": "securepassword"})
    
    # --- Connexion
    # OAuth2 : data => Form-Data, pas JSON pur
    response = client.post("/login", data={
        "username": "youssef", 
        "password": "securepassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

# --- mcoking : ML & gemini
@patch("app.services.pipeline")    # ML joblib : simulation
def test_predict_endpoint(mock_pipeline):

    # ML : exists & pred = 1
    mock_pipeline.predict.return_value = [1]
    
    mock_pipeline.predict_proba.return_value = [[0.2, 0.8]]    # départ : 80% de chance  

    # Auth requise
    token = test_login_user()
    
    payload = {
        "EmployeeNumber": 100,
        # "Age": 30,
        "Department": "Sales",
        "JobRole": "Manager",
        "BusinessTravel": "Travel_Rarely",
        "OverTime": "Yes",
        "MaritalStatus": "Single",
        "EducationField": "Marketing",
        "JobLevel": 2,
        "JobSatisfaction": 1,
        "EnvironmentSatisfaction": 1,
        "JobInvolvement": 2,
        "StockOptionLevel": 0,
        "YearsAtCompany": 2
    }

    response = client.post(
        "/predict", 
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    
    # Vérifications
    assert "prediction" in data
    assert "probability" in data

    # mocké proba=0.8 --> pred=0.8 (attendu)
    assert data["probability"] == 0.8 

@patch("app.services.client")        # Gemini : simulation
def test_generate_plan(mock_gemini):

    # Auth
    token = test_login_user()

    # Mock : config --> fake obj resp
    mock_response = MagicMock()
    mock_response.text = " Action 1: Augmentation.\n Action 2: Formation."
    mock_gemini.generate_content.return_value = mock_response

    payload = {
        "employee_data": {
            "EmployeeNumber": 101,
            # "Age": 45,
            "Department": "R&D",
            "JobRole": "Scientist",
            "BusinessTravel": "Non-Travel",
            "OverTime": "No",
            "MaritalStatus": "Married",
            "EducationField": "Medical",
            "JobLevel": 3,
            "JobSatisfaction": 4,
            "EnvironmentSatisfaction": 4,
            "JobInvolvement": 3,
            "StockOptionLevel": 1,
            "YearsAtCompany": 10
        },
        "churn_probability": 0.85
    }

    response = client.post(
        "/generate-retention-plan", 
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "plan" in data
    assert "Action 1" in data["plan"]   # imposer le texte brut