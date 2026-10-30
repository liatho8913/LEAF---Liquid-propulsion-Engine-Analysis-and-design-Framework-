"""
Programme 28A: Engineering Module Interface Model.

Defines the reusable interface contract for LEAF engineering modules.

Design rules:
- Platform contract only.
- No Qt ownership.
- No solver execution.
- No storage mutation.
- No module-specific hardcoding.
- Future engineering modules should expose this shape rather than bespoke adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Tuple


class EngineeringModuleSurface(str, Enum):
    MODEL = "MODEL"
    SOLVER = "SOLVER"
    VALIDATION = "VALIDATION"
    REPORT = "REPORT"
    WORKFLOW = "WORKFLOW"
    RUNTIME = "RUNTIME"
    STORAGE = "STORAGE"
    NOTIFICATION = "NOTIFICATION"
    DEPENDENCY = "DEPENDENCY"


class EngineeringModuleInterfaceStatus(str, Enum):
    DRAFT = "DRAFT"
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    DEPRECATED = "DEPRECATED"


@dataclass(frozen=True)
class EngineeringModuleDependency:
    dependency_id: str
    provides: Tuple[str, ...] = field(default_factory=tuple)
    requires: Tuple[str, ...] = field(default_factory=tuple)
    optional: Tuple[str, ...] = field(default_factory=tuple)
    reason: str = ""

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.dependency_id.strip():
            failures.append("dependency_id is empty")

        if not self.reason.strip():
            failures.append(f"dependency reason is empty for {self.dependency_id!r}")

        overlap = set(self.requires) & set(self.optional)
        if overlap:
            failures.append(
                f"dependency {self.dependency_id!r} has overlapping requires/optional: {sorted(overlap)}"
            )

        return failures

    def as_dict(self) -> Dict[str, Any]:
        return {
            "dependency_id": self.dependency_id,
            "provides": list(self.provides),
            "requires": list(self.requires),
            "optional": list(self.optional),
            "reason": self.reason,
        }


@dataclass(frozen=True)
class EngineeringModuleCapability:
    surface: EngineeringModuleSurface
    capability_id: str
    title: str
    description: str
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not isinstance(self.surface, EngineeringModuleSurface):
            failures.append(f"surface invalid for capability {self.capability_id!r}: {self.surface!r}")

        if not self.capability_id.strip():
            failures.append("capability_id is empty")

        if not self.title.strip():
            failures.append(f"capability title is empty for {self.capability_id!r}")

        if not self.description.strip():
            failures.append(f"capability description is empty for {self.capability_id!r}")

        return failures

    def as_dict(self) -> Dict[str, Any]:
        return {
            "surface": self.surface.value,
            "capability_id": self.capability_id,
            "title": self.title,
            "description": self.description,
            "required": self.required,
            "metadata_keys": sorted(self.metadata.keys()),
        }


@dataclass(frozen=True)
class EngineeringModuleInterface:
    module_id: str
    title: str
    version: str = "1.0.0"
    status: EngineeringModuleInterfaceStatus = EngineeringModuleInterfaceStatus.DRAFT
    capabilities: Tuple[EngineeringModuleCapability, ...] = field(default_factory=tuple)
    dependencies: Tuple[EngineeringModuleDependency, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.module_id.strip():
            failures.append("module_id is empty")

        if not self.title.strip():
            failures.append(f"title is empty for module {self.module_id!r}")

        if not self.version.strip():
            failures.append(f"version is empty for module {self.module_id!r}")

        if not isinstance(self.status, EngineeringModuleInterfaceStatus):
            failures.append(f"status invalid for module {self.module_id!r}: {self.status!r}")

        seen_capabilities = set()
        for capability in self.capabilities:
            failures.extend(capability.validate())
            if capability.capability_id in seen_capabilities:
                failures.append(f"duplicate capability_id: {capability.capability_id}")
            seen_capabilities.add(capability.capability_id)

        seen_dependencies = set()
        for dependency in self.dependencies:
            failures.extend(dependency.validate())
            if dependency.dependency_id in seen_dependencies:
                failures.append(f"duplicate dependency_id: {dependency.dependency_id}")
            seen_dependencies.add(dependency.dependency_id)

        missing_surfaces = self.missing_required_surfaces()
        if missing_surfaces:
            failures.append(f"missing required module surfaces: {list(missing_surfaces)}")

        return failures

    def surfaces(self) -> Tuple[str, ...]:
        return tuple(sorted({capability.surface.value for capability in self.capabilities}))

    def missing_required_surfaces(self) -> Tuple[str, ...]:
        present = {capability.surface for capability in self.capabilities if capability.required}
        required = set(EngineeringModuleSurface)
        missing = sorted(surface.value for surface in required if surface not in present)
        return tuple(missing)

    def capability_map(self) -> Dict[str, EngineeringModuleCapability]:
        return {capability.capability_id: capability for capability in self.capabilities}

    def dependency_report(self) -> Dict[str, Any]:
        provides = []
        requires = []
        optional = []

        for dependency in self.dependencies:
            provides.extend(dependency.provides)
            requires.extend(dependency.requires)
            optional.extend(dependency.optional)

        return {
            "provides": sorted(set(provides)),
            "requires": sorted(set(requires)),
            "optional": sorted(set(optional)),
            "dependency_count": len(self.dependencies),
        }

    def report(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_ENGINEERING_MODULE_INTERFACE_MODEL_PHASE_28A_V1",
            "module_id": self.module_id,
            "title": self.title,
            "version": self.version,
            "status": self.status.value,
            "surface_count": len(self.surfaces()),
            "surfaces": list(self.surfaces()),
            "missing_required_surfaces": list(self.missing_required_surfaces()),
            "capability_count": len(self.capabilities),
            "dependency_report": self.dependency_report(),
            "validation_failures": self.validate(),
            "capabilities": [capability.as_dict() for capability in self.capabilities],
            "dependencies": [dependency.as_dict() for dependency in self.dependencies],
            "metadata_keys": sorted(self.metadata.keys()),
        }


def _default_capabilities() -> Tuple[EngineeringModuleCapability, ...]:
    return (
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.MODEL,
            capability_id="module_model_contract",
            title="Module Model Contract",
            description="Defines input/output model structures exposed by the engineering module.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.SOLVER,
            capability_id="module_solver_contract",
            title="Module Solver Contract",
            description="Defines solver entry points without executing them inside the interface model.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.VALIDATION,
            capability_id="module_validation_contract",
            title="Module Validation Contract",
            description="Defines validation ownership, failure structure, and gating behaviour.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.REPORT,
            capability_id="module_report_contract",
            title="Module Report Contract",
            description="Defines report ownership and report payload expectations.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.WORKFLOW,
            capability_id="module_workflow_contract",
            title="Module Workflow Contract",
            description="Defines workflow integration with the Programme 26 workflow platform.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.RUNTIME,
            capability_id="module_runtime_contract",
            title="Module Runtime Contract",
            description="Defines safe runtime integration boundaries.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.STORAGE,
            capability_id="module_storage_contract",
            title="Module Storage Contract",
            description="Defines canonical project/design/report/export storage integration.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.NOTIFICATION,
            capability_id="module_notification_contract",
            title="Module Notification Contract",
            description="Defines notification/event behaviour without owning notification infrastructure.",
        ),
        EngineeringModuleCapability(
            surface=EngineeringModuleSurface.DEPENDENCY,
            capability_id="module_dependency_contract",
            title="Module Dependency Contract",
            description="Defines provides/requires/optional dependency declarations.",
        ),
    )


def build_engineering_module_interface(
    module_id: str,
    title: str,
    version: str = "1.0.0",
    status: EngineeringModuleInterfaceStatus = EngineeringModuleInterfaceStatus.DRAFT,
    capabilities: Iterable[EngineeringModuleCapability] | None = None,
    dependencies: Iterable[EngineeringModuleDependency] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleInterface:
    return EngineeringModuleInterface(
        module_id=module_id,
        title=title,
        version=version,
        status=status,
        capabilities=tuple(capabilities) if capabilities is not None else _default_capabilities(),
        dependencies=tuple(dependencies or ()),
        metadata=dict(metadata or {}),
    )
