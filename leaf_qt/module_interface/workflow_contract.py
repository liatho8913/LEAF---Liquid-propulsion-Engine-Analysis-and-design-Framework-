"""
Programme 28G: Engineering Module Workflow Contract.

Connects engineering module interfaces to the Programme 26 Workflow Platform.

Design rules:
- Reuse workflow model, registry, graph, progress, readiness, and recommendations.
- No solver execution.
- No Qt ownership.
- No runtime mutation.
- No storage mutation.
- No bespoke module workflow logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from typing import Any, Dict, Iterable, Mapping, Tuple

from leaf_qt.workflow import (
    WorkflowDependency,
    WorkflowExecutionContext,
    WorkflowStep,
    WorkflowStepStatus,
    build_workflow_execution_context,
    build_workflow_model,
    build_workflow_progress_tracker,
    build_workflow_readiness_gate,
    build_workflow_recommendation_engine,
)

from .interface_model import EngineeringModuleInterface


@dataclass(frozen=True)
class EngineeringModuleWorkflowStepDefinition:
    step_id: str
    title: str
    description: str
    dependencies: Tuple[str, ...] = dataclass_field(default_factory=tuple)
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.step_id.strip():
            failures.append("workflow step_id is empty")

        if not self.title.strip():
            failures.append(f"workflow title is empty for step {self.step_id!r}")

        if not self.description.strip():
            failures.append(f"workflow description is empty for step {self.step_id!r}")

        if self.step_id in self.dependencies:
            failures.append(f"workflow step {self.step_id!r} depends on itself")

        return tuple(failures)

    def build_step(
        self,
        owner: str,
        status: WorkflowStepStatus = WorkflowStepStatus.NOT_STARTED,
    ) -> WorkflowStep:
        return WorkflowStep(
            step_id=self.step_id,
            title=self.title,
            description=self.description,
            owner=owner,
            status=status,
            dependencies=tuple(
                WorkflowDependency(
                    required_step_id=dependency,
                    reason=f"{self.step_id} requires {dependency} to complete first.",
                )
                for dependency in self.dependencies
            ),
            metadata=dict(self.metadata),
        )


@dataclass(frozen=True)
class EngineeringModuleWorkflowContract:
    interface: EngineeringModuleInterface
    workflow_id: str
    workflow_title: str
    step_definitions: Tuple[EngineeringModuleWorkflowStepDefinition, ...]
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate_contract(self) -> Tuple[str, ...]:
        failures = []
        failures.extend(self.interface.validate())

        if not self.workflow_id.strip():
            failures.append("workflow_id is empty")

        if not self.workflow_title.strip():
            failures.append("workflow_title is empty")

        if not self.step_definitions:
            failures.append("workflow contract has no step definitions")

        seen = set()
        step_ids = {step.step_id for step in self.step_definitions}

        for step in self.step_definitions:
            failures.extend(step.validate())
            if step.step_id in seen:
                failures.append(f"duplicate workflow step_id: {step.step_id}")
            seen.add(step.step_id)

            for dependency in step.dependencies:
                if dependency not in step_ids:
                    failures.append(
                        f"workflow step {step.step_id!r} depends on missing step {dependency!r}"
                    )

        return tuple(failures)

    def build_workflow(
        self,
        statuses: Mapping[str, WorkflowStepStatus] | None = None,
    ):
        status_map = dict(statuses or {})
        steps = tuple(
            definition.build_step(
                owner=self.interface.module_id,
                status=status_map.get(definition.step_id, WorkflowStepStatus.NOT_STARTED),
            )
            for definition in self.step_definitions
        )

        return build_workflow_model(
            workflow_id=self.workflow_id,
            title=self.workflow_title,
            description=f"Workflow contract for engineering module {self.interface.module_id}.",
            steps=steps,
            metadata={
                "module_id": self.interface.module_id,
                "contract": "engineering_module_workflow_contract",
                **dict(self.metadata),
            },
        )

    def build_context(
        self,
        current_step_id: str,
        statuses: Mapping[str, WorkflowStepStatus] | None = None,
    ) -> WorkflowExecutionContext:
        return build_workflow_execution_context(
            workflow=self.build_workflow(statuses=statuses),
            current_step_id=current_step_id,
            active_module=self.interface.module_id,
            metadata={
                "contract": "engineering_module_workflow_contract",
                **dict(self.metadata),
            },
        )

    def report(
        self,
        current_step_id: str,
        statuses: Mapping[str, WorkflowStepStatus] | None = None,
    ) -> Dict[str, Any]:
        workflow = self.build_workflow(statuses=statuses)
        context = build_workflow_execution_context(
            workflow=workflow,
            current_step_id=current_step_id,
            active_module=self.interface.module_id,
        )

        progress = build_workflow_progress_tracker(workflow).snapshot().as_dict()
        readiness = build_workflow_readiness_gate(context).evaluate().as_dict()
        recommendation = build_workflow_recommendation_engine(context).recommend().as_dict()

        return {
            "schema": "LEAF_ENGINEERING_MODULE_WORKFLOW_CONTRACT_PHASE_28G_V1",
            "module_id": self.interface.module_id,
            "workflow_id": self.workflow_id,
            "workflow_title": self.workflow_title,
            "contract_validation_failures": list(self.validate_contract()),
            "workflow": workflow.report(),
            "progress": progress,
            "readiness": readiness,
            "recommendation": recommendation,
            "mutation_performed": False,
            "solver_executed": False,
            "runtime_mutation_performed": False,
            "storage_mutation_performed": False,
        }


def default_engineering_module_workflow_steps() -> Tuple[EngineeringModuleWorkflowStepDefinition, ...]:
    return (
        EngineeringModuleWorkflowStepDefinition(
            step_id="define_inputs",
            title="Define Module Inputs",
            description="Define and validate engineering module inputs.",
        ),
        EngineeringModuleWorkflowStepDefinition(
            step_id="run_module_solver",
            title="Run Module Solver",
            description="Execute or request the module solver through the approved adapter layer.",
            dependencies=("define_inputs",),
        ),
        EngineeringModuleWorkflowStepDefinition(
            step_id="validate_module_outputs",
            title="Validate Module Outputs",
            description="Validate outputs through the module validation contract.",
            dependencies=("run_module_solver",),
        ),
        EngineeringModuleWorkflowStepDefinition(
            step_id="produce_module_report",
            title="Produce Module Report",
            description="Produce owned report output through the module report contract.",
            dependencies=("validate_module_outputs",),
        ),
        EngineeringModuleWorkflowStepDefinition(
            step_id="store_module_design",
            title="Store Module Design",
            description="Prepare design storage through canonical storage integration.",
            dependencies=("produce_module_report",),
        ),
    )


def build_engineering_module_workflow_contract(
    interface: EngineeringModuleInterface,
    workflow_id: str | None = None,
    workflow_title: str | None = None,
    step_definitions: Iterable[EngineeringModuleWorkflowStepDefinition] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleWorkflowContract:
    return EngineeringModuleWorkflowContract(
        interface=interface,
        workflow_id=workflow_id or f"{interface.module_id}_workflow",
        workflow_title=workflow_title or f"{interface.title} Workflow",
        step_definitions=tuple(step_definitions or default_engineering_module_workflow_steps()),
        metadata=dict(metadata or {}),
    )
