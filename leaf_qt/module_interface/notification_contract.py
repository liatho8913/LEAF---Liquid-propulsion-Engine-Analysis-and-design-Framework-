"""
Programme 28J: Engineering Module Notification Contract.

Defines safe structured module notifications/events.

Design rules:
- Modules emit notification events only.
- Modules do not own notification delivery infrastructure.
- No Qt ownership.
- No solver execution.
- No runtime/storage mutation.
- No file writes/deletes/archives.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

from .interface_model import EngineeringModuleInterface


class EngineeringModuleNotificationLevel(str, Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKED = "BLOCKED"


class EngineeringModuleNotificationTopic(str, Enum):
    MODULE_STATUS = "MODULE_STATUS"
    VALIDATION = "VALIDATION"
    REPORT = "REPORT"
    WORKFLOW = "WORKFLOW"
    RUNTIME = "RUNTIME"
    STORAGE = "STORAGE"
    DEPENDENCY = "DEPENDENCY"
    USER_ACTION_REQUIRED = "USER_ACTION_REQUIRED"


class EngineeringModuleNotificationStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EngineeringModuleNotificationEvent:
    module_id: str
    topic: EngineeringModuleNotificationTopic
    level: EngineeringModuleNotificationLevel
    title: str
    message: str
    payload: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.module_id.strip():
            failures.append("module_id is empty")

        if not isinstance(self.topic, EngineeringModuleNotificationTopic):
            failures.append(f"invalid notification topic: {self.topic!r}")

        if not isinstance(self.level, EngineeringModuleNotificationLevel):
            failures.append(f"invalid notification level: {self.level!r}")

        if not self.title.strip():
            failures.append("notification title is empty")

        if not self.message.strip():
            failures.append("notification message is empty")

        return tuple(failures)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "topic": self.topic.value,
            "level": self.level.value,
            "title": self.title,
            "message": self.message,
            "payload": dict(self.payload),
            "source": "engineering_module_notification_contract",
        }


@dataclass(frozen=True)
class EngineeringModuleNotificationResult:
    schema: str
    module_id: str
    status: EngineeringModuleNotificationStatus
    accepted: bool
    event: Dict[str, Any] | None = None
    validation_failures: Tuple[str, ...] = tuple()
    notification_delivered: bool = False
    mutation_performed: bool = False
    solver_executed: bool = False
    runtime_mutation_performed: bool = False
    storage_mutation_performed: bool = False
    file_written: bool = False
    file_deleted: bool = False
    archive_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "module_id": self.module_id,
            "status": self.status.value,
            "accepted": self.accepted,
            "event": dict(self.event or {}),
            "validation_failures": list(self.validation_failures),
            "notification_delivered": self.notification_delivered,
            "mutation_performed": self.mutation_performed,
            "solver_executed": self.solver_executed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "storage_mutation_performed": self.storage_mutation_performed,
            "file_written": self.file_written,
            "file_deleted": self.file_deleted,
            "archive_performed": self.archive_performed,
        }


@dataclass(frozen=True)
class EngineeringModuleNotificationContract:
    interface: EngineeringModuleInterface
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate_contract(self) -> Tuple[str, ...]:
        return tuple(self.interface.validate())

    def build_event(
        self,
        topic: EngineeringModuleNotificationTopic,
        level: EngineeringModuleNotificationLevel,
        title: str,
        message: str,
        payload: Mapping[str, Any] | None = None,
    ) -> EngineeringModuleNotificationEvent:
        return EngineeringModuleNotificationEvent(
            module_id=self.interface.module_id,
            topic=topic,
            level=level,
            title=title,
            message=message,
            payload=dict(payload or {}),
        )

    def emit(self, event: EngineeringModuleNotificationEvent) -> EngineeringModuleNotificationResult:
        failures = list(self.validate_contract())
        failures.extend(event.validate())

        if event.module_id != self.interface.module_id:
            failures.append(
                f"event module_id {event.module_id!r} does not match interface module_id {self.interface.module_id!r}"
            )

        if failures:
            return EngineeringModuleNotificationResult(
                schema="LEAF_ENGINEERING_MODULE_NOTIFICATION_RESULT_PHASE_28J_V1",
                module_id=event.module_id,
                status=EngineeringModuleNotificationStatus.INVALID,
                accepted=False,
                event=None,
                validation_failures=tuple(failures),
                notification_delivered=False,
            )

        payload = event.as_dict()
        payload.update(
            {
                "notification_delivered": False,
                "delivery_owned_by_module": False,
                "mutation_performed": False,
                "solver_executed": False,
                "runtime_mutation_performed": False,
                "storage_mutation_performed": False,
                "file_written": False,
                "file_deleted": False,
                "archive_performed": False,
            }
        )

        return EngineeringModuleNotificationResult(
            schema="LEAF_ENGINEERING_MODULE_NOTIFICATION_RESULT_PHASE_28J_V1",
            module_id=event.module_id,
            status=EngineeringModuleNotificationStatus.ACCEPTED,
            accepted=True,
            event=payload,
            validation_failures=tuple(),
            notification_delivered=False,
            mutation_performed=False,
            solver_executed=False,
            runtime_mutation_performed=False,
            storage_mutation_performed=False,
            file_written=False,
            file_deleted=False,
            archive_performed=False,
        )

    def report(
        self,
        topic: EngineeringModuleNotificationTopic,
        level: EngineeringModuleNotificationLevel,
        title: str,
        message: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        event = self.build_event(
            topic=topic,
            level=level,
            title=title,
            message=message,
            payload=payload,
        )
        result = self.emit(event)

        return {
            "schema": "LEAF_ENGINEERING_MODULE_NOTIFICATION_CONTRACT_PHASE_28J_V1",
            "module_id": self.interface.module_id,
            "contract_validation_failures": list(self.validate_contract()),
            "result": result.as_dict(),
            "delivery_policy": {
                "module_owns_delivery": False,
                "notification_delivered": False,
                "event_only": True,
            },
            "mutation_performed": False,
            "solver_executed": False,
            "runtime_mutation_performed": False,
            "storage_mutation_performed": False,
            "file_written": False,
            "file_deleted": False,
            "archive_performed": False,
        }


def build_engineering_module_notification_contract(
    interface: EngineeringModuleInterface,
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleNotificationContract:
    return EngineeringModuleNotificationContract(
        interface=interface,
        metadata=dict(metadata or {}),
    )
