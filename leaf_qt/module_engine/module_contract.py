from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from leaf_qt.module_engine.module_definition import REQUIRED_CONTRACTS, ModuleDefinition


@dataclass(frozen=True)
class ModuleContract:
    module_id: str
    module_name: str
    domain: str
    version: str
    entrypoint: str
    runtime_binding: str
    engineering_owner: str
    contract_owners: dict[str, str]
    dependencies: list[str]
    outputs: list[str]
    tags: list[str]
    enabled: bool = True
    requires_modules: list[str] | None = None

    def validate(self) -> dict[str, Any]:
        missing_contracts = [
            contract for contract in REQUIRED_CONTRACTS
            if contract not in self.contract_owners
        ]

        empty_contracts = [
            contract for contract, owner in self.contract_owners.items()
            if not str(owner).strip()
        ]

        passed = not missing_contracts and not empty_contracts

        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "status": "PASS" if passed else "FAIL",
            "missing_contracts": missing_contracts,
            "empty_contracts": empty_contracts,
            "contract_count": len(self.contract_owners),
            "required_contract_count": len(REQUIRED_CONTRACTS),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "domain": self.domain,
            "version": self.version,
            "entrypoint": self.entrypoint,
            "runtime_binding": self.runtime_binding,
            "engineering_owner": self.engineering_owner,
            "contract_owners": self.contract_owners,
            "dependencies": self.dependencies,
            "outputs": self.outputs,
            "tags": self.tags,
            "enabled": self.enabled,
            "requires_modules": list(self.requires_modules or []),
        }

    @classmethod
    def from_definition(cls, definition: ModuleDefinition) -> "ModuleContract":
        return cls(
            module_id=definition.module_id,
            module_name=definition.name,
            domain=definition.domain,
            version=definition.version,
            entrypoint=definition.entrypoint,
            runtime_binding=definition.runtime_binding,
            engineering_owner=definition.engineering_owner,
            contract_owners=dict(definition.contracts),
            dependencies=list(definition.dependencies),
            outputs=list(definition.outputs),
            tags=list(definition.tags),
            enabled=definition.enabled,
            requires_modules=list(definition.requires_modules),
        )
