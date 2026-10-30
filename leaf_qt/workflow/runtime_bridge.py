"""
Programme 26H: Workflow Runtime Bridge.

Safe bridge between Workflow Platform and Runtime Platform.

Design rules:
- Workflow may request runtime-facing actions.
- This bridge does not directly mutate runtime state.
- Readiness gate must pass before an EXECUTE_STEP request is allowed.
- Runtime internals remain outside workflow ownership.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Tuple

from .execution_context import WorkflowExecutionContext
from .readiness_gate import WorkflowReadinessVerdict, build_workflow_readiness_gate


class WorkflowRuntimeBridgeAction(str, Enum):
    EXECUTE_STEP = "EXECUTE_STEP"
    SET_ACTIVE_STEP = "SET_ACTIVE_STEP"
    EMIT_WORKFLOW_EVENT = "EMIT_WORKFLOW_EVENT"
    REQUEST_RUNTIME_REPORT = "REQUEST_RUNTIME_REPORT"
    NO_OP = "NO_OP"


class WorkflowRuntimeBridgeStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"
    INVALID_CONTEXT = "INVALID_CONTEXT"
    UNSUPPORTED_ACTION = "UNSUPPORTED_ACTION"


@dataclass(frozen=True)
class WorkflowRuntimeBridgeRequest:
    workflow_id: str
    step_id: str
    action: WorkflowRuntimeBridgeAction
    runtime_reference: Optional[str] = None
    payload: Dict[str, Any] | None = None

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.workflow_id or not self.workflow_id.strip():
            failures.append("runtime_bridge_request.workflow_id is empty")

        if not self.step_id or not self.step_id.strip():
            failures.append("runtime_bridge_request.step_id is empty")

        if not isinstance(self.action, WorkflowRuntimeBridgeAction):
            failures.append(f"runtime_bridge_request.action invalid: {self.action!r}")

        return tuple(failures)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "step_id": self.step_id,
            "action": self.action.value,
            "runtime_reference": self.runtime_reference,
            "payload": dict(self.payload or {}),
        }


@dataclass(frozen=True)
class WorkflowRuntimeBridgeResult:
    schema: str
    status: WorkflowRuntimeBridgeStatus
    accepted: bool
    action: str
    workflow_id: str
    step_id: str
    runtime_reference: Optional[str]
    reason: str
    emitted_event: Dict[str, Any] | None
    validation_failures: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "status": self.status.value,
            "accepted": self.accepted,
            "action": self.action,
            "workflow_id": self.workflow_id,
            "step_id": self.step_id,
            "runtime_reference": self.runtime_reference,
            "reason": self.reason,
            "emitted_event": dict(self.emitted_event or {}),
            "validation_failures": list(self.validation_failures),
        }


class WorkflowRuntimeBridge:
    """
    Runtime bridge façade.

    This class intentionally returns structured bridge results instead of
    directly calling runtime mutation methods. Later integration can consume
    emitted_event safely.
    """

    SUPPORTED_ACTIONS = {
        WorkflowRuntimeBridgeAction.EXECUTE_STEP,
        WorkflowRuntimeBridgeAction.SET_ACTIVE_STEP,
        WorkflowRuntimeBridgeAction.EMIT_WORKFLOW_EVENT,
        WorkflowRuntimeBridgeAction.REQUEST_RUNTIME_REPORT,
        WorkflowRuntimeBridgeAction.NO_OP,
    }

    def __init__(self, context: WorkflowExecutionContext) -> None:
        self.context = context
        self.readiness_gate = build_workflow_readiness_gate(context)

    def build_request(
        self,
        action: WorkflowRuntimeBridgeAction,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> WorkflowRuntimeBridgeRequest:
        return WorkflowRuntimeBridgeRequest(
            workflow_id=self.context.workflow.workflow_id,
            step_id=self.context.current_step_id,
            action=action,
            runtime_reference=self.context.runtime_reference,
            payload=dict(payload or {}),
        )

    def submit(self, request: WorkflowRuntimeBridgeRequest) -> WorkflowRuntimeBridgeResult:
        request_failures = list(request.validate())
        context_failures = list(self.context.validate())
        readiness = self.readiness_gate.evaluate()

        failures = request_failures + context_failures

        if request.action not in self.SUPPORTED_ACTIONS:
            return self._result(
                request=request,
                status=WorkflowRuntimeBridgeStatus.UNSUPPORTED_ACTION,
                accepted=False,
                reason=f"Unsupported workflow runtime bridge action: {request.action!r}",
                emitted_event=None,
                failures=tuple(failures),
            )

        if failures:
            return self._result(
                request=request,
                status=WorkflowRuntimeBridgeStatus.INVALID_CONTEXT,
                accepted=False,
                reason="Runtime bridge request or execution context failed validation.",
                emitted_event=None,
                failures=tuple(failures),
            )

        if request.action == WorkflowRuntimeBridgeAction.NO_OP:
            return self._result(
                request=request,
                status=WorkflowRuntimeBridgeStatus.ACCEPTED,
                accepted=True,
                reason="No-op runtime bridge request accepted.",
                emitted_event=self._event(request, "workflow.runtime.no_op"),
                failures=tuple(),
            )

        if request.action == WorkflowRuntimeBridgeAction.EXECUTE_STEP:
            if readiness.verdict != WorkflowReadinessVerdict.READY:
                return self._result(
                    request=request,
                    status=WorkflowRuntimeBridgeStatus.BLOCKED,
                    accepted=False,
                    reason=(
                        "Execution request blocked by workflow readiness gate: "
                        f"{readiness.verdict.value}"
                    ),
                    emitted_event=None,
                    failures=tuple(),
                )

            return self._result(
                request=request,
                status=WorkflowRuntimeBridgeStatus.ACCEPTED,
                accepted=True,
                reason="Execution request accepted by workflow readiness gate.",
                emitted_event=self._event(request, "workflow.runtime.execute_step_requested"),
                failures=tuple(),
            )

        return self._result(
            request=request,
            status=WorkflowRuntimeBridgeStatus.ACCEPTED,
            accepted=True,
            reason="Runtime bridge request accepted as a safe structured event.",
            emitted_event=self._event(request, f"workflow.runtime.{request.action.value.lower()}"),
            failures=tuple(),
        )

    def _event(
        self,
        request: WorkflowRuntimeBridgeRequest,
        event_type: str,
    ) -> Dict[str, Any]:
        return {
            "event_type": event_type,
            "workflow_id": request.workflow_id,
            "step_id": request.step_id,
            "action": request.action.value,
            "runtime_reference": request.runtime_reference,
            "payload": dict(request.payload or {}),
            "source": "workflow_runtime_bridge",
            "mutation_performed": False,
        }

    def _result(
        self,
        request: WorkflowRuntimeBridgeRequest,
        status: WorkflowRuntimeBridgeStatus,
        accepted: bool,
        reason: str,
        emitted_event: Dict[str, Any] | None,
        failures: Tuple[str, ...],
    ) -> WorkflowRuntimeBridgeResult:
        return WorkflowRuntimeBridgeResult(
            schema="LEAF_WORKFLOW_RUNTIME_BRIDGE_PHASE_26H_V1",
            status=status,
            accepted=accepted,
            action=request.action.value if isinstance(request.action, WorkflowRuntimeBridgeAction) else str(request.action),
            workflow_id=request.workflow_id,
            step_id=request.step_id,
            runtime_reference=request.runtime_reference,
            reason=reason,
            emitted_event=emitted_event,
            validation_failures=failures,
        )

    def report(self, request: WorkflowRuntimeBridgeRequest) -> Dict[str, Any]:
        result = self.submit(request)
        return {
            "schema": "LEAF_WORKFLOW_RUNTIME_BRIDGE_REPORT_PHASE_26H_V1",
            "request": request.as_dict(),
            "result": result.as_dict(),
            "readiness": self.readiness_gate.evaluate().as_dict(),
            "context": self.context.report(),
        }


def build_workflow_runtime_bridge(context: WorkflowExecutionContext) -> WorkflowRuntimeBridge:
    return WorkflowRuntimeBridge(context)
