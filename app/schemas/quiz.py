from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from models.quiz import DifficultyLevel


# ── Question ──────────────────────────────────────────────
class QuestionCreate(BaseModel):
    text: str
    options: List[str]          # exactly 4 items
    correct_option: int         # 0-3
    explanation: Optional[str] = None


class QuestionOut(BaseModel):
    id: int
    quiz_id: int
    text: str
    options: List[str]
    explanation: Optional[str]

    class Config:
        from_attributes = True


class QuestionOutWithAnswer(QuestionOut):
    correct_option: int


# ── Quiz ──────────────────────────────────────────────────
class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None
    difficulty: DifficultyLevel
    subject: str
    topic: str
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    is_active: Optional[bool] = None


class QuizOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    difficulty: DifficultyLevel
    subject: str
    topic: str
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    is_active: bool
    created_at: datetime
    question_count: int = 0

    class Config:
        from_attributes = True


class QuizDetail(QuizOut):
    questions: List[QuestionOut] = []


# ── Attempt ───────────────────────────────────────────────
class SubmitAnswers(BaseModel):
    answers: Dict[int, int]     # {question_id: chosen_option}


class AttemptOut(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: int
    total: int
    submitted: bool
    started_at: datetime
    submitted_at: Optional[datetime]
    # ↓ populated by the router before returning — not DB columns
    quiz_title: Optional[str] = None
    difficulty: Optional[str] = None

    class Config:
        from_attributes = True


class AttemptResult(AttemptOut):
    answers: Dict[int, int]
    questions: List[QuestionOutWithAnswer] = []
