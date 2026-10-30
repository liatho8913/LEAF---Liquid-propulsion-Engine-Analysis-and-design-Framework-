"""
Reusable Engineering Module Contract Compatibility Verifier.

Purpose:
Validate that contract result payloads expose expected fields before completion
gates rely on them.

This prevents gates from assuming payload shape and failing with KeyError.

Reusable by:
- Regen module
- Combustion chamber module
- Nozzle module
- Injector module
- Turbopump module
- Future engineering plugins
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class ContractFieldExpectation:
    contract_name: str
    required_fields: Tuple[str, ...]
    optional_fields: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ContractCompatibilityResult:
    contract_name: str
    available_fields: Tuple[str, ...]
    required_fields: Tuple[str, ...]
    optional_fields: Tuple[str, ...]
    missing_required_fields: Tuple[str, ...]
    missing_optional_fields: Tuple[str, ...]
    compatible: bool

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contract_name": self.contract_name,
            "available_fields": list(self.available_fields),
            "required_fields": list(self.required_fields),
            "optional_fields": list(self.optional_fields),
            "missing_required_fields": list(self.missing_required_fields),
            "missing_optional_fields": list(self.missing_optional_fields),
            "compatible": self.compatible,
        }


@dataclass(frozen=True)
class ModuleContractCompatibilityReport:
    module_id: str
    results: Tuple[ContractCompatibilityResult, ...]
    compatible: bool
    mutation_performed: bool = False
    solver_executed: bool = False
    runtime_mutation_performed: bool = False
    storage_mutation_performed: bool = False

    def failures(self) -> Tuple[str, ...]:
        output = []
        for result in self.results:
            if not result.compatible:
                output.append(
                    f"{result.contract_name} missing required fields: "
                    f"{', '.join(result.missing_required_fields)}"
                )
        return tuple(output)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": "LEAF_MODULE_CONTRACT_COMPATIBILITY_REPORT_V1",
            "module_id": self.module_id,
            "compatible": self.compatible,
            "results": [result.as_dict() for result in self.results],
            "failures": list(self.failures()),
            "mutation_performed": self.mutation_performed,
            "solver_executed": self.solver_executed,
            "runtime_mutation_performed": self.runtime_mutation_performed,
            "storage_mutation_performed": self.storage_mutation_performed,
        }


def evaluate_contract_payload(
    contract_name: str,
    payload: Mapping[str, Any],
    required_fields: Sequence[str],
    optional_fields: Sequence[str] = (),
) -> ContractCompatibilityResult:
    available = tuple(sorted(str(key) for key in payload.keys()))
    available_set = set(available)

    required = tuple(required_fields)
    optional = tuple(optional_fields)

    missing_required = tuple(field for field in required if field not in available_set)
    missing_optional = tuple(field for field in optional if field not in available_set)

    return ContractCompatibilityResult(
        contract_name=contract_name,
        available_fields=available,
        required_fields=required,
        optional_fields=optional,
        missing_required_fields=missing_required,
        missing_optional_fields=missing_optional,
        compatible=not missing_required,
    )


def evaluate_module_contract_compatibility(
    module_id: str,
    payloads: Mapping[str, Mapping[str, Any]],
    expectations: Sequence[ContractFieldExpectation],
) -> ModuleContractCompatibilityReport:
    results = []

    for expectation in expectations:
        payload = payloads.get(expectation.contract_name, {})
        results.append(
            evaluate_contract_payload(
                contract_name=expectation.contract_name,
                payload=payload,
                required_fields=expectation.required_fields,
                optional_fields=expectation.optional_fields,
            )
        )

    compatible = all(result.compatible for result in results)

    return ModuleContractCompatibilityReport(
        module_id=module_id,
        results=tuple(results),
        compatible=compatible,
    )
