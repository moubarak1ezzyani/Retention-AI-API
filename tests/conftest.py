import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base
from app.api.dependencies import get_db

# --- Database Setup for Testing (SQLite in-memory) ---
# We use StaticPool to maintain the same connection across the session during tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Initializes the test database.
    Creates all tables at the start of the session and drops them at the end.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    """
    Fixture to provide a clean database session for each test.
    Automatically rolls back changes or handles cleanup after each test.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_db():
    """Implementation of the get_db override for FastAPI."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_dependencies():
    """
    Injects the test database into the FastAPI application dependencies.
    Cleans up the overrides after each test.
    """
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    """Fixture to provide a TestClient for making requests to the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def test_user_data():
    """Fixture providing standard user credentials for testing."""
    return {"username": "qa_manager", "password": "secure_password_101"}

@pytest.fixture
def auth_headers(client, test_user_data):
    """
    Fixture to provide authentication headers with a valid JWT.
    Automatically creates the user and logs in to retrieve the token.
    """
    # Create user if it doesn't exist (using the /register endpoint)
    client.post("/register", json=test_user_data)
    
    # Login to retrieve the JWT
    login_response = client.post("/login", data=test_user_data)
    token = login_response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_employee_payload():
    """Fixture providing a realistic employee feature set for ML/LLM tests."""
    return {
        "Age": 32.0,
        "DailyRate": 800.0,
        "DistanceFromHome": 5.0,
        "HourlyRate": 60.0,
        "MonthlyIncome": 5000.0,
        "MonthlyRate": 15000.0,
        "NumCompaniesWorked": 2.0,
        "PercentSalaryHike": 15.0,
        "TotalWorkingYears": 10.0,
        "TrainingTimesLastYear": 2.0,
        "YearsAtCompany": 5.0,
        "YearsInCurrentRole": 3.0,
        "YearsSinceLastPromotion": 1.0,
        "YearsWithCurrManager": 3.0,
        "BusinessTravel": "Travel_Rarely",
        "OverTime": "No",
        "Gender": "Male",
        "Department": "Research & Development",
        "EducationField": "Medical",
        "JobRole": "Laboratory Technician",
        "MaritalStatus": "Married",
        "Education": 3,
        "EnvironmentSatisfaction": 3,
        "JobInvolvement": 3,
        "JobSatisfaction": 3,
        "PerformanceRating": 3,
        "RelationshipSatisfaction": 3,
        "StockOptionLevel": 1,
        "WorkLifeBalance": 3,
        "employee_id": "EMP001"
    }
