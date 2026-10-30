"""
Programme 26D: Workflow Execution Context.

Defines the safe execution envelope for LEAF workflows.

Design rules:
- No Qt ownership.
- No solver execution.
- No storage writes.
- No runtime mutation.
- Context only describes whether a workflow step is allowed to execute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

from .graph import WorkflowDependencyGraph, build_workflow_dependency_graph
from .model import WorkflowModel, WorkflowStepStatus


class WorkflowValidationMode(str, Enum):
    PLACEHOLDER_MODE = "PLACEHOLDER_MODE"
    PARTIAL_SOURCE_MODE = "PARTIAL_SOURCE_MODE"
    SOURCED_VALIDATION_MODE = "SOURCED_VALIDATION_MODE"


class WorkflowExecutionPermission(str, Enum):
    ALLOWED = "ALLOWED"
    BLOCKED = "BLOCKED"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"
    UNKNOWN_STEP = "UNKNOWN_STEP"


@dataclass
class WorkflowExecutionContext:
    """
    Reusable workflow execution context.

    This is intentionally module-agnostic. Engineering modules attach identity
    through active_module and metadata, not hardcoded platform branches.
    """

    workflow: WorkflowModel
    current_step_id: str
    active_module: str = "platform"
    validation_mode: WorkflowValidationMode = WorkflowValidationMode.PARTIAL_SOURCE_MODE
    runtime_reference: Optional[str] = None
    storage_reference: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def graph(self) -> WorkflowDependencyGraph:
        return build_workflow_dependency_graph(self.workflow)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.active_module or not self.active_module.strip():
            failures.append("execution_context.active_module is empty")

        if not self.current_step_id or not self.current_step_id.strip():
            failures.append("execution_context.current_step_id is empty")

        if not isinstance(self.validation_mode, WorkflowValidationMode):
            failures.append(
                f"execution_context.validation_mode invalid: {self.validation_mode!r}"
            )

        failures.extend(self.workflow.validate())
        failures.extend(self.graph().validate())

        return failures

    def current_step(self):
        return self.workflow.step_map().get(self.current_step_id)

    def blockers(self) -> List[str]:
        step = self.current_step()
        if step is None:
            return [f"Unknown workflow step: {self.current_step_id}"]

        return list(self.graph().blockers_for(self.current_step_id))

    def permission(self) -> WorkflowExecutionPermission:
        step = self.current_step()

        if step is None:
            return WorkflowExecutionPermission.UNKNOWN_STEP

        if step.status == WorkflowStepStatus.COMPLETE:
            return WorkflowExecutionPermission.COMPLETE

        if step.status == WorkflowStepStatus.FAILED:
            return WorkflowExecutionPermission.FAILED

        if self.blockers():
            return WorkflowExecutionPermission.BLOCKED

        return WorkflowExecutionPermission.ALLOWED

    def can_execute(self) -> bool:
        return self.permission() == WorkflowExecutionPermission.ALLOWED

    def next_ready_steps(self) -> List[str]:
        return list(self.graph().ready_step_ids())

    def report(self) -> Dict[str, Any]:
        step = self.current_step()
        blockers = self.blockers()
        permission = self.permission()

        return {
            "schema": "LEAF_WORKFLOW_EXECUTION_CONTEXT_PHASE_26D_V1",
            "workflow_id": self.workflow.workflow_id,
            "workflow_title": self.workflow.title,
            "active_module": self.active_module,
            "current_step_id": self.current_step_id,
            "current_step_title": step.title if step else None,
            "current_step_status": step.status.value if step else None,
            "validation_mode": self.validation_mode.value,
            "runtime_reference": self.runtime_reference,
            "storage_reference": self.storage_reference,
            "permission": permission.value,
            "can_execute": self.can_execute(),
            "blockers": blockers,
            "next_ready_steps": self.next_ready_steps(),
            "workflow_state": self.workflow.state().value,
            "workflow_progress": self.workflow.progress(),
            "validation_failures": self.validate(),
            "metadata_keys": sorted(self.metadata.keys()),
        }


def build_workflow_execution_context(
    workflow: WorkflowModel,
    current_step_id: str,
    active_module: str = "platform",
    validation_mode: WorkflowValidationMode = WorkflowValidationMode.PARTIAL_SOURCE_MODE,
    runtime_reference: Optional[str] = None,
    storage_reference: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> WorkflowExecutionContext:
    return WorkflowExecutionContext(
        workflow=workflow,
        current_step_id=current_step_id,
        active_module=active_module,
        validation_mode=validation_mode,
        runtime_reference=runtime_reference,
        storage_reference=storage_reference,
        metadata=dict(metadata or {}),
    )
