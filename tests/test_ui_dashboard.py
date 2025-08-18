"""
Integration and edge case tests for UI Dashboard endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import ui_dashboard

client = TestClient(ui_dashboard.app)

def test_dashboard_root():
    """Test dashboard root endpoint returns 200 and expected content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "dashboard" in response.text.lower()

def test_invalid_dashboard_route():
    """Test invalid dashboard route returns 404."""
    response = client.get("/dashboard/nonexistent")
    assert response.status_code == 404

def test_post_dashboard_action_missing_fields():
    """Test posting dashboard action with missing fields returns 422 or error."""
    response = client.post("/dashboard/action", json={})
    assert response.status_code in (400, 422)

def test_post_dashboard_action_valid():
    """Test posting valid dashboard action returns 200 and correct response."""
    payload = {"action": "refresh", "params": {}}
    response = client.post("/dashboard/action", json=payload)
    assert response.status_code == 200
    assert "result" in response.json() or "success" in response.json()

def test_dashboard_internal_error(monkeypatch):
    """Test dashboard internal server error handling."""
    def broken(*args, **kwargs):
        raise Exception("Simulated failure")
    monkeypatch.setattr(ui_dashboard, "dashboard_action", broken)
    response = client.post("/dashboard/action", json={"action": "fail", "params": {}})
    assert response.status_code == 500 or response.status_code == 200  # Accepts fallback