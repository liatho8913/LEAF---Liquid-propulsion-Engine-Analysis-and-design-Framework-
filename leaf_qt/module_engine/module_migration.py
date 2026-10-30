from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ModuleMigrationRecord:
    module_id: str
    migration_status: str
    source_architecture: str
    target_architecture: str
    definition_present: bool
    contract_present: bool
    verification_present: bool
    runtime_present: bool
    engineering_execution_performed: bool
    engineering_behaviour_changed: bool
    legacy_architecture_removed: bool
    next_action: str

    def status(self) -> str:
        required = (
            self.definition_present
            and self.contract_present
            and self.verification_present
            and self.runtime_present
            and not self.engineering_execution_performed
            and not self.engineering_behaviour_changed
        )
        return "PASS" if required else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_id": self.module_id,
            "status": self.status(),
            "migration_status": self.migration_status,
            "source_architecture": self.source_architecture,
            "target_architecture": self.target_architecture,
            "definition_present": self.definition_present,
            "contract_present": self.contract_present,
            "verification_present": self.verification_present,
            "runtime_present": self.runtime_present,
            "engineering_execution_performed": self.engineering_execution_performed,
            "engineering_behaviour_changed": self.engineering_behaviour_changed,
            "legacy_architecture_removed": self.legacy_architecture_removed,
            "next_action": self.next_action,
        }
