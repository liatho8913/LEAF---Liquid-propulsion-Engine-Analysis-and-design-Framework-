from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from leaf_qt.module_engine.module_contract import ModuleContract
from leaf_qt.module_engine.module_definition import ModuleDefinition
from leaf_qt.module_engine.module_discovery_engine import ModuleDiscoveryEngine


@dataclass(frozen=True)
class ModuleContractBuildResult:
    status: str
    contract_count: int
    contracts: dict[str, dict[str, Any]]
    invalid_contracts: dict[str, Any]
    builder_owner: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "contract_count": self.contract_count,
            "contracts": self.contracts,
            "invalid_contracts": self.invalid_contracts,
            "builder_owner": self.builder_owner,
        }


class ModuleContractBuilder:
    """
    Single source of truth for constructing module contracts.

    This builder converts module declarations into standard contracts.

    It does not create engineering logic.
    It does not run solvers.
    It does not manually bind modules.

    Its responsibility is architectural contract construction only.
    """

    BUILDER_OWNER = "leaf_qt.module_engine.module_contract_builder.ModuleContractBuilder"

    def __init__(self, definition_dir: Path):
        self.definition_dir = Path(definition_dir)
        self.discovery_engine = ModuleDiscoveryEngine(self.definition_dir)

    def build_contract(self, definition: ModuleDefinition) -> ModuleContract:
        return ModuleContract.from_definition(definition)

    def build_all(self) -> dict[str, ModuleContract]:
        definitions = self.discovery_engine.discover_definitions()
        contracts: dict[str, ModuleContract] = {}

        for definition in definitions:
            if definition.module_id in contracts:
                raise ValueError(f"Duplicate module contract: {definition.module_id}")
            contracts[definition.module_id] = self.build_contract(definition)

        return contracts

    def audit(self) -> ModuleContractBuildResult:
        contracts = self.build_all()

        invalid_contracts: dict[str, Any] = {}
        contract_payloads: dict[str, dict[str, Any]] = {}

        for module_id, contract in sorted(contracts.items()):
            validation = contract.validate()
            contract_payloads[module_id] = contract.to_dict()

            if validation["status"] != "PASS":
                invalid_contracts[module_id] = validation

        passed = bool(contracts) and not invalid_contracts

        return ModuleContractBuildResult(
            status="PASS" if passed else "FAIL",
            contract_count=len(contracts),
            contracts=contract_payloads,
            invalid_contracts=invalid_contracts,
            builder_owner=self.BUILDER_OWNER,
        )
