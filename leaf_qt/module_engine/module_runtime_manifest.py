from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ACTIVE = "Active"
USER_DEACTIVATED = "UserDeactivated"
DEPENDENCY_DEACTIVATED = "DependencyDeactivated"
BLOCKED = "Blocked"


@dataclass(frozen=True)
class ModuleRuntimeRecord:
    module_id: str
    module_name: str
    domain: str
    version: str
    entrypoint: str
    runtime_binding: str
    engineering_owner: str
    runtime_owner: str
    verification_status: str
    runtime_status: str
    outputs: list[str]
    dependencies: list[str]
    enabled: bool = True
    requires_modules: list[str] | None = None
    activation_status: str = ACTIVE
    activation_reason: str = "Module enabled and dependencies active."

    @property
    def active_outputs(self) -> list[str]:
        return self.outputs if self.activation_status == ACTIVE else []

    @property
    def can_user_activate(self) -> bool:
        return self.activation_status in {ACTIVE, USER_DEACTIVATED}

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "module_name": self.module_name,
            "domain": self.domain,
            "version": self.version,
            "entrypoint": self.entrypoint,
            "runtime_binding": self.runtime_binding,
            "engineering_owner": self.engineering_owner,
            "runtime_owner": self.runtime_owner,
            "verification_status": self.verification_status,
            "runtime_status": self.runtime_status,
            "outputs": self.outputs,
            "active_outputs": self.active_outputs,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
            "requires_modules": list(self.requires_modules or []),
            "activation_status": self.activation_status,
            "activation_reason": self.activation_reason,
            "can_user_activate": self.can_user_activate,
        }


@dataclass(frozen=True)
class ModuleRuntimeManifest:
    records: dict[str, ModuleRuntimeRecord]

    def ids(self) -> list[str]:
        return sorted(self.records)

    def ready_ids(self) -> list[str]:
        return sorted(k for k, v in self.records.items() if v.runtime_status == "READY")

    def blocked_ids(self) -> list[str]:
        return sorted(k for k, v in self.records.items() if v.runtime_status == "BLOCKED")

    def active_ids(self) -> list[str]:
        return sorted(k for k, v in self.records.items() if v.activation_status == ACTIVE)

    def deactivated_ids(self) -> list[str]:
        return sorted(k for k, v in self.records.items() if v.activation_status != ACTIVE)

    def user_deactivated_ids(self) -> list[str]:
        return sorted(k for k, v in self.records.items() if v.activation_status == USER_DEACTIVATED)

    def dependency_deactivated_ids(self) -> list[str]:
        return sorted(k for k, v in self.records.items() if v.activation_status == DEPENDENCY_DEACTIVATED)

    def status(self) -> str:
        return "PASS" if self.records and not self.blocked_ids() else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status(),
            "module_count": len(self.records),
            "ready_modules": self.ready_ids(),
            "blocked_modules": self.blocked_ids(),
            "active_modules": self.active_ids(),
            "deactivated_modules": self.deactivated_ids(),
            "user_deactivated_modules": self.user_deactivated_ids(),
            "dependency_deactivated_modules": self.dependency_deactivated_ids(),
            "records": {k: v.to_dict() for k, v in sorted(self.records.items())},
        }
