from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.database import get_db
from app.models.quiz import Quiz, Question, QuizAttempt, now_ist
from app.models.user import User
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizOut, QuizDetail,AdminQuizDetail,
    QuestionCreate, QuestionOut, QuestionOutWithAnswer,
    AttemptOut
)
from app.schemas.user import UserOut
from app.core.security import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Users ─────────────────────────────────────────────────
@router.get("/users", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar()
    total_quizzes = (await db.execute(select(func.count(Quiz.id)))).scalar()
    total_attempts = (await db.execute(select(func.count(QuizAttempt.id)))).scalar()
    # "Live" = started but not submitted, AND the quiz hasn't ended.
    # Without the quiz-end check, an attempt abandoned mid-quiz (tab closed,
    # browser crash, etc.) stays "submitted=False" forever and would
    # permanently inflate this count.
    now = now_ist()
    active_attempts = (await db.execute(
        select(func.count(QuizAttempt.id))
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .where(
            QuizAttempt.submitted == False,
            or_(Quiz.scheduled_end.is_(None), Quiz.scheduled_end >= now),
        )
    )).scalar()
    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "live_takers": active_attempts,
    }


@router.get("/attempts", response_model=List[AttemptOut])
async def all_attempts(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    """Most recent attempts across every quiz (not just a handful of
    quizzes), newest submissions first. Fixes the dashboard's old approach
    of only checking the first 5 quizzes returned by list_quizzes (which
    has no ORDER BY, so it isn't the same as "most recently active
    quizzes") — that meant quizzes created later, even if heavily attempted,
    never showed up in "Recent Attempts".
    """
    result = await db.execute(
        select(QuizAttempt)
        .order_by(QuizAttempt.submitted_at.desc().nullslast(), QuizAttempt.started_at.desc())
        .limit(limit)
    )
    attempts = result.scalars().all()

    enriched = []
    for a in attempts:
        quiz_r = await db.execute(select(Quiz).where(Quiz.id == a.quiz_id))
        quiz = quiz_r.scalar_one_or_none()
        user_r = await db.execute(select(User).where(User.id == a.user_id))
        user = user_r.scalar_one_or_none()
        enriched.append(AttemptOut(
            id=a.id, quiz_id=a.quiz_id, user_id=a.user_id,
            score=a.score, total=a.total, submitted=a.submitted,
            started_at=a.started_at, submitted_at=a.submitted_at,
            quiz_title=quiz.title if quiz else None,
            difficulty=quiz.difficulty.value if quiz else None,
            user=UserOut.model_validate(user) if user else None,
        ))
    return enriched


@router.get("/live", response_model=List[AttemptOut])
async def live_attempts(db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    """Currently in-progress attempts (started, not yet submitted, quiz not
    ended). Lets the Live Monitor show who's attending right now on load /
    reconnect, instead of only reacting to events broadcast during the
    current browser session."""
    now = now_ist()
    result = await db.execute(
        select(QuizAttempt)
        .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
        .where(
            QuizAttempt.submitted == False,
            or_(Quiz.scheduled_end.is_(None), Quiz.scheduled_end >= now),
        )
        .order_by(QuizAttempt.started_at.desc())
    )
    attempts = result.scalars().all()

    enriched = []
    for a in attempts:
        quiz_r = await db.execute(select(Quiz).where(Quiz.id == a.quiz_id))
        quiz = quiz_r.scalar_one_or_none()
        user_r = await db.execute(select(User).where(User.id == a.user_id))
        user = user_r.scalar_one_or_none()
        enriched.append(AttemptOut(
            id=a.id, quiz_id=a.quiz_id, user_id=a.user_id,
            score=a.score, total=a.total, submitted=a.submitted,
            started_at=a.started_at, submitted_at=a.submitted_at,
            quiz_title=quiz.title if quiz else None,
            difficulty=quiz.difficulty.value if quiz else None,
            user=UserOut.model_validate(user) if user else None,
        ))
    return enriched


# ── Quiz CRUD ─────────────────────────────────────────────
@router.post("/quizzes", response_model=QuizOut, status_code=201)
async def create_quiz(data: QuizCreate, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    quiz = Quiz(**data.model_dump())
    db.add(quiz)
    await db.commit()
    await db.refresh(quiz)
    quiz.question_count = 0
    return quiz


@router.get("/quizzes", response_model=List[QuizOut])
async def list_quizzes(
    difficulty: Optional[str] = None,
    subject: Optional[str] = None,
    quiz_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user)
):
    q = select(Quiz)
    if difficulty:
        q = q.where(Quiz.difficulty == difficulty)
    if subject:
        q = q.where(Quiz.subject == subject)
    if quiz_type:
        q = q.where(Quiz.quiz_type == quiz_type)
    result = await db.execute(q)
    quizzes = result.scalars().all()
    for quiz in quizzes:
        count = (await db.execute(
            select(func.count(Question.id)).where(Question.quiz_id == quiz.id)
        )).scalar()
        quiz.question_count = count
    return quizzes


@router.get("/quizzes/{quiz_id}", response_model=AdminQuizDetail)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user)
):
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions))
        .where(Quiz.id == quiz_id)
    )

    quiz = result.scalar_one_or_none()

    if not quiz:
        raise HTTPException(404, "Quiz not found")

    quiz.question_count = len(quiz.questions)

    return quiz


