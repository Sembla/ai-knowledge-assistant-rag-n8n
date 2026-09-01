from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_question_validation_rejects_short_input():
    response = client.post("/ask", json={"question": "a"})
    assert response.status_code == 422
