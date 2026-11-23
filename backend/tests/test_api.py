from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_initial_stats():
    response = client.get("/api/stats")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["total_events"], int)
    assert data["total_events"] >= 0
    assert data["monitoring_status"] == "database_ready"
