from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from leaf_qt.runtime.event_bus import RuntimeEventBus, runtime_event_bus

SCHEMA = "LEAF_RUNTIME_NOTIFICATION_CENTRE_PHASE_24G_V1"

LEVEL_DEBUG = "debug"
LEVEL_INFO = "info"
LEVEL_SUCCESS = "success"
LEVEL_WARNING = "warning"
LEVEL_ERROR = "error"
LEVEL_CRITICAL = "critical"

VALID_NOTIFICATION_LEVELS = {
    LEVEL_DEBUG,
    LEVEL_INFO,
    LEVEL_SUCCESS,
    LEVEL_WARNING,
    LEVEL_ERROR,
    LEVEL_CRITICAL,
}

CATEGORY_RUNTIME = "runtime"
CATEGORY_SAVE = "save"
CATEGORY_VALIDATION = "validation"
CATEGORY_OPTIMISATION = "optimisation"
CATEGORY_IMPORT = "import"
CATEGORY_WORKSPACE = "workspace"
CATEGORY_REPORT = "report"
CATEGORY_WARNING = "warning"
CATEGORY_ERROR = "error"

VALID_NOTIFICATION_CATEGORIES = {
    CATEGORY_RUNTIME,
    CATEGORY_SAVE,
    CATEGORY_VALIDATION,
    CATEGORY_OPTIMISATION,
    CATEGORY_IMPORT,
    CATEGORY_WORKSPACE,
    CATEGORY_REPORT,
    CATEGORY_WARNING,
    CATEGORY_ERROR,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RuntimeNotification:
    notification_id: str
    category: str
    level: str
    title: str
    message: str
    source: str
    target_id: str | None = None
    target_type: str | None = None
    action_ref: str | None = None
    created_at: str = field(default_factory=utc_now)
    read: bool = False

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_RUNTIME_NOTIFICATION_PHASE_24G_V1"
        return payload


class RuntimeNotificationCentre:
    """
    Shared runtime notification owner.

    This owns notification metadata only.

    It does not own:
    - Qt popups
    - modal dialogs
    - report payloads
    - solver payloads
    - validation execution
    """

    def __init__(
        self,
        event_bus: RuntimeEventBus | None = None,
        max_history: int = 500,
    ) -> None:
        self._event_bus = event_bus or runtime_event_bus
        self._max_history = max_history
        self._notifications: dict[str, RuntimeNotification] = {}
        self._order: list[str] = []

    def notify(
        self,
        category: str,
        level: str,
        title: str,
        message: str,
        source: str,
        target_id: str | None = None,
        target_type: str | None = None,
        action_ref: str | None = None,
    ) -> RuntimeNotification:
        if category not in VALID_NOTIFICATION_CATEGORIES:
            raise KeyError(f"notification_category_not_allowed:{category}")

        if level not in VALID_NOTIFICATION_LEVELS:
            raise ValueError(f"notification_level_not_allowed:{level}")

        if not title:
            raise ValueError("title_required")

        if not source:
            raise ValueError("source_required")

        notification = RuntimeNotification(
            notification_id=f"note_{uuid4().hex[:16]}",
            category=category,
            level=level,
            title=title,
            message=message,
            source=source,
            target_id=target_id,
            target_type=target_type,
            action_ref=action_ref,
        )

        self._notifications[notification.notification_id] = notification
        self._order.append(notification.notification_id)
        self._trim_history()

        self._event_bus.emit(
            "runtime.notification.created",
            source=source,
            payload=notification.snapshot(),
        )

        self._event_bus.emit(
            f"runtime.notification.created.{category}",
            source=source,
            payload=notification.snapshot(),
        )

        return notification

    def success(self, title: str, message: str, source: str, **kwargs: Any) -> RuntimeNotification:
        return self.notify(CATEGORY_RUNTIME, LEVEL_SUCCESS, title, message, source, **kwargs)

    def warning(self, title: str, message: str, source: str, **kwargs: Any) -> RuntimeNotification:
        return self.notify(CATEGORY_WARNING, LEVEL_WARNING, title, message, source, **kwargs)

    def error(self, title: str, message: str, source: str, **kwargs: Any) -> RuntimeNotification:
        return self.notify(CATEGORY_ERROR, LEVEL_ERROR, title, message, source, **kwargs)

    def mark_read(self, notification_id: str) -> RuntimeNotification:
        current = self._notifications.get(notification_id)

        if current is None:
            raise KeyError(f"notification_not_found:{notification_id}")

        updated = RuntimeNotification(
            notification_id=current.notification_id,
            category=current.category,
            level=current.level,
            title=current.title,
            message=current.message,
            source=current.source,
            target_id=current.target_id,
            target_type=current.target_type,
            action_ref=current.action_ref,
            created_at=current.created_at,
            read=True,
        )

        self._notifications[notification_id] = updated

        self._event_bus.emit(
            "runtime.notification.read",
            source="notification_centre",
            payload=updated.snapshot(),
        )

        return updated

    def unread(self) -> list[dict[str, Any]]:
        return [
            self._notifications[nid].snapshot()
            for nid in self._order
            if not self._notifications[nid].read
        ]

    def history(self, category: str | None = None) -> list[dict[str, Any]]:
        notes = [self._notifications[nid] for nid in self._order]
        if category is not None:
            notes = [note for note in notes if note.category == category]
        return [note.snapshot() for note in notes]

    def clear(self) -> None:
        self._notifications.clear()
        self._order.clear()

        self._event_bus.emit(
            "runtime.notification.cleared",
            source="notification_centre",
            payload={},
        )

    def _trim_history(self) -> None:
        while len(self._order) > self._max_history:
            oldest = self._order.pop(0)
            self._notifications.pop(oldest, None)

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "notification_count": len(self._order),
            "unread_count": len(self.unread()),
            "max_history": self._max_history,
            "valid_levels": sorted(VALID_NOTIFICATION_LEVELS),
            "valid_categories": sorted(VALID_NOTIFICATION_CATEGORIES),
            "category_counts": {
                category: sum(
                    1 for note in self._notifications.values()
                    if note.category == category
                )
                for category in sorted(VALID_NOTIFICATION_CATEGORIES)
            },
            "qt_owns_notifications": False,
            "replaces_modal_popup_scatter": True,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
            "emits_notification_events": True,
        }


runtime_notification_centre = RuntimeNotificationCentre()
