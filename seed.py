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
        "description": "mugals qution 50",
        "difficulty": DifficultyLevel.hard,
        "subject": "History",
        "topic": "Indian History",
        "scheduled_start": datetime.utcnow(),
        "scheduled_end": datetime.utcnow() + timedelta(days=7),
        "questions": [
    {
        "text": "பாபரின் தந்தை வழி வம்சாவளி யாருடன் தொடர்புடையது?",
        "options": ["செங்கிஸ்கான்", "தைமூர்", "ஷேர் ஷா", "அக்பர்"],
        "correct_option": 1,
        "explanation": "பாபர் தந்தை வழியில் தைமூரின் வம்சாவளியைச் சேர்ந்தவர்.",
        "year": "TNPSC Model"
    },
    {
        "text": "பாபரின் தாய்வழி முன்னோர் யார்?",
        "options": ["அலாவுதீன் கில்ஜி", "செங்கிஸ்கான்", "இல்துத்தமிஷ்", "ஷாஜகான்"],
        "correct_option": 1,
        "explanation": "பாபர் தாய்வழியில் செங்கிஸ்கானின் வம்சாவளியைச் சேர்ந்தவர்.",
        "year": "TNPSC Model"
    },
    {
        "text": "பாபர் எந்த வயதில் பர்கானாவின் ஆட்சியாளரானார்?",
        "options": ["10", "11", "12", "14"],
        "correct_option": 2,
        "explanation": "12 வயதில் பர்கானாவின் ஆட்சியாளரானார்.",
        "year": "TNPSC Model"
    },
    {
        "text": "பாபர் இந்தியாவை நோக்கி முதன்முதலில் படையெடுத்த ஆண்டு?",
        "options": ["1505", "1526", "1519", "1524"],
        "correct_option": 0,
        "explanation": "1505 இல் பாபர் இந்தியாவை நோக்கி முதல் முயற்சி செய்தார்.",
        "year": "TNPSC Model"
    },
    {
        "text": "பாபர் இப்ராஹிம் லோதியை தோற்கடித்த போர் எது?",
        "options": ["கன்வா போர்", "பானிபட் முதல் போர்", "ஹல்திகாட் போர்", "பிளாசி போர்"],
        "correct_option": 1,
        "explanation": "1526 பானிபட் முதல் போரில் இப்ராஹிம் லோதியை தோற்கடித்தார்.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "பாபர் ராணா சங்காவை தோற்கடித்த போர் எது?",
        "options": ["கன்வா போர்", "பானிபட் போர்", "தலிகோட்டா போர்", "ஹல்திகாட் போர்"],
        "correct_option": 0,
        "explanation": "1527 இல் கன்வா போரில் ராணா சங்கா தோற்கடிக்கப்பட்டார்.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "பாபர் தனது சுயசரிதையை எந்த மொழியில் எழுதினார்?",
        "options": ["பாரசீகம்", "அரபு", "துருக்கி", "உருது"],
        "correct_option": 2,
        "explanation": "பாபர்நாமா துருக்கி மொழியில் எழுதப்பட்டது.",
        "year": "TNPSC Model"
    },
    {
        "text": "ஹுமாயூனை தோற்கடித்த ஆப்கான் தலைவர் யார்?",
        "options": ["ஷேர் ஷா", "ராணா சங்கா", "பைரம் கான்", "பாபர்"],
        "correct_option": 0,
        "explanation": "ஷேர் ஷா சூரி ஹுமாயூனை தோற்கடித்தார்.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "ஹுமாயூன் தோல்வியடைந்த போர் எது?",
        "options": ["சௌசா போர்", "பானிபட் போர்", "கன்வா போர்", "ஹல்திகாட் போர்"],
        "correct_option": 0,
        "explanation": "1539 சௌசா போரில் ஹுமாயூன் தோல்வியடைந்தார்.",
        "year": "TNPSC Model"
    },
    {
        "text": "ஹுமாயூனுக்கு உதவி செய்த பாரசீக அரசர் யார்?",
        "options": ["ஷா தஹ்மாஸ்ப்", "நாதிர்ஷா", "அக்பர்", "பாபர்"],
        "correct_option": 0,
        "explanation": "ஷா தஹ்மாஸ்ப் ஹுமாயூனுக்கு உதவி செய்தார்.",
        "year": "TNPSC Group 4"
    },
    {
        "text": "ஷேர் ஷா அறிமுகப்படுத்திய வெள்ளி நாணயம் எது?",
        "options": ["தினார்", "ரூபியா", "மொஹர்", "தங்கா"],
        "correct_option": 1,
        "explanation": "ரூபியா நாணயத்தை அறிமுகப்படுத்தினார்.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "கிராண்ட் ட்ரங்க் சாலையை அமைத்தவர் யார்?",
        "options": ["அக்பர்", "ஷாஜகான்", "ஷேர் ஷா", "பாபர்"],
        "correct_option": 2,
        "explanation": "ஷேர் ஷா முக்கிய சாலைகளை அமைத்தார்.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "அக்பர் பேரரசராக அறிவிக்கப்பட்ட வயது?",
        "options": ["10", "13", "15", "18"],
        "correct_option": 1,
        "explanation": "13 வயதில் அக்பர் பேரரசரானார்.",
        "year": "TNPSC Group 4"
    },
    {
        "text": "இரண்டாம் பானிபட் போர் நடைபெற்ற ஆண்டு?",
        "options": ["1526", "1556", "1761", "1576"],
        "correct_option": 1,
        "explanation": "1556 இல் இரண்டாம் பானிபட் போர் நடைபெற்றது.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "அக்பரின் பாதுகாவலர் யார்?",
        "options": ["பீர்பால்", "பைரம் கான்", "தோடர்மால்", "தான்சேன்"],
        "correct_option": 1,
        "explanation": "பைரம் கான் அக்பரின் பாதுகாவலர்.",
        "year": "TNPSC Model"
    },
    {
        "text": "ஹல்திகாட் போர் யாருக்கு இடையில் நடைபெற்றது?",
        "options": ["அக்பர் மற்றும் ராணா பிரதாப்", "பாபர் மற்றும் லோதி", "ஷேர் ஷா மற்றும் ஹுமாயூன்", "ஷாஜகான் மற்றும் மராத்தியர்"],
        "correct_option": 0,
        "explanation": "1576 இல் ஹல்திகாட் போர் நடைபெற்றது.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "ராணா பிரதாப் எந்த நாட்டின் அரசர்?",
        "options": ["மேவார்", "மால்வா", "குஜராத்", "வங்காளம்"],
        "correct_option": 0,
        "explanation": "ராணா பிரதாப் மேவாரின் அரசர்.",
        "year": "TNPSC Model"
    },
    {
        "text": "அக்பர் ஜிஸ்யா வரியை எப்போது நீக்கினார்?",
        "options": ["1562", "1564", "1570", "1580"],
        "correct_option": 1,
        "explanation": "1564 இல் அக்பர் ஜிஸ்யா வரியை நீக்கினார்.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "அக்பரின் மத விவாத மன்றம் எது?",
        "options": ["இபாதத் கானா", "திவான்-இ-ஆம்", "திவான்-இ-காஸ்", "சுபா"],
        "correct_option": 0,
        "explanation": "இபாதத் கானா மத விவாத மன்றமாக இருந்தது.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "தின்-இ-இலாஹி அறிமுகமான ஆண்டு?",
        "options": ["1575", "1582", "1605", "1560"],
        "correct_option": 1,
        "explanation": "1582 இல் தின்-இ-இலாஹி அறிமுகமானது.",
        "year": "TNPSC Model"
    },

    {
        "text": "அக்பரின் நவரத்தினங்களில் வரி நிர்வாகி யார்?",
        "options": ["பீர்பால்", "தோடர்மால்", "தான்சேன்", "அபுல் ஃபஸ்ல்"],
        "correct_option": 1,
        "explanation": "தோடர்மால் நிலவரி முறையை அமைத்தார்.",
        "year": "TNPSC Group 4"
    },
    {
        "text": "‘ஆயின்-இ-அக்பரி’ நூலை எழுதியவர் யார்?",
        "options": ["அபுல் ஃபஸ்ல்", "பதாயூனி", "பீர்பால்", "தான்சேன்"],
        "correct_option": 0,
        "explanation": "அபுல் ஃபஸ்ல் எழுதியார்.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "ஜகங்கீரின் இயற்பெயர் என்ன?",
        "options": ["சலீம்", "குர்ரம்", "அலங்கீர்", "முஹம்மது"],
        "correct_option": 0,
        "explanation": "ஜகங்கீரின் இயற்பெயர் சலீம்.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "நூர்ஜகானின் உண்மைப் பெயர் என்ன?",
        "options": ["மேஹ்ருன்னிசா", "மும்தாஜ்", "ஜஹானாரா", "குல்பதான்"],
        "correct_option": 0,
        "explanation": "நூர்ஜகானின் உண்மைப் பெயர் மேஹ்ருன்னிசா.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "ஜகங்கீர் காலத்தில் இந்தியா வந்த ஆங்கில தூதர் யார்?",
        "options": ["தாமஸ் ரோ", "ஹாக்கின்ஸ்", "கிளைவ்", "வாஸ்கோடகாமா"],
        "correct_option": 0,
        "explanation": "சர் தாமஸ் ரோ ஜகங்கீர் காலத்தில் வந்தார்.",
        "year": "TNPSC Group 2"
    },

    {
        "text": "ஷாஜகானின் இயற்பெயர் என்ன?",
        "options": ["குர்ரம்", "சலீம்", "அலங்கீர்", "முராத்"],
        "correct_option": 0,
        "explanation": "ஷாஜகானின் இயற்பெயர் குர்ரம்.",
        "year": "TNPSC Group 4"
    },
    {
        "text": "தாஜ்மஹால் கட்டத் தொடங்கிய ஆண்டு?",
        "options": ["1628", "1632", "1648", "1658"],
        "correct_option": 1,
        "explanation": "1632 இல் கட்டத் தொடங்கப்பட்டது.",
        "year": "TNPSC Model"
    },
    {
        "text": "ஷாஜகானை சிறையில் அடைத்தவர் யார்?",
        "options": ["தாரா", "ஔரங்கசீப்", "முராத்", "ஷுஜா"],
        "correct_option": 1,
        "explanation": "ஔரங்கசீப் தந்தையை சிறையில் அடைத்தார்.",
        "year": "TNPSC Group 1"
    },
    {
        "text": "ஔரங்கசீப்பின் பட்டப்பெயர் என்ன?",
        "options": ["சலீம்", "அலங்கீர்", "குர்ரம்", "ஜகங்கீர்"],
        "correct_option": 1,
        "explanation": "ஔரங்கசீப் அலங்கீர் என அழைக்கப்பட்டார்.",
        "year": "TNPSC Group 2"
    },
    {
        "text": "ஜிஸ்யா வரியை மீண்டும் அறிமுகப்படுத்தியவர் யார்?",
        "options": ["அக்பர்", "ஜகங்கீர்", "ஷாஜகான்", "ஔரங்கசீப்"],
        "correct_option": 3,
        "explanation": "ஔரங்கசீப் ஜிஸ்யா வரியை மீண்டும் அறிமுகப்படுத்தினார்.",
        "year": "TNPSC Group 1"
    }
],
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
