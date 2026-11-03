import json
import logging
import asyncio
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("simrs_tte.websocket")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.loop: asyncio.AbstractEventLoop = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.loop = asyncio.get_running_loop()
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, data: Dict[str, Any]):
        """Kirim pesan real-time ke semua client yang terkoneksi (SIMRS Web, Mobile React Native, SSO)"""
        if not self.active_connections:
            return

        message = json.dumps(data)
        disconnected = []
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Error sending websocket message: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            self.disconnect(conn)

ws_manager = ConnectionManager()

def dispatch_ws_event(event_type: str, noreg: str, document_id: int, version_label: str = "v1.0", extra: dict = None):
    """
    Kirim event real-time ke semua client WebSocket (SIMRS Web, SSO, Mobile React Native)
    Didesain agar 100% thread-safe saat dipanggil dari synchronous FastAPI controller route handler.
    """
    payload = {
        "event": event_type,
        "noreg": str(noreg),
        "document_id": int(document_id) if document_id else None,
        "version_label": str(version_label),
        **(extra or {})
    }
    try:
        if ws_manager.loop and ws_manager.loop.is_running():
            asyncio.run_coroutine_threadsafe(ws_manager.broadcast(payload), ws_manager.loop)
        else:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ws_manager.broadcast(payload))
            except RuntimeError:
                pass
    except Exception as e:
        logger.warning(f"Failed to dispatch ws event {event_type}: {e}")

        logger.warning(f"Failed to dispatch ws event {event_type}: {e}")

