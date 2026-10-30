from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from leaf_qt.runtime.event_bus import RuntimeEventBus, runtime_event_bus

SCHEMA = "LEAF_UNDO_REDO_INFRASTRUCTURE_PHASE_24E_V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RuntimeCommand:
    command_id: str
    command_type: str
    target_id: str
    target_type: str
    description: str
    do_payload: dict[str, Any] = field(default_factory=dict)
    undo_payload: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_RUNTIME_COMMAND_PHASE_24E_V1"
        return payload


class UndoRedoManager:
    """
    Shared runtime undo / redo infrastructure.

    This stores command metadata and delegates execution to registered handlers.

    It does not own:
    - Qt widgets
    - solver payloads
    - report payloads
    - validation payloads
    - file writing
    """

    TARGET_TYPES = {
        "project",
        "design",
        "workspace",
        "tool",
        "report",
        "graph",
        "station",
        "geometry",
        "material",
        "validation",
        "optimisation",
        "sorting_decision",
    }

    def __init__(
        self,
        event_bus: RuntimeEventBus | None = None,
        max_history: int = 250,
    ) -> None:
        self._event_bus = event_bus or runtime_event_bus
        self._max_history = max_history
        self._undo_stack: list[RuntimeCommand] = []
        self._redo_stack: list[RuntimeCommand] = []
        self._do_handlers: dict[str, Callable[[RuntimeCommand], None]] = {}
        self._undo_handlers: dict[str, Callable[[RuntimeCommand], None]] = {}

    def register_handler(
        self,
        command_type: str,
        do_handler: Callable[[RuntimeCommand], None],
        undo_handler: Callable[[RuntimeCommand], None],
    ) -> None:
        if not command_type:
            raise ValueError("command_type_required")

        if not callable(do_handler):
            raise TypeError("do_handler_must_be_callable")

        if not callable(undo_handler):
            raise TypeError("undo_handler_must_be_callable")

        self._do_handlers[command_type] = do_handler
        self._undo_handlers[command_type] = undo_handler

    def create_command(
        self,
        command_type: str,
        target_id: str,
        target_type: str,
        description: str,
        do_payload: dict[str, Any] | None = None,
        undo_payload: dict[str, Any] | None = None,
    ) -> RuntimeCommand:
        if target_type not in self.TARGET_TYPES:
            raise KeyError(f"undo_target_type_not_allowed:{target_type}")

        if not target_id:
            raise ValueError("target_id_required")

        if not command_type:
            raise ValueError("command_type_required")

        return RuntimeCommand(
            command_id=f"cmd_{uuid4().hex[:16]}",
            command_type=command_type,
            target_id=target_id,
            target_type=target_type,
            description=description,
            do_payload=dict(do_payload or {}),
            undo_payload=dict(undo_payload or {}),
        )

    def execute(self, command: RuntimeCommand) -> RuntimeCommand:
        handler = self._do_handlers.get(command.command_type)

        if handler is None:
            raise KeyError(f"do_handler_missing:{command.command_type}")

        handler(command)

        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._trim_history()

        self._event_bus.emit(
            "runtime.undo_redo.command_executed",
            source="undo_redo_manager",
            payload=command.snapshot(),
        )

        return command

    def undo(self) -> RuntimeCommand:
        if not self._undo_stack:
            raise RuntimeError("undo_stack_empty")

        command = self._undo_stack.pop()
        handler = self._undo_handlers.get(command.command_type)

        if handler is None:
            self._undo_stack.append(command)
            raise KeyError(f"undo_handler_missing:{command.command_type}")

        handler(command)
        self._redo_stack.append(command)

        self._event_bus.emit(
            "runtime.undo_redo.command_undone",
            source="undo_redo_manager",
            payload=command.snapshot(),
        )

        return command

    def redo(self) -> RuntimeCommand:
        if not self._redo_stack:
            raise RuntimeError("redo_stack_empty")

        command = self._redo_stack.pop()
        handler = self._do_handlers.get(command.command_type)

        if handler is None:
            self._redo_stack.append(command)
            raise KeyError(f"do_handler_missing:{command.command_type}")

        handler(command)
        self._undo_stack.append(command)
        self._trim_history()

        self._event_bus.emit(
            "runtime.undo_redo.command_redone",
            source="undo_redo_manager",
            payload=command.snapshot(),
        )

        return command

    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()

        self._event_bus.emit(
            "runtime.undo_redo.history_cleared",
            source="undo_redo_manager",
            payload={},
        )

    def _trim_history(self) -> None:
        if len(self._undo_stack) > self._max_history:
            self._undo_stack = self._undo_stack[-self._max_history :]

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "undo_count": len(self._undo_stack),
            "redo_count": len(self._redo_stack),
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "max_history": self._max_history,
            "registered_command_types": sorted(self._do_handlers),
            "undo_stack": [command.snapshot() for command in self._undo_stack],
            "redo_stack": [command.snapshot() for command in self._redo_stack],
            "target_types": sorted(self.TARGET_TYPES),
            "qt_owns_undo_redo": False,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
            "emits_undo_redo_events": True,
        }


undo_redo_manager = UndoRedoManager()
