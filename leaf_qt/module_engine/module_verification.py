from __future__ import annotations

from dataclasses import dataclass
from typing import Any


STANDARD_VERIFICATION_TYPES = (
    "compatibility",
    "dependency",
    "readiness",
    "completion",
    "cross_platform",
)


@dataclass(frozen=True)
class ModuleVerificationCheck:
    module_id: str
    verification_type: str
    owner: str
    status: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "verification_type": self.verification_type,
            "owner": self.owner,
            "status": self.status,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ModuleVerificationPlan:
    module_id: str
    checks: list[ModuleVerificationCheck]

    def status(self) -> str:
        return "PASS" if all(check.status == "PASS" for check in self.checks) else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "status": self.status(),
            "checks": [check.to_dict() for check in self.checks],
        }
