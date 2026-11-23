from fastapi.testclient import TestClient
from app.main import app


def test_event_storage():
    with TestClient(app) as client:
        response = client.post(
            "/api/events",
            json={
                "source_ip": "192.0.2.10",
                "destination_ip": "192.0.2.20",
                "destination_port": 443,
                "protocol": "TCP"
            }
        )

        assert response.status_code == 200
        assert response.json()["status"] == "stored"

        events = client.get("/api/events")

        assert events.status_code == 200
        assert any(
            event["id"] == response.json()["id"]
            for event in events.json()
        )


def test_database_stats():
    with TestClient(app) as client:
        response = client.get("/api/stats")

        assert response.status_code == 200
        assert response.json()["monitoring_status"] == "database_ready"
