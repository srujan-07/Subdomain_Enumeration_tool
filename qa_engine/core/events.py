"""Event streaming system for real-time QA inspection updates."""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, List, Dict, Any

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types emitted during QA scanning."""

    SCAN_STARTED = "scan_started"
    URL_DISCOVERED = "url_discovered"
    URL_VALIDATED = "url_validated"
    PAGE_TESTING_STARTED = "page_testing_started"
    PAGE_ANALYZED = "page_analyzed"
    ISSUES_DETECTED = "issues_detected"
    SCORE_UPDATED = "score_updated"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"


@dataclass
class QAEvent:
    """Base event structure."""

    type: EventType
    timestamp: str
    scan_id: str
    data: Dict[str, Any]

    def to_dict(self) -> Dict:
        return {
            "type": self.type.value,
            "timestamp": self.timestamp,
            "scan_id": self.scan_id,
            "data": self.data,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventBus:
    """Manages event subscriptions and emissions."""

    def __init__(self) -> None:
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: Dict[str, List[QAEvent]] = {}

    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type.value}")

    def subscribe_all(self, callback: Callable) -> None:
        """Subscribe to all event types."""
        for event_type in EventType:
            self.subscribe(event_type, callback)

    async def emit(self, event: QAEvent) -> None:
        """Emit an event to all subscribers."""
        # Store in history
        if event.scan_id not in self.event_history:
            self.event_history[event.scan_id] = []
        self.event_history[event.scan_id].append(event)

        # Notify subscribers
        callbacks = self.subscribers.get(event.type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {e}")

    def get_history(self, scan_id: str) -> List[QAEvent]:
        """Get all events for a scan."""
        return self.event_history.get(scan_id, [])

    def clear_history(self, scan_id: str) -> None:
        """Clear event history for a scan."""
        self.event_history.pop(scan_id, None)


# Global event bus
event_bus = EventBus()


def create_event(
    event_type: EventType, scan_id: str, data: Dict[str, Any]
) -> QAEvent:
    """Factory for creating events."""
    return QAEvent(
        type=event_type,
        timestamp=datetime.utcnow().isoformat(),
        scan_id=scan_id,
        data=data,
    )
