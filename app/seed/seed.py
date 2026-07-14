"""
Run once to populate sample quizzes and questions.
Usage:
    python seed.py
"""

import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from app.database import AsyncSessionLocal, init_db
from app.models.quiz import Quiz, Question, DifficultyLevel

load_dotenv()

IST = ZoneInfo("Asia/Kolkata")


def now_ist():
    # Return timezone-naive IST datetime
    return datetime.now(IST).replace(tzinfo=None)


SAMPLE_QUIZZES = [
    {
        "title": "இந்திய வரலாறு – கடினம்",
        "description": "mugals qution 50",
        "difficulty": DifficultyLevel.hard,
        "subject": "History",
        "topic": "mugals",
        "scheduled_start": now_ist(),
        "scheduled_end": now_ist() + timedelta(days=7),
        "questions": [
            {
                "text": "பொருத்துக:\n(a) கிருஷ்ணதேவராயர்\n(b) இரண்டாம் தேவராயர்\n(c) குமார கம்பணா\n(d) ராமராயர்\n1. மதுரை வெற்றி\n2. தலைக்கோட்டை போர்\n3. முஸ்லிம் வீரர்கள் சேர்த்தல்\n4. அமுக்தமால்யதா",
                "options": [
                    "4 3 1 2",
                    "3 4 2 1",
                    "4 1 2 3",
                    "2 3 1 4"
                ],
                "correct_option": 0,
                "explanation": "கிருஷ்ணதேவராயர் – அமுக்தமால்யதா; இரண்டாம் தேவராயர் – முஸ்லிம் வீரர்கள்; குமார கம்பணா – மதுரை; ராமராயர் – தலைக்கோட்டை.",
                "year": "TNPSC Group 2"
            },
            {
                "text": "விஜயநகர அரசில் உள்ளூர் நிர்வாகத்தில் முக்கிய பங்கு வகித்தது எது?",
                "options": [
                    "கிராம சபை",
                    "முகலாய ஆளுநர்",
                    "ஐரோப்பிய வணிகர்",
                    "சுல்தான்"
                ],
                "correct_option": 0,
                "explanation": "கிராம நிர்வாகம் உள்ளூர் அமைப்புகள் மூலம் நடைபெற்றது.",
                "year": "TNPSC Group 4"
            }

            # 👇 Paste the remaining questions exactly as they are...
        ]
    }
]


async def seed():
    await init_db()

    async with AsyncSessionLocal() as db:
        try:
            for quiz_data in SAMPLE_QUIZZES:
                data = quiz_data.copy()

                questions = data.pop("questions")

                quiz = Quiz(**data)

                db.add(quiz)

                await db.flush()

                for question in questions:
                    db.add(
                        Question(
                            quiz_id=quiz.id,
                            **question
                        )
                    )

            await db.commit()
            print("✅ Seed completed successfully!")

        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed())