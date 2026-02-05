"""
Test health check endpoint.
"""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """
    Test health check endpoint trả về status 200 và correct response.
    """
    response = client.get("/api/v1/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["database"] == "connected"


def test_root_endpoint(client: TestClient) -> None:
    """
    Test root endpoint.
    """
    response = client.get("/")
    
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
