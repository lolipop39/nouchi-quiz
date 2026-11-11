from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_questions_hides_answers():
    response = client.get("/questions")

    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 2
    assert set(questions[0]) == {"id", "text", "choices"}


def test_submit_correct_answer():
    response = client.post(
        "/answers",
        json={"question_id": 1, "choice": "Réponse A"},
    )

    assert response.status_code == 200
    assert response.json() == {"question_id": 1, "correct": True}


def test_submit_incorrect_answer():
    response = client.post(
        "/answers",
        json={"question_id": 1, "choice": "Réponse B"},
    )

    assert response.status_code == 200
    assert response.json() == {"question_id": 1, "correct": False}


def test_submit_answer_for_missing_question():
    response = client.post(
        "/answers",
        json={"question_id": 999, "choice": "Réponse A"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Question introuvable"}
