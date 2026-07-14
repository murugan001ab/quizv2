"""
Create sample users.

Usage:
    python seed_user.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.core.security import hash_password


SAMPLE_USERS = [
    {
        "name":"arun",
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "Test@123",
        "is_admin": False,
        "profile_url": None,
    },
    {
        "name":"krish",
        "username": "student",
        "email": "student@example.com",
        "password": "Student@123",
        "is_admin": False,
        "profile_url": None,
    },
]


async def seed_users():
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            for user_data in SAMPLE_USERS:
                result = await db.execute(
                    select(User).where(
                        User.username == user_data["username"]
                    )
                )

                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(
                        f"⚠️ User already exists: "
                        f"{user_data['email']}"
                    )
                    continue

                user = User(
                    name=user_data["name"],
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hash_password(
                        user_data["password"]
                    ),
                    is_admin=user_data["is_admin"],
                    profile_url=user_data["profile_url"],
                )

                db.add(user)

                print(
                    f"➕ Added user: {user_data['username']}"
                )

            await db.commit()

            print("✅ User seed completed!")

        except Exception as exc:
            await db.rollback()

            print(
                f"❌ User seed failed: {exc}"
            )

            raise


if __name__ == "__main__":
    asyncio.run(seed_users())