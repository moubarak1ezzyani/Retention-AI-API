import pytest

def test_register_success(client):
    """
    Test case: Successful user registration.
    Verifies that a new user can be created and receives a 201 Created status.
    """
    payload = {"username": "qa_specialist", "password": "test_password_123"}
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "registered successfully" in data["message"]
    assert "id" in data

def test_register_duplicate_user(client, test_user_data):
    """
    Test case: Duplicate registration failure.
    Verifies that the system prevents registering the same username twice (409 Conflict).
    """
    # First successful registration
    client.post("/register", json=test_user_data)
    
    # Second registration with same username
    response = client.post("/register", json=test_user_data)
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"]

def test_login_success(client, test_user_data):
    """
    Test case: Successful authentication.
    Verifies that valid credentials return a JWT access token.
    """
    # Ensure user exists
    client.post("/register", json=test_user_data)
    
    # Login using OAuth2PasswordRequestForm (form-data)
    response = client.post("/login", data=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user_data):
    """
    Test case: Authentication failure (invalid password).
    Verifies that incorrect passwords return a 401 Unauthorized status.
    """
    client.post("/register", json=test_user_data)
    
    invalid_data = {
        "username": test_user_data["username"],
        "password": "definitely_wrong_password"
    }
    response = client.post("/login", data=invalid_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_user_not_found(client):
    """
    Test case: Authentication failure (non-existent user).
    Verifies that non-existent users cannot log in.
    """
    unknown_user = {"username": "non_existent_user", "password": "some_password"}
    response = client.post("/login", data=unknown_user)
    assert response.status_code == 401
