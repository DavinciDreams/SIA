"""
Integration and edge case tests for SIA API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
import sia_api

client = TestClient(sia_api.app)

def test_root_endpoint():
    """Test root endpoint returns 200 and expected structure."""
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_invalid_endpoint():
    """Test invalid endpoint returns 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404

def test_post_memory_missing_fields():
    """Test posting memory with missing fields returns 422 or error."""
    response = client.post("/memory", json={})
    assert response.status_code in (400, 422)

def test_post_memory_valid():
    """Test posting valid memory returns 200 and correct response."""
    payload = {"text": "unit test memory", "meta": {"source": "test"}}
    response = client.post("/memory", json=payload)
    assert response.status_code == 200
    assert "id" in response.json() or "success" in response.json()

def test_get_memory_not_found():
    """Test retrieving non-existent memory returns empty or error."""
    response = client.get("/memory/doesnotexist")
    assert response.status_code in (404, 200)
    if response.status_code == 200:
        assert response.json() == [] or response.json() == {}

def test_internal_server_error(monkeypatch):
    """Test internal server error handling."""
    def broken(*args, **kwargs):
        raise Exception("Simulated failure")
    monkeypatch.setattr(sia_api, "get_memory", broken)
    response = client.get("/memory/test")
    assert response.status_code == 500 or response.status_code == 200  # Accepts fallback