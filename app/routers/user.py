from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime
from typing import List, Optional

from database import get_db
from models.quiz import Quiz, Question, QuizAttempt
from models.user import User
from schemas.quiz import QuizOut, QuizDetail, SubmitAnswers, AttemptOut, AttemptResult
from core.security import get_current_user
from ws_manager import manager

router = APIRouter(prefix="/user", tags=["User"])


# ── Available quizzes ──────────────────────────────────────
@router.get("/quizzes", response_model=List[QuizOut])
async def available_quizzes(
    difficulty: Optional[str] = None,
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = select(Quiz).where(Quiz.is_active == True)

    if difficulty:
        q = q.where(Quiz.difficulty == difficulty)
    if subject:
        q = q.where(Quiz.subject == subject)

    result = await db.execute(q)
    quizzes = result.scalars().all()

    for quiz in quizzes:
        count_result = await db.execute(
            select(func.count(Question.id)).where(Question.quiz_id == quiz.id)
        )
        quiz.question_count = count_result.scalar()

    return quizzes


# ── Get quiz with questions ──────────────────────────────────
@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id, Quiz.is_active == True)
    )

    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    now = datetime.utcnow()

    if quiz.scheduled_start and now < quiz.scheduled_start:
        raise HTTPException(403, f"Quiz starts at {quiz.scheduled_start}")

    if quiz.scheduled_end and now > quiz.scheduled_end:
        raise HTTPException(403, "Quiz time has ended")

    quiz.question_count = len(quiz.questions)
    return quiz


# ── Start attempt ─────────────────────────────────────────
@router.post("/quizzes/{quiz_id}/start", response_model=AttemptOut, status_code=201)
async def start_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    now = datetime.utcnow()

    if quiz.scheduled_start and now < quiz.scheduled_start:
        raise HTTPException(403, f"Quiz starts at {quiz.scheduled_start}")

    if quiz.scheduled_end and now > quiz.scheduled_end:
        raise HTTPException(403, "Quiz time has ended")

    existing = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.submitted == False
        )
    )
    attempt = existing.scalar_one_or_none()

    if attempt:
        return attempt

    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        answers={}
    )

    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    # 📡 Broadcast — field names aligned with frontend expectations
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

    return attempt


# ── Submit attempt ────────────────────────────────────────
@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResult)
async def submit_quiz(
    attempt_id: int,
    data: SubmitAnswers,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.user_id == current_user.id
        )
    )
    attempt = result.scalar_one_or_none()

    if not attempt:
        raise HTTPException(404, "Attempt not found")

    if attempt.submitted:
        raise HTTPException(400, "Already submitted")

    # Load quiz for title + difficulty
    quiz_result = await db.execute(
        select(Quiz).where(Quiz.id == attempt.quiz_id)
    )
    quiz = quiz_result.scalar_one_or_none()

    q_result = await db.execute(
        select(Question).where(Question.quiz_id == attempt.quiz_id)
    )
    questions = q_result.scalars().all()

    score = 0
    for q in questions:
        chosen = data.answers.get(q.id)
        if chosen is not None and chosen == q.correct_option:
            score += 1

    attempt.answers = {str(k): v for k, v in data.answers.items()}
    attempt.score = score
    attempt.total = len(questions)
    attempt.submitted = True
    attempt.submitted_at = datetime.utcnow()

    await db.commit()
    await db.refresh(attempt)

    # 📡 Broadcast — field names aligned with frontend expectations
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
        "ts": attempt.submitted_at.isoformat(),
    })

    return AttemptResult(
        **AttemptOut.model_validate(attempt).model_dump(),
        answers={int(k): v for k, v in attempt.answers.items()},
        questions=questions
    )


# ── Results list ───────────────────────────────────────────
@router.get("/results", response_model=List[AttemptOut])
async def my_results(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.user_id == current_user.id,
            QuizAttempt.submitted == True
        )
    )
    return result.scalars().all()


# ── Result detail ──────────────────────────────────────────
@router.get("/results/{attempt_id}", response_model=AttemptResult)
async def result_detail(
    attempt_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(QuizAttempt).where(
            QuizAttempt.id == attempt_id,
            QuizAttempt.user_id == current_user.id
        )
    )
    attempt = result.scalar_one_or_none()

    if not attempt or not attempt.submitted:
        raise HTTPException(404, "Result not found")

    q_result = await db.execute(
        select(Question).where(Question.quiz_id == attempt.quiz_id)
    )
    questions = q_result.scalars().all()

    return AttemptResult(
        **AttemptOut.model_validate(attempt).model_dump(),
        answers={int(k): v for k, v in attempt.answers.items()},
        questions=questions
    )
