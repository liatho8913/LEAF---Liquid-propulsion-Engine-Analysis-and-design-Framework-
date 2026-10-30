"""
Programme 28H: Engineering Module Runtime Contract.

Defines how engineering modules request runtime-facing actions safely.

Design rules:
- Runtime request contract only.
- No direct runtime mutation.
- No solver execution.
- No storage mutation.
- No Qt ownership.
- Runtime actions are emitted as structured requests/events.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

from .interface_model import EngineeringModuleInterface


class EngineeringModuleRuntimeAction(str, Enum):
    SET_ACTIVE_MODULE = "SET_ACTIVE_MODULE"
    REQUEST_SOLVER_EXECUTION = "REQUEST_SOLVER_EXECUTION"
    REQUEST_VALIDATION = "REQUEST_VALIDATION"
    REQUEST_REPORT_REFRESH = "REQUEST_REPORT_REFRESH"
    REQUEST_STATE_SNAPSHOT = "REQUEST_STATE_SNAPSHOT"
    EMIT_MODULE_EVENT = "EMIT_MODULE_EVENT"
    NO_OP = "NO_OP"


class EngineeringModuleRuntimeRequestStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


@dataclass(frozen=True)
class EngineeringModuleRuntimeRequest:
    module_id: str
    action: EngineeringModuleRuntimeAction
    payload: Dict[str, Any] = dataclass_field(default_factory=dict)
    runtime_reference: str | None = None

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.module_id.strip():
            failures.append("module_id is empty")

        if not isinstance(self.action, EngineeringModuleRuntimeAction):
            failures.append(f"invalid runtime action: {self.action!r}")

        return tuple(failures)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "action": self.action.value,
            "payload": dict(self.payload),
            "runtime_reference": self.runtime_reference,
        }


@dataclass(frozen=True)
class EngineeringModuleRuntimeResult:
    schema: str
    module_id: str
    action: str
    status: EngineeringModuleRuntimeRequestStatus
    accepted: bool
    reason: str
    emitted_event: Dict[str, Any] | None = None
    validation_failures: Tuple[str, ...] = tuple()
    mutation_performed: bool = False
    solver_executed: bool = False
    runtime_mutation_performed: bool = False
    storage_mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "module_id": self.module_id,
            "action": self.action,
            "status": self.status.value,
            "accepted": self.accepted,
            "reason": self.reason,
            "emitted_event": dict(self.emitted_event or {}),
            "validation_failures": list(self.validation_failures),
            "mutation_performed": self.mutation_performed,
            "solver_executed": self.solver_executed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "storage_mutation_performed": self.storage_mutation_performed,
        }


@dataclass(frozen=True)
class EngineeringModuleRuntimeContract:
    interface: EngineeringModuleInterface
    runtime_reference: str | None = None
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate_contract(self) -> Tuple[str, ...]:
        failures = []
        failures.extend(self.interface.validate())

        if self.runtime_reference is not None and not self.runtime_reference.strip():
            failures.append("runtime_reference is empty")

        return tuple(failures)

    def build_request(
        self,
        action: EngineeringModuleRuntimeAction,
        payload: Mapping[str, Any] | None = None,
    ) -> EngineeringModuleRuntimeRequest:
        return EngineeringModuleRuntimeRequest(
            module_id=self.interface.module_id,
            action=action,
            payload=dict(payload or {}),
            runtime_reference=self.runtime_reference,
        )

    def submit(self, request: EngineeringModuleRuntimeRequest) -> EngineeringModuleRuntimeResult:
        failures = list(self.validate_contract())
        failures.extend(request.validate())

        if request.module_id != self.interface.module_id:
            failures.append(
                f"request module_id {request.module_id!r} does not match interface module_id {self.interface.module_id!r}"
            )

        if failures:
            return EngineeringModuleRuntimeResult(
                schema="LEAF_ENGINEERING_MODULE_RUNTIME_RESULT_PHASE_28H_V1",
                module_id=request.module_id,
                action=request.action.value if isinstance(request.action, EngineeringModuleRuntimeAction) else str(request.action),
                status=EngineeringModuleRuntimeRequestStatus.INVALID,
                accepted=False,
                reason="Runtime request failed contract validation.",
                emitted_event=None,
                validation_failures=tuple(failures),
                mutation_performed=False,
                solver_executed=False,
                runtime_mutation_performed=False,
                storage_mutation_performed=False,
            )

        event_type = f"engineering_module.runtime.{request.action.value.lower()}"

        if request.action == EngineeringModuleRuntimeAction.NO_OP:
            reason = "No-op runtime request accepted."
        else:
            reason = "Runtime request accepted as a structured non-mutating event."

        return EngineeringModuleRuntimeResult(
            schema="LEAF_ENGINEERING_MODULE_RUNTIME_RESULT_PHASE_28H_V1",
            module_id=request.module_id,
            action=request.action.value,
            status=EngineeringModuleRuntimeRequestStatus.ACCEPTED,
            accepted=True,
            reason=reason,
            emitted_event={
                "event_type": event_type,
                "module_id": request.module_id,
                "action": request.action.value,
                "runtime_reference": request.runtime_reference,
                "payload": dict(request.payload),
                "source": "engineering_module_runtime_contract",
                "mutation_performed": False,
                "solver_executed": False,
                "runtime_mutation_performed": False,
                "storage_mutation_performed": False,
            },
            validation_failures=tuple(),
            mutation_performed=False,
            solver_executed=False,
            runtime_mutation_performed=False,
            storage_mutation_performed=False,
        )

    def report(
        self,
        action: EngineeringModuleRuntimeAction,
        payload: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        request = self.build_request(action=action, payload=payload)
        result = self.submit(request)

        return {
            "schema": "LEAF_ENGINEERING_MODULE_RUNTIME_CONTRACT_PHASE_28H_V1",
            "module_id": self.interface.module_id,
            "runtime_reference": self.runtime_reference,
            "request": request.as_dict(),
            "result": result.as_dict(),
            "contract_validation_failures": list(self.validate_contract()),
            "mutation_performed": False,
            "solver_executed": False,
            "runtime_mutation_performed": False,
            "storage_mutation_performed": False,
        }


def build_engineering_module_runtime_contract(
    interface: EngineeringModuleInterface,
    runtime_reference: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleRuntimeContract:
    return EngineeringModuleRuntimeContract(
        interface=interface,
        runtime_reference=runtime_reference,
        metadata=dict(metadata or {}),
    )
