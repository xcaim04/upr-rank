"""Integration tests for the health check endpoint."""

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    """GET /health reports the backend service as alive."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "upr-rank-backend"}
