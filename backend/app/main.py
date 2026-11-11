from fastapi import FastAPI, HTTPException

from app.models import AnswerResult, AnswerSubmission, Question

app = FastAPI(
    title="Nouchi Quiz API",
    version="0.1.0",
)

QUESTIONS = [
    Question(
        id=1,
        text="Question de démonstration : choisis une réponse.",
        choices=["Réponse A", "Réponse B", "Réponse C"],
    ),
    Question(
        id=2,
        text="Deuxième question de démonstration.",
        choices=["Choix 1", "Choix 2", "Choix 3"],
    ),
]

ANSWER_KEY = {
    1: "Réponse A",
    2: "Choix 2",
}


@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur Nouchi Quiz API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/questions", response_model=list[Question])
def list_questions():
    return QUESTIONS


@app.post("/answers", response_model=AnswerResult)
def submit_answer(submission: AnswerSubmission):
    correct_choice = ANSWER_KEY.get(submission.question_id)

    if correct_choice is None:
        raise HTTPException(status_code=404, detail="Question introuvable")

    return AnswerResult(
        question_id=submission.question_id,
        correct=submission.choice == correct_choice,
    )
