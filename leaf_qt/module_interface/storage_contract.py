"""
Programme 28I: Engineering Module Storage Contract.

Defines safe storage-facing requests for engineering modules.

Design rules:
- Modules do not own storage.
- Modules do not write files directly.
- Storage requests must target canonical LEAF storage domains.
- No mutation is performed by this contract.
- Future storage bridges may consume these structured requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Any, Dict, Mapping, Tuple

from .interface_model import EngineeringModuleInterface


class EngineeringModuleStorageDomain(str, Enum):
    PROJECT = "PROJECT"
    DESIGN = "DESIGN"
    REPORT = "REPORT"
    EXPORT = "EXPORT"
    VALIDATION = "VALIDATION"


class EngineeringModuleStorageAction(str, Enum):
    PREPARE_SAVE_DESIGN = "PREPARE_SAVE_DESIGN"
    PREPARE_LOAD_DESIGN = "PREPARE_LOAD_DESIGN"
    ATTACH_REPORT = "ATTACH_REPORT"
    ATTACH_EXPORT = "ATTACH_EXPORT"
    REQUEST_STORAGE_SNAPSHOT = "REQUEST_STORAGE_SNAPSHOT"
    NO_OP = "NO_OP"


class EngineeringModuleStorageRequestStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"
    INVALID = "INVALID"


CANONICAL_STORAGE_FOLDERS = {
    EngineeringModuleStorageDomain.PROJECT: "LEAF_Projects",
    EngineeringModuleStorageDomain.DESIGN: "LEAF_Designs",
    EngineeringModuleStorageDomain.REPORT: "LEAF_Reports",
    EngineeringModuleStorageDomain.EXPORT: "LEAF_Exports",
    EngineeringModuleStorageDomain.VALIDATION: "LEAF_Validation",
}


@dataclass(frozen=True)
class EngineeringModuleStorageRequest:
    module_id: str
    action: EngineeringModuleStorageAction
    domain: EngineeringModuleStorageDomain
    storage_key: str
    payload: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate(self) -> Tuple[str, ...]:
        failures = []

        if not self.module_id.strip():
            failures.append("module_id is empty")

        if not isinstance(self.action, EngineeringModuleStorageAction):
            failures.append(f"invalid storage action: {self.action!r}")

        if not isinstance(self.domain, EngineeringModuleStorageDomain):
            failures.append(f"invalid storage domain: {self.domain!r}")

        if not self.storage_key.strip():
            failures.append("storage_key is empty")

        if "/" in self.storage_key or "\\" in self.storage_key or ".." in self.storage_key:
            failures.append("storage_key must be a safe filename-like key, not a path")

        return tuple(failures)

    def canonical_folder(self) -> str:
        return CANONICAL_STORAGE_FOLDERS[self.domain]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "module_id": self.module_id,
            "action": self.action.value,
            "domain": self.domain.value,
            "canonical_folder": self.canonical_folder(),
            "storage_key": self.storage_key,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class EngineeringModuleStorageResult:
    schema: str
    module_id: str
    action: str
    domain: str
    canonical_folder: str
    status: EngineeringModuleStorageRequestStatus
    accepted: bool
    reason: str
    storage_event: Dict[str, Any] | None = None
    validation_failures: Tuple[str, ...] = tuple()
    mutation_performed: bool = False
    file_written: bool = False
    file_deleted: bool = False
    archive_performed: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "module_id": self.module_id,
            "action": self.action,
            "domain": self.domain,
            "canonical_folder": self.canonical_folder,
            "status": self.status.value,
            "accepted": self.accepted,
            "reason": self.reason,
            "storage_event": dict(self.storage_event or {}),
            "validation_failures": list(self.validation_failures),
            "mutation_performed": self.mutation_performed,
            "file_written": self.file_written,
            "file_deleted": self.file_deleted,
            "archive_performed": self.archive_performed,
        }


@dataclass(frozen=True)
class EngineeringModuleStorageContract:
    interface: EngineeringModuleInterface
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)

    def validate_contract(self) -> Tuple[str, ...]:
        return tuple(self.interface.validate())

    def build_request(
        self,
        action: EngineeringModuleStorageAction,
        domain: EngineeringModuleStorageDomain,
        storage_key: str,
        payload: Mapping[str, Any] | None = None,
    ) -> EngineeringModuleStorageRequest:
        return EngineeringModuleStorageRequest(
            module_id=self.interface.module_id,
            action=action,
            domain=domain,
            storage_key=storage_key,
            payload=dict(payload or {}),
        )

    def submit(self, request: EngineeringModuleStorageRequest) -> EngineeringModuleStorageResult:
        failures = list(self.validate_contract())
        failures.extend(request.validate())

        if request.module_id != self.interface.module_id:
            failures.append(
                f"request module_id {request.module_id!r} does not match interface module_id {self.interface.module_id!r}"
            )

        if failures:
            return EngineeringModuleStorageResult(
                schema="LEAF_ENGINEERING_MODULE_STORAGE_RESULT_PHASE_28I_V1",
                module_id=request.module_id,
                action=request.action.value if isinstance(request.action, EngineeringModuleStorageAction) else str(request.action),
                domain=request.domain.value if isinstance(request.domain, EngineeringModuleStorageDomain) else str(request.domain),
                canonical_folder=request.canonical_folder() if isinstance(request.domain, EngineeringModuleStorageDomain) else "UNKNOWN",
                status=EngineeringModuleStorageRequestStatus.INVALID,
                accepted=False,
                reason="Storage request failed contract validation.",
                storage_event=None,
                validation_failures=tuple(failures),
                mutation_performed=False,
                file_written=False,
                file_deleted=False,
                archive_performed=False,
            )

        return EngineeringModuleStorageResult(
            schema="LEAF_ENGINEERING_MODULE_STORAGE_RESULT_PHASE_28I_V1",
            module_id=request.module_id,
            action=request.action.value,
            domain=request.domain.value,
            canonical_folder=request.canonical_folder(),
            status=EngineeringModuleStorageRequestStatus.ACCEPTED,
            accepted=True,
            reason="Storage request accepted as a structured non-mutating storage event.",
            storage_event={
                "event_type": f"engineering_module.storage.{request.action.value.lower()}",
                "module_id": request.module_id,
                "domain": request.domain.value,
                "canonical_folder": request.canonical_folder(),
                "storage_key": request.storage_key,
                "payload": dict(request.payload),
                "source": "engineering_module_storage_contract",
                "mutation_performed": False,
                "file_written": False,
                "file_deleted": False,
                "archive_performed": False,
            },
            validation_failures=tuple(),
            mutation_performed=False,
            file_written=False,
            file_deleted=False,
            archive_performed=False,
        )

    def report(
        self,
        action: EngineeringModuleStorageAction,
        domain: EngineeringModuleStorageDomain,
        storage_key: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Dict[str, Any]:
        request = self.build_request(
            action=action,
            domain=domain,
            storage_key=storage_key,
            payload=payload,
        )
        result = self.submit(request)

        return {
            "schema": "LEAF_ENGINEERING_MODULE_STORAGE_CONTRACT_PHASE_28I_V1",
            "module_id": self.interface.module_id,
            "request": request.as_dict(),
            "result": result.as_dict(),
            "contract_validation_failures": list(self.validate_contract()),
            "canonical_folders": {
                domain.value: folder for domain, folder in CANONICAL_STORAGE_FOLDERS.items()
            },
            "mutation_performed": False,
            "file_written": False,
            "file_deleted": False,
            "archive_performed": False,
        }


def build_engineering_module_storage_contract(
    interface: EngineeringModuleInterface,
    metadata: Mapping[str, Any] | None = None,
) -> EngineeringModuleStorageContract:
    return EngineeringModuleStorageContract(
        interface=interface,
        metadata=dict(metadata or {}),
    )
