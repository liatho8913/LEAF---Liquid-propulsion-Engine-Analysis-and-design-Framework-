from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class ContractResult:
    status: str
    subsystem: str
    message: str = ""
    evidence: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status.upper() in {"PASS", "PASSED", "OK", "SUCCESS"}


class LeafContract(ABC):
    contract_name: str = "LEAF_CONTRACT"
    contract_version: str = "1.0"

    @abstractmethod
    def contract_metadata(self) -> Mapping[str, Any]:
        raise NotImplementedError


class SolverContract(LeafContract):
    contract_name = "SOLVER_CONTRACT"

    @abstractmethod
    def solve(self, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError


class ValidationContract(LeafContract):
    contract_name = "VALIDATION_CONTRACT"

    @abstractmethod
    def validate(self, payload: Mapping[str, Any]) -> ContractResult:
        raise NotImplementedError


class ReportingContract(LeafContract):
    contract_name = "REPORTING_CONTRACT"

    @abstractmethod
    def build_report(self, payload: Mapping[str, Any]) -> str:
        raise NotImplementedError


class RegistryContract(LeafContract):
    contract_name = "REGISTRY_CONTRACT"

    @abstractmethod
    def list_registered_keys(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_registered_item(self, key: str) -> Any:
        raise NotImplementedError


class OptimisationContract(LeafContract):
    contract_name = "OPTIMISATION_CONTRACT"

    @abstractmethod
    def optimise(self, inputs: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError


class UIPanelContract(LeafContract):
    contract_name = "UI_PANEL_CONTRACT"

    @abstractmethod
    def panel_title(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def refresh_from_payload(self, payload: Mapping[str, Any]) -> None:
        raise NotImplementedError


class SupportsContractMetadata(Protocol):
    def contract_metadata(self) -> Mapping[str, Any]:
        ...


def describe_contract(obj: SupportsContractMetadata) -> Mapping[str, Any]:
    metadata = dict(obj.contract_metadata())
    metadata.setdefault("contract_name", getattr(obj, "contract_name", "UNKNOWN_CONTRACT"))
    metadata.setdefault("contract_version", getattr(obj, "contract_version", "UNKNOWN_VERSION"))
    return metadata


def validate_contract_metadata(obj: SupportsContractMetadata) -> ContractResult:
    metadata = describe_contract(obj)

    required = ["contract_name", "contract_version", "subsystem"]
    missing = [key for key in required if not metadata.get(key)]

    if missing:
        return ContractResult(
            status="FAIL",
            subsystem=str(metadata.get("subsystem", "UNKNOWN")),
            message="Missing required contract metadata.",
            evidence={"missing": missing, "metadata": metadata},
        )

    return ContractResult(
        status="PASS",
        subsystem=str(metadata["subsystem"]),
        message="Contract metadata is valid.",
        evidence={"metadata": metadata},
    )
