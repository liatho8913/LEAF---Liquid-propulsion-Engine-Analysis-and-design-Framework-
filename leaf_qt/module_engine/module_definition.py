from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


REQUIRED_CONTRACTS = (
    "interface",
    "solver",
    "validation",
    "workflow",
    "runtime",
    "storage",
    "reports",
    "notifications",
)


RUNTIME_BINDING_STAGE_GATED = "stage_gated"
RUNTIME_BINDING_ENTRYPOINT = "entrypoint"
SUPPORTED_RUNTIME_BINDINGS = (
    RUNTIME_BINDING_STAGE_GATED,
    RUNTIME_BINDING_ENTRYPOINT,
)


@dataclass(frozen=True)
class ModuleDefinition:
    module_id: str
    name: str
    domain: str
    version: str
    description: str
    engineering_owner: str
    entrypoint: str
    runtime_binding: str
    contracts: dict[str, str]
    dependencies: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    enabled: bool = True
    requires_modules: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModuleDefinition":
        return cls(
            module_id=str(data["module_id"]),
            name=str(data["name"]),
            domain=str(data["domain"]),
            version=str(data["version"]),
            description=str(data["description"]),
            engineering_owner=str(data["engineering_owner"]),
            entrypoint=str(data.get("entrypoint", "")),
            runtime_binding=str(
                data.get("runtime_binding", RUNTIME_BINDING_ENTRYPOINT)
            ).strip() or RUNTIME_BINDING_ENTRYPOINT,
            contracts=dict(data["contracts"]),
            dependencies=list(data.get("dependencies", [])),
            outputs=list(data.get("outputs", [])),
            tags=list(data.get("tags", [])),
            enabled=bool(data.get("enabled", True)),
            requires_modules=list(data.get("requires_modules", [])),
        )

    def validate(self) -> dict[str, Any]:
        missing_contracts = [
            contract for contract in REQUIRED_CONTRACTS
            if contract not in self.contracts
        ]

        empty_contracts = [
            contract for contract, owner in self.contracts.items()
            if not str(owner).strip()
        ]

        self_dependency = self.module_id in self.requires_modules
        runtime_binding_supported = self.runtime_binding in SUPPORTED_RUNTIME_BINDINGS
        entrypoint_present = bool(str(self.entrypoint).strip())
        runtime_binding_valid = (
            runtime_binding_supported
            and (
                self.runtime_binding != RUNTIME_BINDING_ENTRYPOINT
                or entrypoint_present
            )
            and not (
                self.runtime_binding == RUNTIME_BINDING_STAGE_GATED
                and entrypoint_present
            )
        )
        passed = (
            not missing_contracts
            and not empty_contracts
            and not self_dependency
            and runtime_binding_valid
        )

        return {
            "module_id": self.module_id,
            "name": self.name,
            "status": "PASS" if passed else "FAIL",
            "missing_contracts": missing_contracts,
            "empty_contracts": empty_contracts,
            "self_dependency": self_dependency,
            "runtime_binding": self.runtime_binding,
            "runtime_binding_supported": runtime_binding_supported,
            "runtime_binding_valid": runtime_binding_valid,
            "required_contracts": list(REQUIRED_CONTRACTS),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "name": self.name,
            "domain": self.domain,
            "version": self.version,
            "description": self.description,
            "engineering_owner": self.engineering_owner,
            "entrypoint": self.entrypoint,
            "runtime_binding": self.runtime_binding,
            "contracts": self.contracts,
            "dependencies": self.dependencies,
            "outputs": self.outputs,
            "tags": self.tags,
            "enabled": self.enabled,
            "requires_modules": self.requires_modules,
        }
