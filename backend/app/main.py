from fastapi import FastAPI, HTTPException

from app.models import AnswerResult, AnswerSubmission, Question

app = FastAPI(
    title="Nouchi Quiz API",
    version="0.1.0",
)

QUESTIONS = [
    Question(
        id=1,
        text="Quelle est la capitale politique de la Côte d’Ivoire ?",
        choices=["Yamoussoukro", "Abidjan", "Bouaké"],
    ),
    Question(
        id=2,
        text="À quelle date la Côte d’Ivoire a-t-elle proclamé son indépendance ?",
        choices=["7 août 1960", "7 août 1958", "7 août 1970"],
    ),
    Question(
        id=3,
        text="Quel est l’hymne national ivoirien ?",
        choices=["L’Abidjanaise", "La Marseillaise", "L’Unité africaine"],
    ),
    Question(
        id=4,
        text="Quelle est la devise de la République de Côte d’Ivoire ?",
        choices=[
            "Union, Discipline, Travail",
            "Paix, Justice, Progrès",
            "Liberté, Égalité, Fraternité",
        ],
    ),
    Question(
        id=5,
        text="L’attiéké est principalement préparé à partir de quel tubercule ?",
        choices=["Manioc", "Igname", "Patate douce"],
    ),
]

ANSWER_KEY = {
    1: "Yamoussoukro",
    2: "7 août 1960",
    3: "L’Abidjanaise",
    4: "Union, Discipline, Travail",
    5: "Manioc",
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
