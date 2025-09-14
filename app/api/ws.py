from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json

router = APIRouter()

# Simple in-memory connection manager (NOTE: single-process only)
class ConnectionManager:
    def __init__(self):
        self.docs: Dict[str, Set[WebSocket]] = {}

    async def connect(self, doc_id: str, ws: WebSocket):
        await ws.accept()
        self.docs.setdefault(doc_id, set()).add(ws)

    def disconnect(self, doc_id: str, ws: WebSocket):
        sockets = self.docs.get(doc_id)
        if sockets and ws in sockets:
            sockets.remove(ws)

    async def broadcast(self, doc_id: str, message: dict):
        sockets = list(self.docs.get(doc_id, []))
        if not sockets:
            return
        data = json.dumps(message)
        await asyncio.gather(*(s.send_text(data) for s in sockets), return_exceptions=True)

manager = ConnectionManager()

@router.websocket("/ws/{doc_id}")
async def websocket_endpoint(websocket: WebSocket, doc_id: str):
    """
    Simple WebSocket endpoint:
    - On connect -> add to room
    - Receive messages (assume JSON) and broadcast to other clients
    TODO: persist deltas to DB / use Redis pubsub for multi-process scaling / implement CRDT syncing
    """
    await manager.connect(doc_id, websocket)
    try:
        while True:
            text = await websocket.receive_text()
            try:
                msg = json.loads(text)
            except Exception:
                msg = {"type": "raw", "data": text}
            await manager.broadcast(doc_id, msg)
    except WebSocketDisconnect:
        manager.disconnect(doc_id, websocket)
