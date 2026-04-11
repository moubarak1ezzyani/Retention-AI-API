from unittest.mock import patch
import pytest

def test_generate_plan_high_risk_success(client, auth_headers, mock_employee_payload):
    """
    Test case: High-risk retention plan generation.
    Verifies that for proba > 0.50, the LLM service is called and returns a plan.
    """
    with patch("app.api.routers.retention.predict_churn") as mock_ml, \
         patch("app.api.routers.retention.generate_plan") as mock_llm:
        
        # Simulate high risk
        mock_ml.return_value = 0.88
        # Simulate LLM response
        mock_llm.return_value = [
            "Conduct structured 1-on-1 discovery meeting",
            "Review salary benchmark for Sales Role",
            "Implement flexible Friday scheduling"
        ]
        
        response = client.post(
            "/generate-retention-plan",
            json=mock_employee_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["churn_probability"] == 0.88
        assert len(data["retention_plan"]) == 3
        assert "salary benchmark" in data["retention_plan"][1]
        
        mock_ml.assert_called_once()
        mock_llm.assert_called_once()

def test_generate_plan_low_risk_skip_llm(client, auth_headers, mock_employee_payload):
    """
    Test case: Low-risk scenario (No LLM call).
    Verifies that for proba <= 0.50, a generic message is returned without calling the LLM API.
    """
    with patch("app.api.routers.retention.predict_churn") as mock_ml, \
         patch("app.api.routers.retention.generate_plan") as mock_llm:
        
        # Simulate low risk
        mock_ml.return_value = 0.15
        
        response = client.post(
            "/generate-retention-plan",
            json=mock_employee_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["churn_probability"] == 0.15
        # Verify the generic response for low risk
        assert any("no urgent retention action" in plan_item.lower() for plan_item in data["retention_plan"])
        
        # Critical: LLM should NOT be called
        mock_llm.assert_not_called()

def test_generate_plan_unauthorized(client, mock_employee_payload):
    """
    Test case: Unauthorized access for retention plan.
    Verifies that protected retention routes require valid JWT.
    """
    response = client.post("/generate-retention-plan", json=mock_employee_payload)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_generate_plan_llm_failure(client, auth_headers, mock_employee_payload):
    """
    Test case: External LLM service failure.
    Verifies that the API handles LLM errors gracefully (returning 502 Bad Gateway).
    """
    with patch("app.api.routers.retention.predict_churn") as mock_ml, \
         patch("app.api.routers.retention.generate_plan") as mock_llm:
        
        mock_ml.return_value = 0.90
        # Simulate an API error (e.g., timeout or quota exceeded)
        mock_llm.side_effect = ValueError("HuggingFace API timeout")
        
        response = client.post(
            "/generate-retention-plan",
            json=mock_employee_payload,
            headers=auth_headers
        )
        
        assert response.status_code == 502
        assert "Gemini generation error" in response.json()["detail"]
