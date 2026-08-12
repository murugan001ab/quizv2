"""
Local cache of LeetCode problems an admin has looked up/imported, so
re-opening the same problem later doesn't re-hit the LeetCode GraphQL API.
Populated by app/routers/admin_leetcode.py; not user-facing.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LeetCodeProblem(Base):
    __tablename__ = "leetcode_problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    title_slug: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(20))
    paid_only: Mapped[bool] = mapped_column(Boolean, default=False)
    topics: Mapped[list | None] = mapped_column(JSON)

    # Full problem data (fetched lazily, on first import click)
    content: Mapped[str | None] = mapped_column(Text)  # raw HTML from LeetCode
    # NOTE: named `question_metadata`, not `metadata` — `metadata` is a
    # reserved attribute name on every SQLAlchemy declarative Base subclass
    # (it's the schema/table registry), so a column literally named that
    # raises InvalidRequestError at import time.
    question_metadata: Mapped[dict | None] = mapped_column(JSON)
    code_snippets: Mapped[list | None] = mapped_column(JSON)
    example_testcases: Mapped[list | None] = mapped_column(JSON)
    hints: Mapped[list | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
