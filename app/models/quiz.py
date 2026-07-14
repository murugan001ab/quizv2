from datetime import datetime
from zoneinfo import ZoneInfo
import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


# Indian Standard Time
IST = ZoneInfo("Asia/Kolkata")


def now_ist():
    # Return IST without timezone info
    return datetime.now(IST).replace(tzinfo=None)


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuizType(str, enum.Enum):
    scheduled = "scheduled"  # self-paced, browsable/takeable by users within scheduled_start/scheduled_end
    live = "live"  # only ever run through a hosted Live Quiz channel — never shown to users directly


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)

    difficulty = Column(SAEnum(DifficultyLevel), nullable=False)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)

    # Plain string (not a native Postgres enum) so existing databases can pick
    # it up with a simple ADD COLUMN — see init_db() in database.py.
    quiz_type = Column(String, nullable=False, default=QuizType.scheduled.value, server_default=QuizType.scheduled.value)

    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=now_ist)

    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.id",
    )

    attempts = relationship(
        "QuizAttempt",
        back_populates="quiz",
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    quiz_id = Column(
        Integer,
        ForeignKey("quizzes.id"),
        nullable=False,
    )

    text = Column(Text, nullable=False)

    options = Column(JSON, nullable=False)

    correct_option = Column(Integer, nullable=False)

    explanation = Column(Text)

    year = Column(Text)

    quiz = relationship(
        "Quiz",
        back_populates="questions",
    )


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    quiz_id = Column(
        Integer,
        ForeignKey("quizzes.id"),
        nullable=False,
    )

    answers = Column(JSON, default=dict)

    score = Column(Integer, default=0)

    total = Column(Integer, default=0)

    submitted = Column(Boolean, default=False)

    started_at = Column(DateTime, default=now_ist)

    submitted_at = Column(DateTime, nullable=True)

    user = relationship(
        "User",
        back_populates="attempts",
    )

    quiz = relationship(
        "Quiz",
        back_populates="attempts",
    )