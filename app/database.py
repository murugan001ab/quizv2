import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "")

# Fix: Aiven (and Heroku) give `postgres://` — SQLAlchemy needs `postgresql+asyncpg://`
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif _raw_url.startswith("postgresql://"):
    _raw_url = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

DATABASE_URL = _raw_url

# Aiven requires SSL — pass connect_args for asyncpg
_connect_args = {}
if "sslmode=require" in DATABASE_URL:
    # asyncpg doesn't use sslmode= query param, strip it and pass ssl directly
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    _connect_args = {"ssl": "require"}

engine = create_async_engine(DATABASE_URL, echo=True, connect_args=_connect_args)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        from models import user, quiz  # noqa
        await conn.run_sync(Base.metadata.create_all)
