from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

SCHEMA = "LEAF_RUNTIME_EVENT_BUS_PHASE_24B_V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    event_type: str
    source: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = SCHEMA
        return payload


class RuntimeEventBus:
    """
    Shared runtime communication layer.

    This is intentionally independent of Qt.

    Tools emit events.
    Subscribers react to events.
    No tool should need to directly call another tool.
    """

    def __init__(self, retain_history: bool = True, max_history: int = 500) -> None:
        self._subscribers: dict[str, dict[str, Callable[[RuntimeEvent], None]]] = {}
        self._retain_history = retain_history
        self._max_history = max_history
        self._history: list[RuntimeEvent] = []

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[RuntimeEvent], None],
        subscriber_id: str | None = None,
    ) -> str:
        if not event_type:
            raise ValueError("event_type_required")

        if not callable(callback):
            raise TypeError("callback_must_be_callable")

        resolved_id = subscriber_id or f"subscriber_{uuid4().hex[:16]}"
        self._subscribers.setdefault(event_type, {})[resolved_id] = callback
        return resolved_id

    def unsubscribe(self, event_type: str, subscriber_id: str) -> bool:
        subscribers = self._subscribers.get(event_type)

        if not subscribers or subscriber_id not in subscribers:
            return False

        del subscribers[subscriber_id]

        if not subscribers:
            del self._subscribers[event_type]

        return True

    def emit(
        self,
        event_type: str,
        source: str,
        payload: dict[str, Any] | None = None,
    ) -> RuntimeEvent:
        if not event_type:
            raise ValueError("event_type_required")

        if not source:
            raise ValueError("source_required")

        event = RuntimeEvent(
            event_id=f"event_{uuid4().hex[:16]}",
            event_type=event_type,
            source=source,
            payload=dict(payload or {}),
        )

        if self._retain_history:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]

        for callback in list(self._subscribers.get(event_type, {}).values()):
            callback(event)

        for callback in list(self._subscribers.get("*", {}).values()):
            callback(event)

        return event

    def subscriber_count(self, event_type: str | None = None) -> int:
        if event_type is not None:
            return len(self._subscribers.get(event_type, {}))

        return sum(len(group) for group in self._subscribers.values())

    def history(self) -> list[dict[str, Any]]:
        return [event.snapshot() for event in self._history]

    def clear_history(self) -> None:
        self._history.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "subscriber_groups": {
                event_type: sorted(subscribers)
                for event_type, subscribers in self._subscribers.items()
            },
            "subscriber_count": self.subscriber_count(),
            "retain_history": self._retain_history,
            "max_history": self._max_history,
            "history_count": len(self._history),
            "qt_owns_event_bus": False,
            "direct_tool_to_tool_calls_required": False,
        }


runtime_event_bus = RuntimeEventBus()
