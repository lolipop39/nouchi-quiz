from pydantic import BaseModel, Field


class Question(BaseModel):
    id: int = Field(ge=1)
    text: str = Field(min_length=1)
    choices: list[str] = Field(min_length=2)


class AnswerSubmission(BaseModel):
    question_id: int = Field(ge=1)
    choice: str = Field(min_length=1)


class AnswerResult(BaseModel):
    question_id: int
    correct: bool
