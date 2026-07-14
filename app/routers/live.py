"""
Live quiz channels: admin creates a named (optionally password-protected)
channel wrapping an existing quiz; everyone joins the same WebSocket,
sees the live participant list, and once the admin starts it, questions
are pushed to everyone in sync with a running leaderboard.

Auth on the WebSocket reuses the same JWT scheme as /ws/admin: the access
token is passed as a query param since browsers can't set custom headers
on a WebSocket handshake.
"""
import time as _time

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import ALGORITHM, SECRET_KEY, get_admin_user, get_current_user
from app.database import AsyncSessionLocal, get_db
from app.live_session_manager import (
    LiveQuestion,
    Participant,
    advance_question,
    broadcast,
    explain_payload,
    send_explain_question,
    send_user_list,
    store,
)
from app.models.quiz import Question, Quiz
from app.models.quiz import QuizType
from app.models.user import User
from app.schemas.live import LiveChannelCreate, LiveChannelOut, LiveChannelSummary

router = APIRouter(prefix="/live", tags=["Live Quiz"])


@router.post("/channels", response_model=LiveChannelOut, status_code=201)
async def create_channel(
    data: LiveChannelCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    result = await db.execute(select(Quiz).where(Quiz.id == data.quiz_id))
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(404, "Quiz not found")
    if quiz.quiz_type != QuizType.live.value:
        raise HTTPException(400, "Only quizzes of type 'live' can be hosted in a live channel")

    q_result = await db.execute(
        select(Question).where(Question.quiz_id == quiz.id).order_by(Question.id)
    )
    questions = q_result.scalars().all()
    if not questions:
        raise HTTPException(400, "This quiz has no questions yet")

    live_questions = [
        LiveQuestion(
            id=q.id,
            text=q.text,
            options=q.options,
            correct_option=q.correct_option,
            time_limit=data.time_per_question,
            explanation=q.explanation,
        )
        for q in questions
    ]

    channel = store.create(
        name=data.name,
        password=data.password,
        quiz_id=quiz.id,
        quiz_title=quiz.title,
        admin_user_id=admin.id,
        questions=live_questions,
    )
    return LiveChannelOut(
        code=channel.code,
        name=channel.name,
        locked=bool(channel.password),
        quiz_id=quiz.id,
        quiz_title=quiz.title,
    )


@router.get("/channels", response_model=list[LiveChannelSummary])
async def list_channels(admin: User = Depends(get_admin_user)):
    return store.list_public()


@router.delete("/channels/{code}", status_code=204)
async def close_channel(code: str, admin: User = Depends(get_admin_user)):
    channel = store.get(code)
    if channel:
        store.remove(code)


def _verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


async def _get_user(payload: dict) -> User | None:
    user_id = payload.get("sub")
    if user_id is None:
        return None
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return None
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


@router.websocket("/ws/{code}")
async def live_ws(websocket: WebSocket, code: str, token: str = Query(...)):
    await websocket.accept()

    payload = _verify_token(token)
    if not payload:
        await websocket.send_json({"type": "error", "message": "Invalid or expired token"})
        await websocket.close(code=1008)
        return

    user = await _get_user(payload)
    if not user:
        await websocket.send_json({"type": "error", "message": "User not found"})
        await websocket.close(code=1008)
        return


    channel = store.get(code)
    if not channel:
        await websocket.send_json({"type": "error", "message": "Channel not found"})
        await websocket.close()
        return

    participant: Participant | None = None

    try:
        first_msg = await websocket.receive_json()
        if first_msg.get("type") != "join":
            await websocket.send_json({"type": "error", "message": "Expected a join message first"})
            await websocket.close()
            return

        password = first_msg.get("password")
        if not channel.check_password(password):
            await websocket.send_json({"type": "error", "message": "Incorrect password"})
            await websocket.close()
            return

        is_admin = user.is_admin and user.id == channel.admin_user_id

        existing = channel.participants.get(user.id)
        if existing is not None:
            # Ping the old socket to see if it's actually still alive. A
            # genuine second tab gets rejected as before; a stale connection
            # (crash, dropped wifi, refresh that skipped WebSocketDisconnect)
            # gets evicted so the admin -- or anyone -- can reclaim their seat
            # instead of being permanently locked out of their own channel.
            try:
                await existing.ws.send_json({"type": "ping"})
                stale = False
            except Exception:
                stale = True

            if not stale:
                await websocket.send_json(
                    {"type": "error", "message": "You're already connected in another tab"}
                )
                await websocket.close()
                return

            try:
                await existing.ws.close()
            except Exception:
                pass
            channel.participants.pop(user.id, None)

        # Reconnecting participants keep their running score instead of
        # restarting at 0.
        prior_score = existing.score if existing is not None else 0
        participant = Participant(
            user_id=user.id,
            username=user.username,
            ws=websocket,
            is_admin=is_admin,
            score=prior_score,
        )
        channel.participants[user.id] = participant

        await websocket.send_json(
            {
                "type": "joined",
                "channel": {
                    "code": channel.code,
                    "name": channel.name,
                    "state": channel.state,
                    "quiz_title": channel.quiz_title,
                },
                "is_admin": is_admin,
            }
        )
        await send_user_list(channel)

        # Resume mid-session: catch this participant up on whatever's showing
        # right now instead of leaving them stuck until the next question.
        if channel.state == "in_progress" and 0 <= channel.current_question_index < len(channel.questions):
            q = channel.questions[channel.current_question_index]
            if channel.phase == "results":
                if is_admin:
                    await websocket.send_json(
                        {
                            "type": "question_ended",
                            "index": channel.current_question_index,
                            "correct_index": channel.last_correct_index,
                            "counts": channel.question_counts(channel.current_question_index),
                        }
                    )
                else:
                    await websocket.send_json(
                        {"type": "question_locked", "index": channel.current_question_index}
                    )
                await websocket.send_json({"type": "leaderboard", "scores": channel.leaderboard()})
            else:
                await websocket.send_json(
                    {
                        "type": "question",
                        "index": channel.current_question_index,
                        "total": len(channel.questions),
                        "id": q.id,
                        "text": q.text,
                        "options": q.options,
                        "time_limit": channel.remaining_seconds(),
                    }
                )
        elif channel.state == "finished":
            await websocket.send_json(
                {"type": "quiz_ended", "final_leaderboard": channel.leaderboard()}
            )
            if channel.phase == "explain":
                payload = explain_payload(channel)
                if payload is not None:
                    await websocket.send_json(payload)

        while True:
            msg = await websocket.receive_json()
            mtype = msg.get("type")

            if mtype == "start_quiz":
                if not participant.is_admin:
                    await websocket.send_json(
                        {"type": "error", "message": "Only the admin can start the quiz"}
                    )
                    continue
                if channel.state != "waiting":
                    continue
                channel.state = "in_progress"
                await broadcast(channel, {"type": "quiz_started"})
                channel.current_question_index = -1
                await advance_question(channel)

            elif mtype == "answer":
                if participant.is_admin:
                    await websocket.send_json(
                        {"type": "error", "message": "The host doesn't take the quiz"}
                    )
                    continue
                if channel.state != "in_progress" or participant.answered_current:
                    continue
                q_index = msg.get("index")
                option_index = msg.get("option_index")
                if q_index != channel.current_question_index:
                    continue
                question = channel.questions[channel.current_question_index]
                if not isinstance(option_index, int) or not (0 <= option_index < len(question.options)):
                    continue
                participant.answered_current = True
                counts = channel.answer_counts.setdefault(
                    channel.current_question_index, [0] * len(question.options)
                )
                counts[option_index] += 1
                is_correct = option_index == question.correct_option
                if is_correct:
                    elapsed = _time.time() - channel.current_question_started_at
                    speed_bonus = max(0.0, question.time_limit - elapsed)
                    participant.score += 100 + int(speed_bonus * 5)
                await websocket.send_json({"type": "answer_ack", "correct": is_correct})

            elif mtype == "start_explain":
                if not participant.is_admin:
                    await websocket.send_json(
                        {"type": "error", "message": "Only the admin can start the explanation"}
                    )
                    continue
                if channel.state != "finished" or not channel.questions:
                    continue
                channel.phase = "explain"
                channel.explain_index = 0
                await send_explain_question(channel)

            elif mtype in ("explain_next", "explain_prev"):
                if not participant.is_admin:
                    await websocket.send_json(
                        {"type": "error", "message": "Only the admin can move through the explanation"}
                    )
                    continue
                if channel.phase != "explain":
                    continue
                step = 1 if mtype == "explain_next" else -1
                new_index = channel.explain_index + step
                if 0 <= new_index < len(channel.questions):
                    channel.explain_index = new_index
                    await send_explain_question(channel)

            elif mtype == "leave":
                break

    except WebSocketDisconnect:
        pass
    finally:
        if participant is not None:
            channel.participants.pop(user.id, None)
            await send_user_list(channel)
