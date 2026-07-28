"""
A single autosave/manual-save slot per (user, problem) — lets a user save
their in-progress code and come back to it later, independent of formal
Submissions (which are only created on Submit).
"""

from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.problem import Language


class SavedCode(Base):
    __tablename__ = "saved_codes"
    __table_args__ = (UniqueConstraint("user_id", "problem_id", name="uq_saved_code_user_problem"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), nullable=False, index=True)

    code: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Language] = mapped_column(SAEnum(Language), default=Language.PYTHON3)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
