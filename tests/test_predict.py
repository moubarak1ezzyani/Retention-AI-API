from unittest.mock import patch
import pytest

def test_predict_success(client, auth_headers, mock_employee_payload):
    """
    Test case: Successful churn prediction.
    Verifies that a full payload with valid authentication returns the expected risk level.
    Mocks the ML service to avoid loading artifacts.
    """
    # We patch where it's USED in the router
    with patch("app.api.routers.predict.predict_churn") as mock_calc:
        # Simulate a high-risk probability (75%)
        mock_calc.return_value = 0.75
        
        response = client.post(
            "/predict",
            json=mock_employee_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["churn_probability"] == 0.75
        assert data["risk_level"] == "High"
        assert data["employee_id"] == mock_employee_payload["employee_id"]
        mock_calc.assert_called_once()

def test_predict_unauthorized(client, mock_employee_payload):
    """
    Test case: Unauthorized access.
    Verifies that the endpoint is protected by JWT authentication.
    """
    response = client.post("/predict", json=mock_employee_payload)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_predict_pydantic_validation(client, auth_headers):
    """
    Test case: Data validation.
    Verifies that Pydantic enforces the schema requirements (e.g., missing required fields).
    """
    # Send a payload missing many required fields
    invalid_payload = {"Age": 25, "employee_id": "ERR001"}
    
    response = client.post(
        "/predict",
        json=invalid_payload,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Unprocessable Entity
    # The response detail should list missing fields
    errors = response.json()["detail"]
    assert any("DailyRate" in err["msg"] or "DailyRate" in err["loc"] for err in errors)

def test_predict_inference_error_handling(client, auth_headers, mock_employee_payload):
    """
    Test case: Error handling during inference.
    Verifies that exceptions in the service are caught and return a 422 status.
    """
    with patch("app.api.routers.predict.predict_churn") as mock_calc:
        # Simulate a crash in the preprocessing/model logic
        mock_calc.side_effect = ValueError("Corrupted model artifact")
        
        response = client.post(
            "/predict",
            json=mock_employee_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        assert "inference error" in response.json()["detail"].lower()
