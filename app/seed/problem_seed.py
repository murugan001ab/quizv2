import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.models.problem import Topic

TOPICS = [
    ("Basics", "basics"),
    ("Data Types", "data-types"),
    ("Conditionals", "conditionals"),
    ("Loops", "loops"),
    ("Functions", "functions"),
    ("Strings", "strings"),
    ("Lists & Tuples", "lists-tuples"),
    ("Dictionaries & Sets", "dicts-sets"),
    ("OOP", "oop"),
    ("Exception Handling", "exception-handling"),
]

async def seed_topics():
    await init_db()

    async with AsyncSessionLocal() as db:
        for i, (name, slug) in enumerate(TOPICS):

            result = await db.execute(
                select(Topic).where(Topic.slug == slug)
            )

            topic = result.scalar_one_or_none()

            if topic is None:
                db.add(
                    Topic(
                        name=name,
                        slug=slug,
                        order_index=i
                    )
                )

        await db.commit()

    print(f"Seeded {len(TOPICS)} topics.")

if __name__ == "__main__":
    asyncio.run(seed_topics())