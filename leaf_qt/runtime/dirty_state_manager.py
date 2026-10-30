from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

from leaf_qt.runtime.event_bus import RuntimeEventBus, runtime_event_bus

SCHEMA = "LEAF_DIRTY_STATE_MANAGER_PHASE_24D_V1"

STATE_SAVED = "saved"
STATE_MODIFIED = "modified"
STATE_UNSAVED = "unsaved"

VALID_DIRTY_STATES = {
    STATE_SAVED,
    STATE_MODIFIED,
    STATE_UNSAVED,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class DirtyStateRecord:
    entity_id: str
    entity_type: str
    state: str
    reason: str
    source: str
    updated_at: str = field(default_factory=utc_now)

    def snapshot(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema"] = "LEAF_DIRTY_STATE_RECORD_PHASE_24D_V1"
        return payload


class DirtyStateManager:
    """
    Shared runtime dirty-state tracker.

    This owns professional saved / modified / unsaved metadata only.

    It does not own:
    - file writing
    - solver payloads
    - report payloads
    - validation payloads
    - Qt widgets
    """

    TRACKED_ENTITY_TYPES = {
        "project",
        "design",
        "workspace",
        "tool",
        "report",
        "graph",
        "station",
        "optimisation",
        "validation",
        "sorting_decision",
    }

    def __init__(self, event_bus: RuntimeEventBus | None = None) -> None:
        self._event_bus = event_bus or runtime_event_bus
        self._records: dict[str, DirtyStateRecord] = {}

    def set_state(
        self,
        entity_id: str,
        entity_type: str,
        state: str,
        reason: str,
        source: str = "dirty_state_manager",
    ) -> DirtyStateRecord:
        if not entity_id:
            raise ValueError("entity_id_required")

        if entity_type not in self.TRACKED_ENTITY_TYPES:
            raise KeyError(f"dirty_entity_type_not_allowed:{entity_type}")

        if state not in VALID_DIRTY_STATES:
            raise ValueError(f"dirty_state_not_allowed:{state}")

        record = DirtyStateRecord(
            entity_id=entity_id,
            entity_type=entity_type,
            state=state,
            reason=reason,
            source=source,
        )

        self._records[entity_id] = record

        self._event_bus.emit(
            "runtime.dirty_state.changed",
            source=source,
            payload=record.snapshot(),
        )

        self._event_bus.emit(
            f"runtime.dirty_state.changed.{entity_type}",
            source=source,
            payload=record.snapshot(),
        )

        return record

    def mark_saved(
        self,
        entity_id: str,
        entity_type: str,
        reason: str = "saved",
        source: str = "dirty_state_manager",
    ) -> DirtyStateRecord:
        return self.set_state(entity_id, entity_type, STATE_SAVED, reason, source)

    def mark_modified(
        self,
        entity_id: str,
        entity_type: str,
        reason: str = "modified",
        source: str = "dirty_state_manager",
    ) -> DirtyStateRecord:
        return self.set_state(entity_id, entity_type, STATE_MODIFIED, reason, source)

    def mark_unsaved(
        self,
        entity_id: str,
        entity_type: str,
        reason: str = "unsaved",
        source: str = "dirty_state_manager",
    ) -> DirtyStateRecord:
        return self.set_state(entity_id, entity_type, STATE_UNSAVED, reason, source)

    def get_state(self, entity_id: str) -> str | None:
        record = self._records.get(entity_id)
        return None if record is None else record.state

    def get_record(self, entity_id: str) -> DirtyStateRecord | None:
        return self._records.get(entity_id)

    def is_dirty(self, entity_id: str) -> bool:
        return self.get_state(entity_id) in {STATE_MODIFIED, STATE_UNSAVED}

    def dirty_records(self) -> list[dict[str, Any]]:
        return [
            record.snapshot()
            for record in self._records.values()
            if record.state in {STATE_MODIFIED, STATE_UNSAVED}
        ]

    def clear_entity(self, entity_id: str) -> bool:
        if entity_id not in self._records:
            return False
        del self._records[entity_id]
        return True

    def rekey_entity(
        self,
        old_entity_id: str,
        new_entity_id: str,
        source: str = "dirty_state_manager",
    ) -> bool:
        """
        Move one tracked entity reference without changing
        its saved/modified/unsaved meaning.
        """
        if (
            old_entity_id
            == new_entity_id
        ):
            return (
                old_entity_id
                in self._records
            )

        current = (
            self._records.get(
                old_entity_id
            )
        )

        if current is None:
            return False

        if (
            new_entity_id
            in self._records
        ):
            raise KeyError(
                "dirty_state_target_entity_already_exists:"
                f"{new_entity_id}"
            )

        updated = DirtyStateRecord(
            entity_id=
                new_entity_id,

            entity_type=
                current.entity_type,

            state=
                current.state,

            reason=
                current.reason,

            source=
                current.source,

            updated_at=
                current.updated_at,
        )

        del self._records[
            old_entity_id
        ]

        self._records[
            new_entity_id
        ] = updated

        self._event_bus.emit(
            "runtime.dirty_state.rekeyed",
            source=source,
            payload={
                "old_entity_id":
                    old_entity_id,

                "new_entity_id":
                    new_entity_id,

                "record":
                    updated.snapshot(),
            },
        )

        return True

    def reset(self) -> None:
        self._records.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "records": {
                entity_id: record.snapshot()
                for entity_id, record in sorted(self._records.items())
            },
            "record_count": len(self._records),
            "dirty_count": len(self.dirty_records()),
            "valid_dirty_states": sorted(VALID_DIRTY_STATES),
            "tracked_entity_types": sorted(self.TRACKED_ENTITY_TYPES),
            "qt_owns_dirty_state": False,
            "stores_solver_payloads": False,
            "stores_report_payloads": False,
            "stores_validation_payloads": False,
            "emits_dirty_state_events": True,
        }


dirty_state_manager = DirtyStateManager()
