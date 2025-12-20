import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock, patch

# Importations depuis votre application
from app.main import app
from app.database import get_db, Base
from app import services

# --------------------------------------------------------
# 1. CONFIGURATION DE LA BDD DE TEST (SQLite en mémoire)
# --------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# On crée les tables dans la BDD temporaire
Base.metadata.create_all(bind=engine)

# Surcharge de la dépendance get_db pour utiliser la BDD de test
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --------------------------------------------------------
# 2. LES TESTS
# --------------------------------------------------------

def test_read_main():
    """Vérifie que l'API tourne"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "RetentionAI API is running 🚀"}

def test_register_user():
    """Test de création de compte"""
    response = client.post("/register", json={
        "email": "testhr@company.com",
        "password": "securepassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testhr@company.com"
    assert "id" in data

def test_login_user():
    """Test de login et récupération du JWT"""
    # 1. Création
    client.post("/register", json={"email": "login@test.com", "password": "123"})
    
    # 2. Connexion
    # Note: OAuth2 form envoie les données en Form-Data, pas en JSON pur
    response = client.post("/login", data={
        "username": "login@test.com", 
        "password": "123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

# --- MOCKING DU ML ET DE GEMINI ---

@patch("app.services.model") # On simule le modèle ML chargé via joblib
def test_predict_endpoint(mock_model):
    """
    Test de la prédiction avec Mock.
    On fait croire à l'appli que le modèle existe et prédit '1' (Départ).
    """
    # On configure le Mock pour qu'il réponde toujours [1] (Départ)
    mock_model.predict.return_value = [1]
    
    # Si vous avez géré le predict_proba dans services.py
    # Il faut mocker aussi predict_proba s'il est utilisé
    mock_model.predict_proba.return_value = [[0.2, 0.8]] # 80% de chance de départ

    # Authentification requise
    token = test_login_user()
    
    payload = {
        "EmployeeNumber": 100,
        "Age": 30,
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
    # Comme on a mocké proba à 0.8, on attend 0.8
    assert data["probability"] == 0.8 

@patch("app.services.llm_model") # On simule Gemini
def test_generate_plan(mock_gemini):
    """
    Test de la génération IA sans payer Google.
    """
    # Authentification
    token = test_login_user()

    # On configure le Mock pour renvoyer un faux objet réponse
    mock_response = MagicMock()
    mock_response.text = "Action 1: Augmentation.\nAction 2: Formation."
    mock_gemini.generate_content.return_value = mock_response

    payload = {
        "employee_data": {
            "EmployeeNumber": 101,
            "Age": 45,
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
    assert "Action 1" in data["plan"] # On vérifie qu'on reçoit bien le texte brut