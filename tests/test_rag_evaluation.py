import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.parametrize(
    ("question", "expected_document"),
    [
        ("How do I request a notebook?", "it_equipment_policy.md"),
        ("How do I request access to a corporate system?", "access_management_policy.md"),
        ("What information is required for a purchase request?", "purchasing_policy.md"),
    ],
)
def test_supported_questions_are_grounded(question: str, expected_document: str):
    response = client.post("/ask", json={"question": question})

    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is True
    assert payload["sources"]
    assert payload["sources"][0]["document"] == expected_document
    assert payload["sources"][0]["score"] >= 0.45


def test_unsupported_question_is_not_grounded():
    response = client.post("/ask", json={"question": "What is the company's vacation policy?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["grounded"] is False
    assert payload["sources"] == []
    assert "not enough evidence" in payload["answer"].lower()
