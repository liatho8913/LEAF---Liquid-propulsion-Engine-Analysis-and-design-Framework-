"""
Programme 28C: Engineering Module Dependency Graph.

Analyses provides/requires/optional relationships between registered engineering
modules.

Design rules:
- Analyse dependencies only.
- No Qt ownership.
- No solver execution.
- No runtime/storage mutation.
- No automatic module activation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple



@dataclass(frozen=True)
class EngineeringModuleDependencyGraphReport:
    schema: str
    registry_id: str
    module_count: int
    provided_capability_count: int
    required_capability_count: int
    optional_capability_count: int
    missing_required_capabilities: Tuple[str, ...]
    provider_map: Dict[str, Tuple[str, ...]]
    consumer_map: Dict[str, Tuple[str, ...]]
    optional_consumer_map: Dict[str, Tuple[str, ...]]
    validation_failures: Tuple[str, ...]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "registry_id": self.registry_id,
            "module_count": self.module_count,
            "provided_capability_count": self.provided_capability_count,
            "required_capability_count": self.required_capability_count,
            "optional_capability_count": self.optional_capability_count,
            "missing_required_capabilities": list(self.missing_required_capabilities),
            "provider_map": {key: list(value) for key, value in self.provider_map.items()},
            "consumer_map": {key: list(value) for key, value in self.consumer_map.items()},
            "optional_consumer_map": {
                key: list(value) for key, value in self.optional_consumer_map.items()
            },
            "validation_failures": list(self.validation_failures),
        }


class EngineeringModuleDependencyGraph:
    """
    Shared module dependency graph.

    This graph treats module dependencies as capability relationships:
        module provides capability
        module requires capability
        module optionally consumes capability
    """

    def __init__(self, registry: EngineeringModuleRegistry) -> None:
        self.registry = registry

    def provider_map(self) -> Dict[str, Tuple[str, ...]]:
        providers: Dict[str, Set[str]] = {}

        for module in self.registry.all_modules():
            dependency_report = module.dependency_report()
            for capability in dependency_report["provides"]:
                providers.setdefault(capability, set()).add(module.module_id)

        return {
            capability: tuple(sorted(module_ids))
            for capability, module_ids in sorted(providers.items())
        }

    def consumer_map(self) -> Dict[str, Tuple[str, ...]]:
        consumers: Dict[str, Set[str]] = {}

        for module in self.registry.all_modules():
            dependency_report = module.dependency_report()
            for capability in dependency_report["requires"]:
                consumers.setdefault(capability, set()).add(module.module_id)

        return {
            capability: tuple(sorted(module_ids))
            for capability, module_ids in sorted(consumers.items())
        }

    def optional_consumer_map(self) -> Dict[str, Tuple[str, ...]]:
        consumers: Dict[str, Set[str]] = {}

        for module in self.registry.all_modules():
            dependency_report = module.dependency_report()
            for capability in dependency_report["optional"]:
                consumers.setdefault(capability, set()).add(module.module_id)

        return {
            capability: tuple(sorted(module_ids))
            for capability, module_ids in sorted(consumers.items())
        }

    def provided_capabilities(self) -> Tuple[str, ...]:
        return tuple(sorted(self.provider_map().keys()))

    def required_capabilities(self) -> Tuple[str, ...]:
        return tuple(sorted(self.consumer_map().keys()))

    def optional_capabilities(self) -> Tuple[str, ...]:
        return tuple(sorted(self.optional_consumer_map().keys()))

    def providers_for(self, capability: str) -> Tuple[str, ...]:
        return self.provider_map().get(capability, tuple())

    def consumers_for(self, capability: str) -> Tuple[str, ...]:
        return self.consumer_map().get(capability, tuple())

    def optional_consumers_for(self, capability: str) -> Tuple[str, ...]:
        return self.optional_consumer_map().get(capability, tuple())

    def missing_required_capabilities(self) -> Tuple[str, ...]:
        provided = set(self.provided_capabilities())
        missing = [
            capability
            for capability in self.required_capabilities()
            if capability not in provided
        ]
        return tuple(sorted(missing))

    def module_missing_requirements(self, module_id: str) -> Tuple[str, ...]:
        module = self.registry.get(module_id)
        provided = set(self.provided_capabilities())
        required = module.dependency_report()["requires"]
        return tuple(sorted(capability for capability in required if capability not in provided))

    def module_integration_ready(self, module_id: str) -> bool:
        return not self.module_missing_requirements(module_id)

    def module_readiness_map(self) -> Dict[str, bool]:
        return {
            module.module_id: self.module_integration_ready(module.module_id)
            for module in self.registry.all_modules()
        }

    def validate(self) -> Tuple[str, ...]:
        failures: List[str] = []
        failures.extend(self.registry.validate())

        for capability in self.missing_required_capabilities():
            failures.append(f"missing required capability provider: {capability}")

        return tuple(failures)

    def report(self) -> EngineeringModuleDependencyGraphReport:
        providers = self.provider_map()
        consumers = self.consumer_map()
        optional_consumers = self.optional_consumer_map()

        return EngineeringModuleDependencyGraphReport(
            schema="LEAF_ENGINEERING_MODULE_DEPENDENCY_GRAPH_PHASE_28C_V1",
            registry_id=self.registry.registry_id,
            module_count=len(self.registry.modules),
            provided_capability_count=len(providers),
            required_capability_count=len(consumers),
            optional_capability_count=len(optional_consumers),
            missing_required_capabilities=self.missing_required_capabilities(),
            provider_map=providers,
            consumer_map=consumers,
            optional_consumer_map=optional_consumers,
            validation_failures=self.validate(),
        )


def build_engineering_module_dependency_graph(
    registry: EngineeringModuleRegistry,
) -> EngineeringModuleDependencyGraph:
    return EngineeringModuleDependencyGraph(registry=registry)
