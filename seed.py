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
        "title": "இந்திய வரலாறு – எளியது",
        "description": "அடிப்படை TNPSC கேள்விகள்",
        "difficulty": DifficultyLevel.easy,
        "subject": "History",
        "topic": "Indian History",
        "scheduled_start": datetime.utcnow(),
        "scheduled_end": datetime.utcnow() + timedelta(days=7),
        "questions": [
            {"text": "‘இந்தியாவின் நெப்போலியன்’ யார்?", "options": ["சந்திரகுப்தர் I","சமுத்ரகுப்தர்","அசோகர்","ஸ்கந்தகுப்தர்"], "correct_option": 1, "explanation": "சமுத்ரகுப்தர்."},
            {"text": "டெல்லி சுல்தான்களை நிறுவியவர் யார்?", "options": ["குத்ப்-உத்-தீன் ஐபக்","இல்துத்தமிஷ்","பால்பன்","கில்ஜி"], "correct_option": 0, "explanation": "ஐபக் நிறுவினார்."},
            {"text": "முகலாய பேரரசின் நிறுவனர்?", "options": ["அக்பர்","பாபர்","ஹுமாயூன்","ஷாஜகான்"], "correct_option": 1, "explanation": "பாபர்."},
            {"text": "சிவாஜி சேர்ந்த பேரரசு?", "options": ["முகலாயர்","மராத்தியர்","சுல்தான்கள்","குப்தர்"], "correct_option": 1, "explanation": "மராத்தியர்."},
            {"text": "அக்பர் உருவாக்கிய மதம்?", "options": ["இஸ்லாம்","தின்-இ-இலாஹி","புத்தம்","ஜைனம்"], "correct_option": 1, "explanation": "தின்-இ-இலாஹி."},
            {"text": "குப்தர்களின் பொற்காலம் எனப்படும் காலம்?", "options": ["மௌரியர்","குப்தர்","சோழர்","பாண்டியர்"], "correct_option": 1, "explanation": "குப்த காலம்."},
            {"text": "பானிபட் முதல் போர் நடந்த ஆண்டு?", "options": ["1526","1556","1761","1707"], "correct_option": 0, "explanation": "1526."},
            {"text": "பதேபூர் சிக்ரி யாரால் கட்டப்பட்டது?", "options": ["பாபர்","அக்பர்","ஷாஜகான்","ஔரங்கசீப்"], "correct_option": 1, "explanation": "அக்பர்."},
            {"text": "மராத்தியரின் தலைநகரம்?", "options": ["பூனா","டெல்லி","ஆக்ரா","லக்னோ"], "correct_option": 0, "explanation": "பூனா."},
            {"text": "பொருத்துக:\n1. பாபர்\n2. அக்பர்\n3. சிவாஜி\n4. ஐபக்\nA. மராத்தியர்\nB. முகலாயர்\nC. தின்-இ-இலாஹி\nD. சுல்தான்கள்", 
             "options": ["1-B,2-C,3-A,4-D","1-A,2-B,3-C,4-D","1-B,2-A,3-C,4-D","1-D,2-C,3-A,4-B"], 
             "correct_option": 0, "explanation": "சரியான பொருத்தம்."}
        ]
    },
    {
        "title": "இந்திய வரலாறு – நடுத்தரம்",
        "description": "மிதமான TNPSC கேள்விகள்",
        "difficulty": DifficultyLevel.medium,
        "subject": "History",
        "topic": "Indian History",
        "scheduled_start": datetime.utcnow(),
        "scheduled_end": datetime.utcnow() + timedelta(days=7),
        "questions": [
            {"text": "சமுத்ரகுப்தரின் கவிஞர்?", "options": ["காளிதாசர்","ஹரிசேனன்","பாணபட்டர்","வராகமிகிரர்"], "correct_option": 1, "explanation": "ஹரிசேனன்."},
            {"text": "இக்தா முறையை அறிமுகப்படுத்தியவர்?", "options": ["பால்பன்","இல்துத்தமிஷ்","கில்ஜி","துக்ளக்"], "correct_option": 1, "explanation": "இல்துத்தமிஷ்."},
            {"text": "அலாவுதீன் கில்ஜி எந்த முறையை அறிமுகப்படுத்தினார்?", "options": ["வரி","விலை கட்டுப்பாடு","நாணயம்","படை"], "correct_option": 1, "explanation": "விலை கட்டுப்பாடு."},
            {"text": "ஷாஜகான் கட்டிய நினைவிடம்?", "options": ["குதுப் மினார்","தாஜ்மஹால்","சிவாஜி கோட்டை","சாஞ்சி"], "correct_option": 1, "explanation": "தாஜ்மஹால்."},
            {"text": "சிவாஜியின் குரு?", "options": ["ராமதாஸ்","கபீர்","நானக்","துகாராம்"], "correct_option": 0, "explanation": "ராமதாஸ்."},
            {"text": "பீகாக் த்ரோன் யாருடையது?", "options": ["பாபர்","ஷாஜகான்","அக்பர்","ஔரங்கசீப்"], "correct_option": 1, "explanation": "ஷாஜகான்."},
            {"text": "முகலாயர் ஆட்சி மொழி?", "options": ["தமிழ்","பாரசீகம்","இந்தி","சமஸ்கிருதம்"], "correct_option": 1, "explanation": "பாரசீகம்."},
            {"text": "பாஜி ராவ் எந்த பேரரசு?", "options": ["மராத்தியர்","முகலாயர்","குப்தர்","சுல்தான்கள்"], "correct_option": 0, "explanation": "மராத்தியர்."},
            {"text": "ஹுமாயூன் தப்பிச்ச நாடு?", "options": ["சீனா","பாரசீகம்","இங்கிலாந்து","அமெரிக்கா"], "correct_option": 1, "explanation": "பாரசீகம்."},
            {"text": "பொருத்துக:\n1. காளிதாசர்\n2. கில்ஜி\n3. அக்பர்\n4. சிவாஜி\nA. இலக்கியம்\nB. விலை கட்டுப்பாடு\nC. தின்-இ-இலாஹி\nD. மராத்தியர்",
             "options": ["1-A,2-B,3-C,4-D","1-B,2-A,3-C,4-D","1-A,2-C,3-B,4-D","1-D,2-B,3-A,4-C"],
             "correct_option": 0, "explanation": "சரியான பொருத்தம்."}
        ]
    },
    {
        "title": "இந்திய வரலாறு – கடினம்",
        "description": "உயர் நிலை கேள்விகள்",
        "difficulty": DifficultyLevel.hard,
        "subject": "History",
        "topic": "Indian History",
        "scheduled_start": datetime.utcnow(),
        "scheduled_end": datetime.utcnow() + timedelta(days=7),
        "questions": [
            {"text": "ஹூணர்களை தோற்கடித்த குப்தர்?", "options": ["சமுத்ரகுப்தர்","சந்திரகுப்தர்","ஸ்கந்தகுப்தர்","குமாரகுப்தர்"], "correct_option": 2, "explanation": "ஸ்கந்தகுப்தர்."},
            {"text": "டோக்கன் நாணயம் அறிமுகம்?", "options": ["பால்பன்","கில்ஜி","துக்ளக்","இல்துத்தமிஷ்"], "correct_option": 2, "explanation": "துக்ளக்."},
            {"text": "இசை தடை செய்தவர்?", "options": ["அக்பர்","ஔரங்கசீப்","ஷாஜகான்","ஹுமாயூன்"], "correct_option": 1, "explanation": "ஔரங்கசீப்."},
            {"text": "நானா சாகேப் யார்?", "options": ["பாலாஜி பாஜி ராவ்","சிவாஜி","ஷாகு","பாஜி ராவ்"], "correct_option": 0, "explanation": "பாலாஜி பாஜி ராவ்."},
            {"text": "ஃபா-ஹியன் வந்த காலம்?", "options": ["மௌரியர்","குப்தர்","முகலாயர்","சுல்தான்கள்"], "correct_option": 1, "explanation": "குப்த காலம்."},
            {"text": "இப்னு பட்டூத்தா யாரின் காலம்?", "options": ["முகலாயர்","சுல்தான்கள்","குப்தர்","மராத்தியர்"], "correct_option": 1, "explanation": "சுல்தான்கள்."},
            {"text": "அபுல் ஃபஸ்ல் யாரின் அரண்மனை?", "options": ["பாபர்","அக்பர்","ஷாஜகான்","ஔரங்கசீப்"], "correct_option": 1, "explanation": "அக்பர்."},
            {"text": "மராத்தியர் வரலாற்றாசிரியர்?", "options": ["டஃப்","ஹியூம்","ஸ்மித்","மேக்ஸ்"], "correct_option": 0, "explanation": "கிராண்ட் டஃப்."},
            {"text": "குப்தர் கால கல்வெட்டு?", "options": ["அலகாபாத்","அசோக","தாஜ்","குதுப்"], "correct_option": 0, "explanation": "அலகாபாத் கல்வெட்டு."},
            {"text": "பொருத்துக:\n1. ஃபா-ஹியன்\n2. இப்னு பட்டூத்தா\n3. அபுல் ஃபஸ்ல்\n4. டஃப்\nA. குப்தர்\nB. சுல்தான்கள்\nC. முகலாயர்\nD. மராத்தியர்",
             "options": ["1-A,2-B,3-C,4-D","1-B,2-A,3-C,4-D","1-A,2-C,3-B,4-D","1-D,2-B,3-A,4-C"],
             "correct_option": 0, "explanation": "சரியான பொருத்தம்."}
        ]
    }
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
