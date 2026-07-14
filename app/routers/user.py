from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Optional

from app.database import get_db
from app.models.quiz import Quiz, Question, QuizAttempt, QuizType
from app.models.user import User
from app.schemas.quiz import QuizOut, QuizDetail, SubmitAnswers, AttemptOut, AttemptResult
from app.core.security import get_current_user
from app.ws_manager import manager

router = APIRouter(prefix="/user", tags=["User"])

IST = ZoneInfo("Asia/Kolkata")


def now_ist():
    return datetime.now(IST)


def normalize_ist(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=IST)
    return dt.astimezone(IST)


def to_naive(dt):
    if dt is None:
        return None
    return dt.replace(tzinfo=None)


def enrich_attempt(attempt: QuizAttempt, quiz: Optional[Quiz], user: Optional[User] = None) -> dict:
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
        "username": user.username if user else None,
    }


@router.get("/quizzes", response_model=List[QuizOut])
async def available_quizzes(
    difficulty: Optional[str] = None,
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Quiz).where(Quiz.is_active == True, Quiz.quiz_type == QuizType.scheduled.value)
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


@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Quiz).options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id, Quiz.is_active == True, Quiz.quiz_type == QuizType.scheduled.value)
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    now = now_ist()
    end = normalize_ist(quiz.scheduled_end)
    if end and now > end:
        raise HTTPException(403, "Quiz time has ended")
    quiz.question_count = len(quiz.questions)
    return quiz


@router.post("/quizzes/{quiz_id}/start", response_model=AttemptOut, status_code=201)
async def start_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id, Quiz.is_active == True, Quiz.quiz_type == QuizType.scheduled.value))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    now = now_ist()
    start = normalize_ist(quiz.scheduled_start)
    end = normalize_ist(quiz.scheduled_end)
    if start and now < start:
        raise HTTPException(403, {"message": "Quiz not started yet", "start_time": start.isoformat()})
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
            user_id=current_user.id, quiz_id=quiz_id,
            answers={}, started_at=to_naive(now),
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
    return AttemptOut(**enrich_attempt(attempt, quiz, current_user))


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

    quiz_r = await db.execute(select(Quiz).where(Quiz.id == attempt.quiz_id))
    quiz = quiz_r.scalar_one_or_none()
    q_result = await db.execute(
        select(Question).where(Question.quiz_id == attempt.quiz_id).order_by(Question.id)
    )
    questions = q_result.scalars().all()

    score = sum(1 for q in questions if data.answers.get(q.id) == q.correct_option)
    now = now_ist()

    attempt.answers = {str(k): v for k, v in data.answers.items()}
    attempt.score = score
    attempt.total = len(questions)
    attempt.submitted = True
    attempt.submitted_at = to_naive(now)
    await db.commit()
    await db.refresh(attempt)

    await manager.broadcast({
        "type": "quiz_submitted",
        "user": current_user.username,
        "quiz_id": attempt.quiz_id,
        "quiz_title": quiz.title if quiz else "",
        "difficulty": quiz.difficulty.value if quiz else "",
        "subject": quiz.subject if quiz else "",
        "attempt_id": attempt.id,
        "score": score,
        "total": len(questions),
        "ts": now.isoformat(),
    })

    return AttemptResult(
        **enrich_attempt(attempt, quiz, current_user),
        answers={str(k): v for k, v in attempt.answers.items()},
        questions=questions,
    )


@router.get("/results", response_model=List[AttemptOut])
async def my_results(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == current_user.id, QuizAttempt.submitted == True)
        .order_by(QuizAttempt.submitted_at.desc())
    )
    attempts = result.scalars().all()
    enriched = []
    for attempt in attempts:
        quiz_r = await db.execute(select(Quiz).where(Quiz.id == attempt.quiz_id))
        quiz = quiz_r.scalar_one_or_none()
        enriched.append(AttemptOut(**enrich_attempt(attempt, quiz, current_user)))
    return enriched


@router.get("/results/{attempt_id}", response_model=AttemptResult)
async def result_detail(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.submitted == True,
        )
    )
    attempt = result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(404, "Result not found")

    quiz_r = await db.execute(select(Quiz).where(Quiz.id == attempt.quiz_id))
    quiz = quiz_r.scalar_one_or_none()
    q_result = await db.execute(
        select(Question).where(Question.quiz_id == attempt.quiz_id).order_by(Question.id)
    )
    questions = q_result.scalars().all()

    return AttemptResult(
        **enrich_attempt(attempt, quiz, current_user),
        answers={str(k): v for k, v in attempt.answers.items()},
        questions=questions,
    )
