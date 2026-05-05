# Quiz App 🎓

A **FastAPI** MCQ Quiz platform with:
- 👤 User & Admin panels
- 📡 WebSocket live monitoring
- 🏷️ Topic/Subject/Difficulty based quizzes
- ⏰ Scheduled tests
- 📊 Results & scoring
- 🐘 PostgreSQL backend

---

## Project Structure

```
quiz_app/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # SQLAlchemy async DB setup
│   ├── ws_manager.py        # WebSocket broadcast manager
│   ├── core/
│   │   └── security.py      # JWT auth, password hashing
│   ├── models/
│   │   ├── user.py
│   │   └── quiz.py
│   ├── schemas/
│   │   ├── user.py
│   │   └── quiz.py
│   └── routers/
│       ├── auth.py
│       ├── admin.py
│       ├── user.py
│       └── ws.py
├── .env                     # DB URL & secret key
├── seed.py
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Create the PostgreSQL database

```bash
psql -U postgres
CREATE DATABASE quiz_app;
\q
```

### 2. Configure `.env`

Edit `.env` with your credentials:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/quiz_app
SECRET_KEY=change_this_to_a_long_random_string
```

### 3. Install & run

```bash
cd quiz_app

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on first startup.

Open **http://localhost:8000/docs** for the Swagger UI.

---

## Default Admin Account

Created automatically on first run:
- **Username:** `admin`
- **Password:** `admin123`

---

## Seed Sample Data

```bash
python seed.py
```

Adds Tamil, Physics, and Maths quizzes with sample MCQ questions.

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login → returns JWT |
| GET | `/auth/me` | Current user info |

### Admin Panel
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/stats` | Dashboard: users, quizzes, live test-takers |
| GET | `/admin/users` | All users |
| POST | `/admin/quizzes` | Create quiz |
| GET | `/admin/quizzes` | List quizzes (filter: difficulty, subject) |
| PUT | `/admin/quizzes/{id}` | Update quiz |
| DELETE | `/admin/quizzes/{id}` | Delete quiz |
| POST | `/admin/quizzes/{id}/questions` | Add MCQ question |
| PUT | `/admin/questions/{id}` | Update question |
| DELETE | `/admin/questions/{id}` | Delete question |
| GET | `/admin/quizzes/{id}/attempts` | Who attempted this quiz |

### User Panel
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/user/quizzes` | Browse available quizzes |
| GET | `/user/quizzes/{id}` | Quiz detail (blocked outside schedule) |
| POST | `/user/quizzes/{id}/start` | Start attempt |
| POST | `/user/attempts/{id}/submit` | Submit answers |
| GET | `/user/results` | My results tab |
| GET | `/user/results/{id}` | Result detail with correct answers |

### WebSocket — Admin Live Monitor
```
ws://localhost:8000/ws/admin?token=<jwt_token>
```

Receives JSON events:
```json
{ "type": "quiz_started",   "user": "john", "quiz_title": "Physics – Motion", ... }
{ "type": "quiz_submitted", "user": "john", "score": 8, "total": 10, ... }
```

---

## Difficulty & Subjects

**Difficulty:** `easy` | `medium` | `hard`

**Subject examples:** Tamil, Science, Physics, Maths, Biology, Chemistry

**Topic:** any sub-topic string — e.g. Grammar, Algebra, Newton's Laws
# quizv2
