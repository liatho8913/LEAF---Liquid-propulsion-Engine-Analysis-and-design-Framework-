"""
Programme 26B: Workflow Step Registry.

Reusable registry for workflow step definitions.

Design rules:
- Registry owns reusable step definitions.
- WorkflowModel owns workflow instances.
- Engineering modules should register steps here instead of hardcoding local step shapes.
- No Qt ownership.
- No storage/runtime/report side effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .model import WorkflowDependency, WorkflowStep, WorkflowStepStatus


@dataclass(frozen=True)
class WorkflowStepDefinition:
    """
    Canonical reusable definition for a workflow step.

    A definition is not a live workflow step. It is a template used to build
    workflow steps consistently across LEAF modules.
    """

    step_id: str
    title: str
    description: str = ""
    owner: str = "platform"
    default_status: WorkflowStepStatus = WorkflowStepStatus.NOT_STARTED
    dependencies: Tuple[WorkflowDependency, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.step_id or not self.step_id.strip():
            failures.append("step_definition.step_id is empty")

        if not self.title or not self.title.strip():
            failures.append(f"step_definition.title is empty for {self.step_id!r}")

        if not self.owner or not self.owner.strip():
            failures.append(f"step_definition.owner is empty for {self.step_id!r}")

        if not isinstance(self.default_status, WorkflowStepStatus):
            failures.append(
                f"step_definition.default_status invalid for {self.step_id!r}: "
                f"{self.default_status!r}"
            )

        for dependency in self.dependencies:
            failures.extend(dependency.validate())

        return failures

    def build_step(
        self,
        status: Optional[WorkflowStepStatus] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> WorkflowStep:
        combined_metadata = dict(self.metadata)
        combined_metadata.update(dict(metadata or {}))

        return WorkflowStep(
            step_id=self.step_id,
            title=self.title,
            description=self.description,
            owner=self.owner,
            status=status or self.default_status,
            dependencies=self.dependencies,
            metadata=combined_metadata,
        )


class WorkflowStepRegistry:
    """
    Reusable registry of workflow step definitions.

    The registry prevents scattered workflow constants and supports later
    dependency graph, readiness gate, recommendation, report, and runtime phases.
    """

    def __init__(self, registry_id: str = "leaf_workflow_step_registry") -> None:
        self.registry_id = registry_id
        self._definitions: Dict[str, WorkflowStepDefinition] = {}

    def register(self, definition: WorkflowStepDefinition, replace: bool = False) -> None:
        failures = definition.validate()
        if failures:
            raise ValueError("; ".join(failures))

        if definition.step_id in self._definitions and not replace:
            raise ValueError(f"workflow step definition already registered: {definition.step_id}")

        self._definitions[definition.step_id] = definition

    def register_many(
        self,
        definitions: Iterable[WorkflowStepDefinition],
        replace: bool = False,
    ) -> None:
        for definition in definitions:
            self.register(definition, replace=replace)

    def has(self, step_id: str) -> bool:
        return step_id in self._definitions

    def get(self, step_id: str) -> WorkflowStepDefinition:
        try:
            return self._definitions[step_id]
        except KeyError as exc:
            raise KeyError(f"unknown workflow step definition: {step_id}") from exc

    def all_definitions(self) -> Tuple[WorkflowStepDefinition, ...]:
        """
        Return definitions in registration order.

        Workflow order is meaningful. We intentionally preserve insertion order
        instead of sorting alphabetically so process sequences remain readable
        and predictable.
        """
        return tuple(self._definitions.values())

    def build_step(
        self,
        step_id: str,
        status: Optional[WorkflowStepStatus] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> WorkflowStep:
        return self.get(step_id).build_step(status=status, metadata=metadata)

    def build_steps(
        self,
        step_ids: Iterable[str],
        statuses: Optional[Mapping[str, WorkflowStepStatus]] = None,
    ) -> Tuple[WorkflowStep, ...]:
        status_map = dict(statuses or {})
        return tuple(
            self.build_step(step_id, status=status_map.get(step_id))
            for step_id in step_ids
        )

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.registry_id or not self.registry_id.strip():
            failures.append("registry.registry_id is empty")

        for definition in self.all_definitions():
            failures.extend(definition.validate())

            for dependency in definition.dependencies:
                if dependency.required_step_id not in self._definitions:
                    failures.append(
                        f"definition {definition.step_id!r} depends on unregistered "
                        f"definition {dependency.required_step_id!r}"
                    )

        failures.extend(self._detect_cycles())

        return failures

    def _detect_cycles(self) -> List[str]:
        failures: List[str] = []
        graph = {
            definition.step_id: tuple(
                dependency.required_step_id for dependency in definition.dependencies
            )
            for definition in self.all_definitions()
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(step_id: str, trail: Tuple[str, ...]) -> None:
            if step_id in visited:
                return
            if step_id in visiting:
                failures.append(
                    "workflow registry dependency cycle detected: "
                    + " -> ".join((*trail, step_id))
                )
                return

            visiting.add(step_id)
            for dependency_id in graph.get(step_id, ()):
                if dependency_id in graph:
                    visit(dependency_id, (*trail, step_id))
            visiting.remove(step_id)
            visited.add(step_id)

        for step_id in graph:
            visit(step_id, tuple())

        return failures

    def report(self) -> Dict[str, Any]:
        failures = self.validate()

        return {
            "schema": "LEAF_WORKFLOW_STEP_REGISTRY_PHASE_26B_V1",
            "registry_id": self.registry_id,
            "definition_count": len(self._definitions),
            "validation_failures": failures,
            "definitions": [
                {
                    "step_id": definition.step_id,
                    "title": definition.title,
                    "owner": definition.owner,
                    "default_status": definition.default_status.value,
                    "dependencies": [
                        dependency.required_step_id
                        for dependency in definition.dependencies
                    ],
                    "metadata_keys": sorted(definition.metadata.keys()),
                }
                for definition in self.all_definitions()
            ],
        }


def build_default_engineering_step_registry() -> WorkflowStepRegistry:
    """
    Default platform workflow steps.

    These are deliberately generic engineering-process steps, not regen-specific
    or Qt-specific steps.
    """

    registry = WorkflowStepRegistry()

    registry.register_many(
        [
            WorkflowStepDefinition(
                step_id="define_inputs",
                title="Define Inputs",
                description="Collect and validate the required engineering inputs.",
                owner="workflow_platform",
                default_status=WorkflowStepStatus.NOT_STARTED,
                metadata={"stage": "inputs"},
            ),
            WorkflowStepDefinition(
                step_id="run_solver",
                title="Run Solver",
                description="Execute the relevant engineering solver.",
                owner="workflow_platform",
                default_status=WorkflowStepStatus.NOT_STARTED,
                dependencies=(
                    WorkflowDependency(
                        required_step_id="define_inputs",
                        reason="Solver execution requires complete engineering inputs.",
                    ),
                ),
                metadata={"stage": "solve"},
            ),
            WorkflowStepDefinition(
                step_id="validate_outputs",
                title="Validate Outputs",
                description="Validate solver outputs against subsystem rules.",
                owner="workflow_platform",
                default_status=WorkflowStepStatus.NOT_STARTED,
                dependencies=(
                    WorkflowDependency(
                        required_step_id="run_solver",
                        reason="Validation requires completed solver outputs.",
                    ),
                ),
                metadata={"stage": "validation"},
            ),
            WorkflowStepDefinition(
                step_id="produce_report",
                title="Produce Report",
                description="Generate a structured engineering report.",
                owner="workflow_platform",
                default_status=WorkflowStepStatus.NOT_STARTED,
                dependencies=(
                    WorkflowDependency(
                        required_step_id="validate_outputs",
                        reason="Reports require validation results.",
                    ),
                ),
                metadata={"stage": "report"},
            ),
            WorkflowStepDefinition(
                step_id="save_design",
                title="Save Design",
                description="Persist the design through canonical storage.",
                owner="workflow_platform",
                default_status=WorkflowStepStatus.NOT_STARTED,
                dependencies=(
                    WorkflowDependency(
                        required_step_id="produce_report",
                        reason="Design save requires report ownership.",
                    ),
                ),
                metadata={"stage": "storage"},
            ),
        ]
    )

    return registry
