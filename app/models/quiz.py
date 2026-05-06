from datetime import datetime
from zoneinfo import ZoneInfo
import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Enum as SAEnum, Text, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base

IST = ZoneInfo("Asia/Kolkata")


def now_ist_naive():
    return datetime.now(IST).replace(tzinfo=None)


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    difficulty = Column(SAEnum(DifficultyLevel), nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=now_ist_naive)

    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_option = Column(Integer, nullable=False)
    explanation = Column(Text)
    year = Column(Text)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    answers = Column(JSON, default={})
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)
    submitted = Column(Boolean, default=False)
    started_at = Column(DateTime, default=now_ist_naive)
    submitted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="attempts")
    quiz = relationship("Quiz", back_populates="attempts")
