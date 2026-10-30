from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from leaf_qt.runtime.event_bus import RuntimeEventBus, runtime_event_bus

SCHEMA = "LEAF_RUNTIME_STATE_REGISTRY_PHASE_24C_V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RuntimeStateChange:
    key: str
    old_value: Any
    new_value: Any
    source: str
    changed_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_RUNTIME_STATE_CHANGE_PHASE_24C_V1"
        return payload


class RuntimeStateRegistry:
    """
    Central registry for active LEAF runtime references.

    This is reference-state only.

    It does not own:
    - solver payloads
    - report payloads
    - validation payloads
    - Qt widgets
    - repository sorting execution
    """

    ALLOWED_KEYS = {
        "active_project",
        "active_design",
        "current_workspace",
        "current_tool",
        "current_graph",
        "current_station",
        "current_report",
        "current_optimisation",
        "current_validation",
    }

    def __init__(self, event_bus: RuntimeEventBus | None = None) -> None:
        self._event_bus = event_bus or runtime_event_bus
        self._state: dict[str, Any] = {key: None for key in sorted(self.ALLOWED_KEYS)}
        self._changes: list[RuntimeStateChange] = []

    def set(self, key: str, value: Any, source: str = "runtime_state_registry") -> RuntimeStateChange:
        if key not in self.ALLOWED_KEYS:
            raise KeyError(f"runtime_state_key_not_allowed:{key}")

        old_value = self._state.get(key)

        change = RuntimeStateChange(
            key=key,
            old_value=old_value,
            new_value=value,
            source=source,
        )

        self._state[key] = value
        self._changes.append(change)

        self._event_bus.emit(
            "runtime.state.changed",
            source=source,
            payload=change.snapshot(),
        )

        self._event_bus.emit(
            f"runtime.state.changed.{key}",
            source=source,
            payload=change.snapshot(),
        )

        return change

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self.ALLOWED_KEYS:
            raise KeyError(f"runtime_state_key_not_allowed:{key}")
        return self._state.get(key, default)

    def clear(self, key: str, source: str = "runtime_state_registry") -> RuntimeStateChange:
        return self.set(key, None, source=source)

    def reset(self, source: str = "runtime_state_registry") -> list[RuntimeStateChange]:
        changes: list[RuntimeStateChange] = []

        for key in sorted(self.ALLOWED_KEYS):
            if self._state.get(key) is not None:
                changes.append(self.clear(key, source=source))

        return changes

    def changes(self) -> list[dict[str, Any]]:
        return [change.snapshot() for change in self._changes]

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "state": dict(self._state),
            "allowed_keys": sorted(self.ALLOWED_KEYS),
            "change_count": len(self._changes),
            "qt_owns_runtime_state": False,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
            "emits_state_events": True,
        }


runtime_state_registry = RuntimeStateRegistry()
