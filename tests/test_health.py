from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint_returns_structured_placeholder():
    response = client.post("/ask", json={"question": "How do I request a notebook?"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"answer", "sources", "grounded"}
    assert body["grounded"] is False
