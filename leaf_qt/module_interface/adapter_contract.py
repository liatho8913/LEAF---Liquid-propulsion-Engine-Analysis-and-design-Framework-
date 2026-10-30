"""
Programme 28D: Engineering Module Adapter Contract.

Defines the safe adapter boundary between real engineering modules and the
LEAF platform.

Design rules:
- Adapter contract only.
- No solver execution by default.
- No Qt ownership.
- No storage mutation.
- No runtime mutation.
- Real modules integrate through adapters instead of bespoke hardcoded wiring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Mapping, Protocol, Tuple, runtime_checkable

from .interface_model import EngineeringModuleInterface


class EngineeringModuleAdapterCapability(str, Enum):
    MODEL = "MODEL"
    SOLVER = "SOLVER"
    VALIDATION = "VALIDATION"
    REPORT = "REPORT"
    WORKFLOW = "WORKFLOW"
    RUNTIME = "RUNTIME"
    STORAGE = "STORAGE"
    NOTIFICATION = "NOTIFICATION"
    DEPENDENCY = "DEPENDENCY"


class EngineeringModuleAdapterStatus(str, Enum):
    READY = "READY"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    UNSAFE = "UNSAFE"


@dataclass(frozen=True)
class EngineeringModuleAdapterResult:
    schema: str
    adapter_id: str
    module_id: str
    status: EngineeringModuleAdapterStatus
    capability: EngineeringModuleAdapterCapability
    payload: Dict[str, Any] = field(default_factory=dict)
    mutation_performed: bool = False
    solver_executed: bool = False
    runtime_mutation_performed: bool = False
    storage_mutation_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "adapter_id": self.adapter_id,
            "module_id": self.module_id,
            "status": self.status.value,
            "capability": self.capability.value,
            "payload": dict(self.payload),
            "mutation_performed": self.mutation_performed,
            "solver_executed": self.solver_executed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "storage_mutation_performed": self.storage_mutation_performed,
        }


@runtime_checkable
class EngineeringModuleAdapterProtocol(Protocol):
    """
    Protocol expected from future engineering module adapters.
    """

    adapter_id: str
    interface: EngineeringModuleInterface

    def validate_adapter(self) -> Tuple[str, ...]:
        ...

    def describe_capabilities(self) -> Dict[str, Any]:
        ...

    def dry_run(self, capability: EngineeringModuleAdapterCapability) -> EngineeringModuleAdapterResult:
        ...


@dataclass
class EngineeringModuleAdapterContract:
    """
    Safe adapter contract wrapper.

    The contract validates that an adapter exposes the expected non-mutating
    platform boundary before later phases allow actual integration.
    """

    adapter_id: str
    interface: EngineeringModuleInterface
    capability_map: Dict[EngineeringModuleAdapterCapability, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate_adapter(self) -> Tuple[str, ...]:
        failures = []

        if not self.adapter_id.strip():
            failures.append("adapter_id is empty")

        interface_failures = self.interface.validate()
        failures.extend(interface_failures)

        required = set(EngineeringModuleAdapterCapability)
        present = set(self.capability_map.keys())
        missing = sorted(capability.value for capability in required - present)

        if missing:
            failures.append(f"adapter capability map missing: {missing}")

        for capability, target in self.capability_map.items():
            if not isinstance(capability, EngineeringModuleAdapterCapability):
                failures.append(f"invalid adapter capability key: {capability!r}")
            if not str(target).strip():
                failures.append(f"empty adapter target for capability: {capability}")

        return tuple(failures)

    def describe_capabilities(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_ENGINEERING_MODULE_ADAPTER_CAPABILITIES_PHASE_28D_V1",
            "adapter_id": self.adapter_id,
            "module_id": self.interface.module_id,
            "capability_count": len(self.capability_map),
            "capabilities": {
                capability.value: target
                for capability, target in sorted(
                    self.capability_map.items(),
                    key=lambda item: item[0].value,
                )
            },
            "validation_failures": list(self.validate_adapter()),
            "metadata_keys": sorted(self.metadata.keys()),
        }

    def dry_run(
        self,
        capability: EngineeringModuleAdapterCapability,
        payload: Mapping[str, Any] | None = None,
    ) -> EngineeringModuleAdapterResult:
        if capability not in self.capability_map:
            return EngineeringModuleAdapterResult(
                schema="LEAF_ENGINEERING_MODULE_ADAPTER_RESULT_PHASE_28D_V1",
                adapter_id=self.adapter_id,
                module_id=self.interface.module_id,
                status=EngineeringModuleAdapterStatus.BLOCKED,
                capability=capability,
                payload={
                    "reason": "Capability is not mapped by adapter contract.",
                    "requested_capability": capability.value,
                },
                mutation_performed=False,
                solver_executed=False,
                runtime_mutation_performed=False,
                storage_mutation_performed=False,
            )

        failures = self.validate_adapter()
        if failures:
            return EngineeringModuleAdapterResult(
                schema="LEAF_ENGINEERING_MODULE_ADAPTER_RESULT_PHASE_28D_V1",
                adapter_id=self.adapter_id,
                module_id=self.interface.module_id,
                status=EngineeringModuleAdapterStatus.BLOCKED,
                capability=capability,
                payload={"validation_failures": list(failures)},
                mutation_performed=False,
                solver_executed=False,
                runtime_mutation_performed=False,
                storage_mutation_performed=False,
            )

        return EngineeringModuleAdapterResult(
            schema="LEAF_ENGINEERING_MODULE_ADAPTER_RESULT_PHASE_28D_V1",
            adapter_id=self.adapter_id,
            module_id=self.interface.module_id,
            status=EngineeringModuleAdapterStatus.READY,
            capability=capability,
            payload={
                "target": self.capability_map[capability],
                "dry_run": True,
                "input_payload": dict(payload or {}),
            },
            mutation_performed=False,
            solver_executed=False,
            runtime_mutation_performed=False,
            storage_mutation_performed=False,
        )

    def report(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_ENGINEERING_MODULE_ADAPTER_CONTRACT_PHASE_28D_V1",
            "adapter_id": self.adapter_id,
            "module_id": self.interface.module_id,
            "interface": self.interface.report(),
            "capabilities": self.describe_capabilities(),
            "validation_failures": list(self.validate_adapter()),
            "mutation_performed": False,
            "solver_executed": False,
            "runtime_mutation_performed": False,
            "storage_mutation_performed": False,
        }


def default_adapter_capability_map(prefix: str) -> Dict[EngineeringModuleAdapterCapability, str]:
    """
    Build a standard adapter capability target map.

    This avoids every module inventing bespoke capability names.
    """

    clean_prefix = prefix.strip().replace(" ", "_")
    return {
        capability: f"{clean_prefix}.{capability.value.lower()}"
        for capability in EngineeringModuleAdapterCapability
    }


def build_engineering_module_adapter_contract(
    adapter_id: str,
    interface: EngineeringModuleInterface,
    capability_map: Mapping[EngineeringModuleAdapterCapability, str] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleAdapterContract:
    return EngineeringModuleAdapterContract(
        adapter_id=adapter_id,
        interface=interface,
        capability_map=dict(capability_map or default_adapter_capability_map(interface.module_id)),
        metadata=dict(metadata or {}),
    )
