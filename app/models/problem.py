"""
Models for the coding-problem module (HackerRank-style practice/quiz platform).

ASSUMPTIONS (adjust imports if yours differ):
- `app/database.py` exposes a SQLAlchemy declarative `Base`.
- `app/models/user.py` defines a `User` model with integer PK `id`.
- You're on SQLAlchemy 2.x style (Mapped / mapped_column). If you're on 1.x
  Column-style, swap accordingly — the shape is the same.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Enum as SAEnum,
    DateTime,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Difficulty(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Language(str, enum.Enum):
    PYTHON3 = "python3"
    # add more later (cpp, java, js...) — keep in sync with judge0_client LANGUAGE_MAP


class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    COMPILE_ERROR = "compile_error"
    ERROR = "error"


class Topic(Base):
    """e.g. Basics, Data Types, Conditionals, Loops, Functions, OOP"""

    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    problems: Mapped[list["Problem"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # markdown
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    starter_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    difficulty: Mapped[Difficulty] = mapped_column(
        SAEnum(Difficulty), default=Difficulty.BASIC, nullable=False
    )
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)

    time_limit_ms: Mapped[int] = mapped_column(Integer, default=2000)
    memory_limit_kb: Mapped[int] = mapped_column(Integer, default=65536)

    # Optional per-problem password gate (e.g. for a contest / classroom drop).
    # Stored hashed — never plaintext. Nullable => open problem, no gate.
    access_password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    topic: Mapped["Topic"] = relationship(back_populates="problems")
    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan", order_by="TestCase.order_index"
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan"
    )

    @property
    def is_locked(self) -> bool:
        return self.access_password_hash is not None


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)

    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)

    # False => shown to the user on the problem page (your "2 visible")
    # True  => used only during Submit, never returned to the client (your "3 hidden")
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    points: Mapped[int] = mapped_column(Integer, default=1)

    problem: Mapped["Problem"] = relationship(back_populates="test_cases")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)

    language: Mapped[Language] = mapped_column(SAEnum(Language), default=Language.PYTHON3)
    code: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[SubmissionStatus] = mapped_column(
        SAEnum(SubmissionStatus), default=SubmissionStatus.PENDING
    )
    score: Mapped[int] = mapped_column(Integer, default=0)
    max_score: Mapped[int] = mapped_column(Integer, default=0)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Per-test-case results, hidden test case bodies are NEVER stored here
    # in a way that's exposed for hidden cases — see schemas for redaction.
    # shape: [{ "test_case_id": 1, "is_hidden": false, "passed": true,
    #           "stdout": "...", "expected": "...", "time_ms": 12 }, ...]
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    problem: Mapped["Problem"] = relationship(back_populates="submissions")


class ProblemUnlock(Base):
    """Records that a user has successfully entered a problem's password."""

    __tablename__ = "problem_unlocks"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", name="uq_user_problem_unlock"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
