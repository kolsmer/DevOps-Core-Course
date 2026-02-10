from fastapi.testclient import TestClient

from app import app


client = TestClient(app)


def test_root_returns_expected_structure():
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["service"]["name"] == "devops-info-service"
    assert data["service"]["framework"] == "FastAPI"
    assert data["request"]["path"] == "/"
    assert isinstance(data["runtime"]["uptime_seconds"], int)

    endpoints = {item["path"] for item in data["endpoints"]}
    assert "/" in endpoints
    assert "/health" in endpoints


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["uptime_seconds"], int)


def test_not_found_handler():
    response = client.get("/missing")
    assert response.status_code == 404

    data = response.json()
    assert data["error"] == "Not Found"
    assert data["path"] == "/missing"
