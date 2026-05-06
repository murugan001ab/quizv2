"""
Run once to populate sample quizzes and questions.
Usage:  python seed.py
"""
import asyncio
from app.database import AsyncSessionLocal, init_db
from app.models.quiz import Quiz, Question, DifficultyLevel
from datetime import datetime, timedelta


SAMPLE_QUIZZES = [
     {
        "title": "இந்திய வரலாறு – கடினம்",
        "description": "உயர் நிலை கேள்விகள்",
        "difficulty": DifficultyLevel.hard,
        "subject": "History",
        "topic": "Indian History",
        "scheduled_start": datetime.utcnow(),
        "scheduled_end": datetime.utcnow() + timedelta(days=7),
        "questions":[
    {
        "text": "முகலாய பேரரசை இந்தியாவில் நிறுவியவர் யார்?",
        "options": ["அக்பர்", "பாபர்", "ஹுமாயூன்", "ஷாஜகான்"],
        "correct_option": 1,
        "explanation": "1526 ஆம் ஆண்டு பாபர் முகலாய பேரரசை நிறுவினார்.",
        "year": "TNPSC 2019"
    },
    {
        "text": "பானிபட் முதல் போர் நடைபெற்ற ஆண்டு எது?",
        "options": ["1526", "1556", "1761", "1707"],
        "correct_option": 0,
        "explanation": "1526 இல் பானிபட் முதல் போர் நடைபெற்றது.",
        "year": "TNPSC 2020"
    },
    {
        "text": "தின்-இ-இலாஹி என்ற மதத்தை உருவாக்கியவர் யார்?",
        "options": ["பாபர்", "ஹுமாயூன்", "அக்பர்", "ஔரங்கசீப்"],
        "correct_option": 2,
        "explanation": "அக்பர் தின்-இ-இலாஹி மதத்தை அறிமுகப்படுத்தினார்.",
        "year": "TNPSC 2018"
    },
    {
        "text": "தாஜ்மஹாலை கட்டிய முகலாய அரசர் யார்?",
        "options": ["அக்பர்", "பாபர்", "ஷாஜகான்", "ஹுமாயூன்"],
        "correct_option": 2,
        "explanation": "ஷாஜகான் தனது மனைவி மும்தாஜ் நினைவாக தாஜ்மஹாலை கட்டினார்.",
        "year": "TNPSC 2017"
    },
    {
        "text": "அக்பரின் அரண்மனை வரலாற்றாசிரியர் யார்?",
        "options": ["அபுல் ஃபஸ்ல்", "பீர்பால்", "தான்சேன்", "பதாயூனி"],
        "correct_option": 0,
        "explanation": "அபுல் ஃபஸ்ல் அக்பர்நாமாவை எழுதினார்.",
        "year": "TNPSC 2021"
    },
    {
        "text": "முகலாயர்களின் ஆட்சி மொழி எது?",
        "options": ["தமிழ்", "பாரசீகம்", "இந்தி", "அரபு"],
        "correct_option": 1,
        "explanation": "பாரசீகம் முகலாய ஆட்சிமொழியாக இருந்தது.",
        "year": "TNPSC 2016"
    },
    {
        "text": "பதேபூர் சிக்ரி நகரை கட்டியவர் யார்?",
        "options": ["பாபர்", "அக்பர்", "ஷாஜகான்", "ஔரங்கசீப்"],
        "correct_option": 1,
        "explanation": "அக்பர் பதேபூர் சிக்ரியை கட்டினார்.",
        "year": "TNPSC 2019"
    },
    {
        "text": "மயில் சிம்மாசனத்தை உருவாக்கியவர் யார்?",
        "options": ["அக்பர்", "ஷாஜகான்", "பாபர்", "ஹுமாயூன்"],
        "correct_option": 1,
        "explanation": "மயில் சிம்மாசனம் ஷாஜகானால் உருவாக்கப்பட்டது.",
        "year": "TNPSC 2022"
    },
    {
        "text": "முகலாய பேரரசின் உண்மையான நிறுவனர் யார்?",
        "options": ["பாபர்", "அக்பர்", "ஹுமாயூன்", "ஷாஜகான்"],
        "correct_option": 1,
        "explanation": "அக்பர் முகலாய பேரரசை வலுப்படுத்தினார்.",
        "year": "TNPSC 2015"
    },
    {
        "text": "இசையைத் தடை செய்த முகலாய அரசர் யார்?",
        "options": ["அக்பர்", "ஷாஜகான்", "ஔரங்கசீப்", "பாபர்"],
        "correct_option": 2,
        "explanation": "ஔரங்கசீப் இசைக்கு தடை விதித்தார்.",
        "year": "TNPSC 2020"
    },

    {
        "text": "ஹுமாயூனுக்கு உதவிய பாரசீக அரசர் யார்?",
        "options": ["ஷா தஹ்மாஸ்ப்", "நாதிர்ஷா", "அக்பர்", "பாபர்"],
        "correct_option": 0,
        "explanation": "ஷா தஹ்மாஸ்ப் ஹுமாயூனுக்கு உதவி செய்தார்.",
        "year": "TNPSC 2018"
    },
    {
        "text": "அக்பரின் வரி முறையை அமைத்தவர் யார்?",
        "options": ["தோடர்மால்", "பீர்பால்", "தான்சேன்", "அபுல் ஃபஸ்ல்"],
        "correct_option": 0,
        "explanation": "தோடர்மால் நிலவரி முறையை சீரமைத்தார்.",
        "year": "TNPSC 2019"
    },
    {
        "text": "முகலாய ஓவியக்கலையை ஊக்குவித்தவர் யார்?",
        "options": ["அக்பர்", "ஔரங்கசீப்", "இப்ராஹிம் லோடி", "ஷேர் ஷா"],
        "correct_option": 0,
        "explanation": "அக்பர் ஓவியக்கலையை ஊக்குவித்தார்.",
        "year": "TNPSC 2021"
    },
    {
        "text": "பானிபட் இரண்டாம் போர் நடைபெற்ற ஆண்டு?",
        "options": ["1526", "1556", "1761", "1707"],
        "correct_option": 1,
        "explanation": "1556 இல் நடைபெற்றது.",
        "year": "TNPSC 2017"
    },
    {
        "text": "அக்பரின் பாதுகாவலர் யார்?",
        "options": ["பீர்பால்", "பைரம் கான்", "தோடர்மால்", "அபுல் ஃபஸ்ல்"],
        "correct_option": 1,
        "explanation": "பைரம் கான் அக்பரின் பாதுகாவலர்.",
        "year": "TNPSC 2022"
    },
    {
        "text": "அக்பரின் அரண்மனையில் இருந்த இசைக்கலைஞர் யார்?",
        "options": ["தான்சேன்", "பீர்பால்", "அபுல் ஃபஸ்ல்", "தோடர்மால்"],
        "correct_option": 0,
        "explanation": "தான்சேன் பிரபல இசைக்கலைஞர்.",
        "year": "TNPSC 2016"
    },
    {
        "text": "முகலாயர்களில் கடைசி வலுவான பேரரசர் யார்?",
        "options": ["அக்பர்", "ஔரங்கசீப்", "பாபர்", "பஹதூர் ஷா"],
        "correct_option": 1,
        "explanation": "ஔரங்கசீப் கடைசி வலுவான முகலாய அரசர்.",
        "year": "TNPSC 2020"
    },
    {
        "text": "அக்பர்நாமா எழுதியவர் யார்?",
        "options": ["அபுல் ஃபஸ்ல்", "பீர்பால்", "தான்சேன்", "பதாயூனி"],
        "correct_option": 0,
        "explanation": "அபுல் ஃபஸ்ல் எழுதியார்.",
        "year": "TNPSC 2019"
    },
    {
        "text": "ஜகங்கீர் காலத்தில் இந்தியா வந்த ஆங்கிலேயர் யார்?",
        "options": ["தாமஸ் ரோ", "வாஸ்கோடகாமா", "கிளைவ்", "ஹாக்கின்ஸ்"],
        "correct_option": 0,
        "explanation": "சர் தாமஸ் ரோ ஜகங்கீர் காலத்தில் வந்தார்.",
        "year": "TNPSC 2021"
    },
    {
        "text": "சிவப்பு கோட்டை அமைத்தவர் யார்?",
        "options": ["அக்பர்", "ஷாஜகான்", "ஔரங்கசீப்", "பாபர்"],
        "correct_option": 1,
        "explanation": "டெல்லி சிவப்பு கோட்டை ஷாஜகானால் கட்டப்பட்டது.",
        "year": "TNPSC 2018"
    }

    # Continue same pattern up to 50
]
    },

]
async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        for qz_data in SAMPLE_QUIZZES:
            questions_data = qz_data.pop("questions")
            quiz = Quiz(**qz_data)
            db.add(quiz)
            await db.flush()
            for q_data in questions_data:
                db.add(Question(quiz_id=quiz.id, **q_data))
        await db.commit()
        print("✅ Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())
