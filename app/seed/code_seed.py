"""
Create sample coding problems and test cases.

Usage:
    python seed_problem.py
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models.problem import Problem, TestCase, Difficulty


SAMPLE_PROBLEMS = [{
    "title": "Perfect Number",
    "slug": "perfect-number",
    "description": """
# Perfect Number

Write a program to check whether a given positive integer is a Perfect Number.

A Perfect Number is a positive integer that is equal to the sum of its proper positive divisors (excluding itself).

For example:

6 = 1 + 2 + 3

So, 6 is a Perfect Number.

Print:

- Perfect, if the number is a Perfect Number.
- Not Perfect, otherwise.

## Input

The input consists of a single integer N.

## Output

Print either:

Perfect

or

Not Perfect

## Example

Input
6

Output
Perfect
""",
    "constraints": """
1 <= N <= 100000
""",
    "starter_code": """n = int(input())

# Write your code below

""",
    "difficulty": Difficulty.BASIC,
    "topic_id": 1,
    "created_by": 1,
    "password": "perfect123",
    "test_cases": [

        # -------------------------
        # Visible Test Cases
        # -------------------------

        {
            "input": "6",
            "expected_output": "Perfect",
            "is_hidden": False,
            "order_index": 1,
            "points": 10,
        },
        {
            "input": "28",
            "expected_output": "Perfect",
            "is_hidden": False,
            "order_index": 2,
            "points": 10,
        },
        {
            "input": "10",
            "expected_output": "Not Perfect",
            "is_hidden": False,
            "order_index": 3,
            "points": 10,
        },

        # -------------------------
        # Hidden Test Cases
        # -------------------------

        {
            "input": "1",
            "expected_output": "Not Perfect",
            "is_hidden": True,
            "order_index": 4,
            "points": 10,
        },
        {
            "input": "2",
            "expected_output": "Not Perfect",
            "is_hidden": True,
            "order_index": 5,
            "points": 10,
        },
        {
            "input": "12",
            "expected_output": "Not Perfect",
            "is_hidden": True,
            "order_index": 6,
            "points": 10,
        },
        {
            "input": "496",
            "expected_output": "Perfect",
            "is_hidden": True,
            "order_index": 7,
            "points": 10,
        },
        {
            "input": "8128",
            "expected_output": "Perfect",
            "is_hidden": True,
            "order_index": 8,
            "points": 10,
        },
        {
            "input": "100",
            "expected_output": "Not Perfect",
            "is_hidden": True,
            "order_index": 9,
            "points": 10,
        },
        {
            "input": "9999",
            "expected_output": "Not Perfect",
            "is_hidden": True,
            "order_index": 10,
            "points": 10,
        },
    ],
},]

async def seed_problems():
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            for problem_data in SAMPLE_PROBLEMS:
                # Check if problem already exists by slug
                result = await db.execute(
                    select(Problem).where(
                        Problem.slug == problem_data["slug"]
                    )
                )

                existing_problem = result.scalar_one_or_none()

                if existing_problem:
                    print(
                        f"⚠️ Problem already exists: {problem_data['slug']}"
                    )
                    continue

                # Prepare test cases data
                test_cases_data = problem_data.pop("test_cases", [])
                plain_password = problem_data.pop("password", None)

                # Create Problem instance
                problem = Problem(
                    title=problem_data["title"],
                    slug=problem_data["slug"],
                    description=problem_data["description"],
                    constraints=problem_data["constraints"],
                    starter_code=problem_data["starter_code"],
                    difficulty=problem_data["difficulty"],
                    topic_id=problem_data["topic_id"],
                    created_by=problem_data["created_by"],
                    access_password_hash=(
                        hash_password(plain_password) if plain_password else None
                    ),
                )

                db.add(problem)
                
                # Flush session asynchronously to generate problem.id
                await db.flush()

                # Instantiate and attach test cases
                test_cases = [
                    TestCase(
                        problem_id=problem.id,
                        input=tc["input"],
                        expected_output=tc["expected_output"],
                        is_hidden=tc["is_hidden"],
                        order_index=tc["order_index"],
                        points=tc["points"],
                    )
                    for tc in test_cases_data
                ]

                db.add_all(test_cases)

                print(f"➕ Added problem: {problem.title} (ID: {problem.id})")

            await db.commit()

            print("✅ Problem seed completed!")

        except Exception as exc:
            await db.rollback()

            print(f"❌ Problem seed failed: {exc}")

            raise


if __name__ == "__main__":
    asyncio.run(seed_problems())