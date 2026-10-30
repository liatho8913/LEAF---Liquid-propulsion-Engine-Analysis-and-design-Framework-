from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from leaf_qt.runtime.event_bus import RuntimeEventBus, runtime_event_bus

SCHEMA = "LEAF_RUNTIME_REPORT_ROUTER_PHASE_24F_V1"

ROUTE_DIAGNOSTIC = "diagnostic"
ROUTE_VALIDATION = "validation"
ROUTE_REPORT = "report"
ROUTE_WARNING = "warning"
ROUTE_RECOMMENDATION = "recommendation"

VALID_REPORT_ROUTES = {
    ROUTE_DIAGNOSTIC,
    ROUTE_VALIDATION,
    ROUTE_REPORT,
    ROUTE_WARNING,
    ROUTE_RECOMMENDATION,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RuntimeReportMessage:
    message_id: str
    route: str
    source: str
    title: str
    summary: str
    severity: str = "info"
    target_id: str | None = None
    target_type: str | None = None
    payload_ref: str | None = None
    created_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_RUNTIME_REPORT_MESSAGE_PHASE_24F_V1"
        return payload


class RuntimeReportRouter:
    """
    Shared runtime report-routing layer.

    This owns routing metadata only.

    It does not own:
    - report file writing
    - validation execution
    - solver payloads
    - Qt widgets
    """

    VALID_SEVERITIES = {
        "debug",
        "info",
        "success",
        "warning",
        "error",
        "critical",
    }

    def __init__(
        self,
        event_bus: RuntimeEventBus | None = None,
        retain_history: bool = True,
        max_history: int = 500,
    ) -> None:
        self._event_bus = event_bus or runtime_event_bus
        self._retain_history = retain_history
        self._max_history = max_history
        self._history: list[RuntimeReportMessage] = []

    def route_message(
        self,
        route: str,
        source: str,
        title: str,
        summary: str,
        severity: str = "info",
        target_id: str | None = None,
        target_type: str | None = None,
        payload_ref: str | None = None,
    ) -> RuntimeReportMessage:
        if route not in VALID_REPORT_ROUTES:
            raise KeyError(f"report_route_not_allowed:{route}")

        if severity not in self.VALID_SEVERITIES:
            raise ValueError(f"report_severity_not_allowed:{severity}")

        if not source:
            raise ValueError("source_required")

        if not title:
            raise ValueError("title_required")

        message = RuntimeReportMessage(
            message_id=f"report_msg_{uuid4().hex[:16]}",
            route=route,
            source=source,
            title=title,
            summary=summary,
            severity=severity,
            target_id=target_id,
            target_type=target_type,
            payload_ref=payload_ref,
        )

        if self._retain_history:
            self._history.append(message)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history :]

        self._event_bus.emit(
            "runtime.report.routed",
            source=source,
            payload=message.snapshot(),
        )

        self._event_bus.emit(
            f"runtime.report.routed.{route}",
            source=source,
            payload=message.snapshot(),
        )

        return message

    def diagnostic(self, source: str, title: str, summary: str, **kwargs: Any) -> RuntimeReportMessage:
        return self.route_message(ROUTE_DIAGNOSTIC, source, title, summary, **kwargs)

    def validation(self, source: str, title: str, summary: str, **kwargs: Any) -> RuntimeReportMessage:
        return self.route_message(ROUTE_VALIDATION, source, title, summary, **kwargs)

    def report(self, source: str, title: str, summary: str, **kwargs: Any) -> RuntimeReportMessage:
        return self.route_message(ROUTE_REPORT, source, title, summary, **kwargs)

    def warning(self, source: str, title: str, summary: str, **kwargs: Any) -> RuntimeReportMessage:
        return self.route_message(ROUTE_WARNING, source, title, summary, severity=kwargs.pop("severity", "warning"), **kwargs)

    def recommendation(self, source: str, title: str, summary: str, **kwargs: Any) -> RuntimeReportMessage:
        return self.route_message(ROUTE_RECOMMENDATION, source, title, summary, **kwargs)

    def history(self, route: str | None = None) -> list[dict[str, Any]]:
        messages = self._history
        if route is not None:
            messages = [message for message in messages if message.route == route]
        return [message.snapshot() for message in messages]

    def clear_history(self) -> None:
        self._history.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "valid_routes": sorted(VALID_REPORT_ROUTES),
            "valid_severities": sorted(self.VALID_SEVERITIES),
            "retain_history": self._retain_history,
            "max_history": self._max_history,
            "history_count": len(self._history),
            "route_counts": {
                route: sum(1 for message in self._history if message.route == route)
                for route in sorted(VALID_REPORT_ROUTES)
            },
            "qt_owns_report_routing": False,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
            "emits_report_route_events": True,
        }


runtime_report_router = RuntimeReportRouter()
