from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import auth, admin, user, ws
from core.security import hash_password
from models.user import User
from database import AsyncSessionLocal
from sqlalchemy import select

app = FastAPI(
    title="Quiz App",
    description="MCQ Quiz platform with Admin & User panels + WebSocket live monitoring",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(ws.router)


@app.on_event("startup")
async def startup():
    await init_db()
    # Create default admin if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if not result.scalar_one_or_none():
            admin_user = User(
                username="admin",
                email="admin@quiz.com",
                hashed_password=hash_password("admin123"),
                is_admin=True,
            )
            db.add(admin_user)
            await db.commit()
            print("✅ Default admin created: admin / admin123")


@app.get("/")
async def root():
    return {
        "message": "Quiz App API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
