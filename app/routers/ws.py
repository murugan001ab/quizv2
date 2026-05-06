import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.ws_manager import manager

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
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(30)
            await websocket.send_text(json.dumps({"type": "ping"}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
