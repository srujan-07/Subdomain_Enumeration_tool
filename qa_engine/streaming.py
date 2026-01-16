"""WebSocket event streaming for real-time frontend updates."""

import asyncio
import json
import logging
from typing import Set

from flask import request
from flask_sock import Sock

from qa_engine.core.events import event_bus, EventType

logger = logging.getLogger(__name__)


class WSManager:
    """Manage WebSocket connections and broadcast events."""

    def __init__(self) -> None:
        self.active_connections: dict[str, Set] = {}

    def register_connection(self, scan_id: str, ws) -> None:
        """Register a WebSocket connection for a scan."""
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = set()
        self.active_connections[scan_id].add(ws)
        logger.debug(f"Registered WS for scan {scan_id}")

    def unregister_connection(self, scan_id: str, ws) -> None:
        """Unregister a WebSocket connection."""
        if scan_id in self.active_connections:
            self.active_connections[scan_id].discard(ws)
            if not self.active_connections[scan_id]:
                del self.active_connections[scan_id]

    async def broadcast(self, scan_id: str, message: str) -> None:
        """Broadcast message to all connected clients for a scan."""
        if scan_id not in self.active_connections:
            return

        disconnected = set()
        for ws in self.active_connections[scan_id]:
            try:
                await ws.send(message)
            except Exception as e:
                logger.warning(f"Error sending to WS: {e}")
                disconnected.add(ws)

        # Clean up disconnected
        for ws in disconnected:
            self.unregister_connection(scan_id, ws)


ws_manager = WSManager()


def setup_websocket(app, sock: Sock) -> None:
    """Setup WebSocket routes."""

    @sock.route("/ws/scan/<scan_id>")
    def ws_scan_events(ws, scan_id: str) -> None:
        """WebSocket endpoint for scan events."""
        ws_manager.register_connection(scan_id, ws)

        async def event_callback(event) -> None:
            await ws_manager.broadcast(scan_id, event.to_json())

        event_bus.subscribe_all(event_callback)

        try:
            while True:
                data = ws.receive()
                if data is None:
                    break
                logger.debug(f"WS received: {data}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            ws_manager.unregister_connection(scan_id, ws)
            logger.debug(f"WebSocket closed for scan {scan_id}")
