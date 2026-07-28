import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "")

if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://"):
    _raw_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = _raw_url

_connect_args = {}
if "sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    _connect_args = {"ssl": "require"}

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=_connect_args)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        from app.models import user, quiz, problem, discussion, saved_code  # noqa: registers models with Base
        await conn.run_sync(Base.metadata.create_all)
        # create_all only creates missing tables — it never ALTERs a table
        # that's already there. quiz_type was added after quizzes already
        # existed in deployed DBs, so patch it in here for anyone upgrading.
        await conn.execute(text(
            "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS quiz_type VARCHAR NOT NULL DEFAULT 'scheduled'"
        ))
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_url VARCHAR"
        ))
        # Per-problem language policy (see app/models/problem.py::Problem for
        # the allowed_languages / default_language semantics). Plain JSON +
        # VARCHAR, not a DB enum, so new Language members never need an
        # ALTER TYPE migration.
        await conn.execute(text(
            "ALTER TABLE problems ADD COLUMN IF NOT EXISTS allowed_languages JSON"
        ))
        await conn.execute(text(
            "ALTER TABLE problems ADD COLUMN IF NOT EXISTS default_language VARCHAR(20)"
        ))
        # submissions.language / saved_codes.language use a native Postgres
        # enum type (named after the Python class, lowercased: "language").
        # create_all() never alters an existing type, so new Language members
        # (java, c) need to be added to it explicitly for anyone upgrading.
        await conn.execute(text(
            "ALTER TYPE language ADD VALUE IF NOT EXISTS 'java'"
        ))
        await conn.execute(text(
            "ALTER TYPE language ADD VALUE IF NOT EXISTS 'c'"
        ))
