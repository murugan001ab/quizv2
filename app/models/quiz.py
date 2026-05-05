import enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    Enum as SAEnum, Text, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


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
    subject = Column(String, nullable=False)   # e.g. Tamil, Science, Physics, Maths
    topic = Column(String, nullable=False)      # sub-topic within subject
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)      # list of 4 strings
    correct_option = Column(Integer, nullable=False)  # index 0-3
    explanation = Column(Text)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    answers = Column(JSON, default={})          # {question_id: chosen_option}
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)
    submitted = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="attempts")
    quiz = relationship("Quiz", back_populates="attempts")
