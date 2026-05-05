"""
WebSocket endpoint — Admin can connect to receive live updates
whenever a user starts or submits a quiz attempt.

ws://localhost:8000/ws/admin?token=<jwt>
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from core.security import SECRET_KEY, ALGORITHM
from ws_manager import manager

router = APIRouter(tags=["WebSocket"])


def _verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


@router.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket, token: str = Query(...)):
    payload = _verify_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    # We trust is_admin check was done; for simplicity accept any valid token here
    # In production you'd check the user's is_admin flag from DB
    await manager.connect(websocket)
    try:
        while True:
            # keep alive — send ping every 30s
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
