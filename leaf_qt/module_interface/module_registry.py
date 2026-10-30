"""
Programme 28B: Engineering Module Registry.

Reusable registry for LEAF engineering module interfaces.

Design rules:
- Register module interfaces only.
- No Qt ownership.
- No solver execution.
- No storage mutation.
- No workflow/runtime mutation.
- Prevent duplicate bespoke module integration patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple

from .interface_model import (
    EngineeringModuleInterface,
    EngineeringModuleInterfaceStatus,
    EngineeringModuleSurface,
)


@dataclass
class EngineeringModuleRegistry:
    registry_id: str = "leaf_engineering_module_registry"
    modules: Dict[str, EngineeringModuleInterface] = field(default_factory=dict)

    def register(
        self,
        interface: EngineeringModuleInterface,
        replace: bool = False,
    ) -> None:
        failures = interface.validate()
        if failures:
            raise ValueError("; ".join(failures))

        if interface.module_id in self.modules and not replace:
            raise ValueError(f"engineering module already registered: {interface.module_id}")

        self.modules[interface.module_id] = interface

    def register_many(
        self,
        interfaces: Iterable[EngineeringModuleInterface],
        replace: bool = False,
    ) -> None:
        for interface in interfaces:
            self.register(interface, replace=replace)

    def has(self, module_id: str) -> bool:
        return module_id in self.modules

    def get(self, module_id: str) -> EngineeringModuleInterface:
        try:
            return self.modules[module_id]
        except KeyError as exc:
            raise KeyError(f"unknown engineering module: {module_id}") from exc

    def all_modules(self) -> Tuple[EngineeringModuleInterface, ...]:
        return tuple(self.modules.values())

    def modules_by_status(
        self,
        status: EngineeringModuleInterfaceStatus,
    ) -> Tuple[EngineeringModuleInterface, ...]:
        return tuple(module for module in self.all_modules() if module.status == status)

    def modules_providing(self, capability: str) -> Tuple[str, ...]:
        providers: List[str] = []

        for module in self.all_modules():
            dependency_report = module.dependency_report()
            if capability in dependency_report["provides"]:
                providers.append(module.module_id)

        return tuple(sorted(providers))

    def modules_requiring(self, capability: str) -> Tuple[str, ...]:
        consumers: List[str] = []

        for module in self.all_modules():
            dependency_report = module.dependency_report()
            if capability in dependency_report["requires"]:
                consumers.append(module.module_id)

        return tuple(sorted(consumers))

    def surface_coverage(self) -> Dict[str, int]:
        coverage = {surface.value: 0 for surface in EngineeringModuleSurface}

        for module in self.all_modules():
            for surface in module.surfaces():
                coverage[surface] += 1

        return coverage

    def validate(self) -> List[str]:
        failures: List[str] = []

        if not self.registry_id.strip():
            failures.append("registry_id is empty")

        for module in self.all_modules():
            failures.extend(module.validate())

        return failures

    def report(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_ENGINEERING_MODULE_REGISTRY_PHASE_28B_V1",
            "registry_id": self.registry_id,
            "module_count": len(self.modules),
            "ready_modules": len(self.modules_by_status(EngineeringModuleInterfaceStatus.READY)),
            "draft_modules": len(self.modules_by_status(EngineeringModuleInterfaceStatus.DRAFT)),
            "partial_modules": len(self.modules_by_status(EngineeringModuleInterfaceStatus.PARTIAL)),
            "blocked_modules": len(self.modules_by_status(EngineeringModuleInterfaceStatus.BLOCKED)),
            "deprecated_modules": len(self.modules_by_status(EngineeringModuleInterfaceStatus.DEPRECATED)),
            "surface_coverage": self.surface_coverage(),
            "validation_failures": self.validate(),
            "modules": [
                {
                    "module_id": module.module_id,
                    "title": module.title,
                    "version": module.version,
                    "status": module.status.value,
                    "surface_count": len(module.surfaces()),
                    "surfaces": list(module.surfaces()),
                    "missing_required_surfaces": list(module.missing_required_surfaces()),
                    "dependency_report": module.dependency_report(),
                }
                for module in self.all_modules()
            ],
        }


def build_engineering_module_registry(
    interfaces: Iterable[EngineeringModuleInterface] | None = None,
) -> EngineeringModuleRegistry:
    registry = EngineeringModuleRegistry()
    if interfaces:
        registry.register_many(interfaces)
    return registry
