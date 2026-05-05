from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional

from database import get_db
from models.quiz import Quiz, Question, QuizAttempt
from models.user import User
from schemas.quiz import QuizOut, QuizDetail, SubmitAnswers, AttemptOut, AttemptResult
from core.security import get_current_user
from ws_manager import manager

router = APIRouter(prefix="/user", tags=["User"])

# ──────────────────────────────────────────────────────────
# TIMEZONE (IST)
# ──────────────────────────────────────────────────────────
IST = ZoneInfo("Asia/Kolkata")


def now_ist():
    return datetime.now(IST)


def normalize_ist(dt):
    """
    DB stores IST as naive → convert to IST aware
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST)
    return dt.astimezone(IST)


def to_naive(dt):
    """
    Convert aware → naive (for DB insert)
    """
    if dt is None:
        return None
    return dt.replace(tzinfo=None)


# ──────────────────────────────────────────────────────────
# HELPER
# ──────────────────────────────────────────────────────────
def enrich_attempt(attempt: QuizAttempt, quiz: Optional[Quiz]) -> dict:
    return {
        "id": attempt.id,
        "quiz_id": attempt.quiz_id,
        "user_id": attempt.user_id,
        "score": attempt.score,
        "total": attempt.total,
        "submitted": attempt.submitted,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "quiz_title": quiz.title if quiz else None,
        "difficulty": quiz.difficulty.value if quiz else None,
    }


# ──────────────────────────────────────────────────────────
# GET QUIZZES
# ──────────────────────────────────────────────────────────
@router.get("/quizzes", response_model=List[QuizOut])
async def available_quizzes(
    difficulty: Optional[str] = None,
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Quiz).where(Quiz.is_active == True)

    if difficulty:
        q = q.where(Quiz.difficulty == difficulty)
    if subject:
        q = q.where(Quiz.subject == subject)

    result = await db.execute(q)
    quizzes = result.scalars().all()

    for quiz in quizzes:
        count = await db.execute(
            select(func.count(Question.id)).where(Question.quiz_id == quiz.id)
        )
        quiz.question_count = count.scalar()

    return quizzes


# ──────────────────────────────────────────────────────────
# GET QUIZ
# ──────────────────────────────────────────────────────────
@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    now = now_ist()
    start = normalize_ist(quiz.scheduled_start)
    end = normalize_ist(quiz.scheduled_end)

    if end and now > end:
        raise HTTPException(403, "Quiz time has ended")

    is_locked = bool(start and now < start)

    quiz.question_count = len(quiz.questions)

    return {
        **quiz.__dict__,
        "questions": quiz.questions,
        "question_count": quiz.question_count,
        "is_locked": is_locked,
        "start_time": start,
        "end_time": end,
    }


# ──────────────────────────────────────────────────────────
# START QUIZ
# ──────────────────────────────────────────────────────────
@router.post("/quizzes/{quiz_id}/start", response_model=AttemptOut, status_code=201)
async def start_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    now = now_ist()
    start = normalize_ist(quiz.scheduled_start)
    end = normalize_ist(quiz.scheduled_end)

    if start and now < start:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Quiz not started",
                "start_time": start.isoformat(),
            },
        )

    if end and now > end:
        raise HTTPException(403, "Quiz time has ended")

    existing = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.submitted == False,
        )
    )
    attempt = existing.scalar_one_or_none()

    if not attempt:
        attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            answers={},
            started_at=to_naive(now),   # ✅ FIX HERE
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)

        await manager.broadcast({
            "type": "quiz_started",
            "user": current_user.username,
            "quiz_id": quiz_id,
            "quiz_title": quiz.title,
            "difficulty": quiz.difficulty.value,
            "subject": quiz.subject,
            "attempt_id": attempt.id,
            "ts": now.isoformat(),
        })

    return AttemptOut(**enrich_attempt(attempt, quiz))


# ──────────────────────────────────────────────────────────
# SUBMIT QUIZ
# ──────────────────────────────────────────────────────────
@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResult)
async def submit_quiz(
    attempt_id: int,
    data: SubmitAnswers,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.user_id == current_user.id,
        )
    )
    attempt = result.scalar_one_or_none()

    if not attempt:
        raise HTTPException(404, "Attempt not found")

    if attempt.submitted:
        raise HTTPException(400, "Already submitted")

    quiz_result = await db.execute(select(Quiz).where(Quiz.id == attempt.quiz_id))
    quiz = quiz_result.scalar_one_or_none()

    q_result = await db.execute(
        select(Question).where(Question.quiz_id == attempt.quiz_id)
    )
    questions = q_result.scalars().all()

    score = sum(
        1 for q in questions
        if data.answers.get(q.id) == q.correct_option
    )

    now = now_ist()

    attempt.answers = {str(k): v for k, v in data.answers.items()}
    attempt.score = score
    attempt.total = len(questions)
    attempt.submitted = True
    attempt.submitted_at = to_naive(now)   # ✅ FIX HERE

    await db.commit()
    await db.refresh(attempt)

    return AttemptResult(
        **enrich_attempt(attempt, quiz),
        answers={int(k): v for k, v in attempt.answers.items()},
        questions=questions,
    )