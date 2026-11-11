from fastapi import FastAPI

from app.models import Question

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