@router.put("/quizzes/{quiz_id}", response_model=QuizOut)
async def update_quiz(quiz_id: int, data: QuizUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(quiz, field, value)
    await db.commit()
    await db.refresh(quiz)
    count = (await db.execute(
        select(func.count(Question.id)).where(Question.quiz_id == quiz_id)
    )).scalar()
    quiz.question_count = count
    return quiz


@router.delete("/quizzes/{quiz_id}", status_code=204)
async def delete_quiz(quiz_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    await db.delete(quiz)
    await db.commit()


# ── Question CRUD ─────────────────────────────────────────
@router.post("/quizzes/{quiz_id}/questions", response_model=QuestionOutWithAnswer, status_code=201)
async def add_question(quiz_id: int, data: QuestionCreate, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Quiz not found")
    if len(data.options) != 4:
        raise HTTPException(400, "Exactly 4 options required")
    if data.correct_option not in range(4):
        raise HTTPException(400, "correct_option must be 0-3")
    q = Question(quiz_id=quiz_id, **data.model_dump())
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return q


@router.put("/questions/{question_id}", response_model=QuestionOutWithAnswer)
async def update_question(question_id: int, data: QuestionCreate, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(404, "Question not found")
    for field, value in data.model_dump().items():
        setattr(q, field, value)
    await db.commit()
    await db.refresh(q)
    return q


@router.delete("/questions/{question_id}", status_code=204)
async def delete_question(question_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(Question).where(Question.id == question_id))
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(404, "Question not found")
    await db.delete(q)
    await db.commit()


# ── Attempt monitoring ────────────────────────────────────
@router.get("/quizzes/{quiz_id}/attempts", response_model=List[AttemptOut])
async def quiz_attempts(quiz_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id))
    attempts = result.scalars().all()
    # Enrich with quiz info
    quiz_r = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = quiz_r.scalar_one_or_none()
    enriched = []
    for a in attempts:
        user_r = await db.execute(select(User).where(User.id == a.user_id))
        user = user_r.scalar_one_or_none()
        enriched.append(AttemptOut(
            id=a.id, quiz_id=a.quiz_id, user_id=a.user_id,
            score=a.score, total=a.total, submitted=a.submitted,
            started_at=a.started_at, submitted_at=a.submitted_at,
            quiz_title=quiz.title if quiz else None,
            difficulty=quiz.difficulty.value if quiz else None,
            user=UserOut.model_validate(user) if user else None,
        ))
    return enriched
