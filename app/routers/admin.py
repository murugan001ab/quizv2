from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from database import get_db
from models.quiz import Quiz, Question, QuizAttempt
from models.user import User
from schemas.quiz import (
    QuizCreate, QuizUpdate, QuizOut, QuizDetail,
    QuestionCreate, QuestionOut, QuestionOutWithAnswer,
    AttemptOut
)
from schemas.user import UserOut
from core.security import get_admin_user

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Users ─────────────────────────────────────────────────
@router.get("/users", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    total_users = (await db.execute(func.count(User.id))).scalar()
    total_quizzes = (await db.execute(func.count(Quiz.id))).scalar()
    total_attempts = (await db.execute(func.count(QuizAttempt.id))).scalar()
    active_attempts = (await db.execute(
        select(func.count(QuizAttempt.id)).where(QuizAttempt.submitted == False)
    )).scalar()
    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "active_test_takers": active_attempts,
    }


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
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user)
):
    q = select(Quiz)
    if difficulty:
        q = q.where(Quiz.difficulty == difficulty)
    if subject:
        q = q.where(Quiz.subject == subject)
    result = await db.execute(q)
    quizzes = result.scalars().all()
    for quiz in quizzes:
        count = (await db.execute(
            select(func.count(Question.id)).where(Question.quiz_id == quiz.id)
        )).scalar()
        quiz.question_count = count
    return quizzes


@router.get("/quizzes/{quiz_id}", response_model=QuizDetail)
async def get_quiz(quiz_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_admin_user)):
    result = await db.execute(select(Quiz).where(Quiz.id == quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    q_result = await db.execute(select(Question).where(Question.quiz_id == quiz_id))
    questions = q_result.scalars().all()
    quiz.question_count = len(questions)
    quiz.questions = questions
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
    return result.scalars().all()
