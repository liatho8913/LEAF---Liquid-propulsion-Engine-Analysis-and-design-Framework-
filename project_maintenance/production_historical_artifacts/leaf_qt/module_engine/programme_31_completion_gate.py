from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


REQUIRED_PHASE_REPORTS = {
    "31A_module_definition_standard": "phase_31a_module_definition_standard_gate.json",
    "31B_module_discovery_engine": "phase_31b_module_discovery_engine_gate.json",
    "31C_automatic_contract_builder": "phase_31c_automatic_contract_builder_gate.json",
    "31D_automatic_verification_builder": "phase_31d_automatic_verification_builder_gate.json",
    "31E_automatic_runtime_integration": "phase_31e_automatic_runtime_integration_gate.json",
    "31F_regen_migration": "phase_31f_regen_migration_gate.json",
    "31G_combustion_chamber_migration": "phase_31g_combustion_chamber_migration_gate.json",
    "31H_repository_reference_audit": "phase_31h_repository_reference_audit_gate.json",
    "31I_reference_replacement_planning": "phase_31i_reference_replacement_planning_gate.json",
    "31I2_targeted_reference_replacement_engine": "phase_31i2_targeted_reference_replacement_gate.json",
    "31I3_replacement_candidate_expansion_audit": "phase_31i3_replacement_candidate_expansion_audit_gate.json",
    "31I4_controlled_candidate_replacement_dry_run": "phase_31i4_controlled_candidate_replacement_dry_run_gate.json",
    "31I5_controlled_candidate_replacement_application": "phase_31i5_controlled_candidate_replacement_application_gate.json",
    "31I6_post_replacement_audit": "phase_31i6_post_replacement_audit_gate.json",
    "31J_legacy_quarantine_planning": "phase_31j_legacy_quarantine_planning_gate.json",
    "31J2_legacy_quarantine_review_classifier": "phase_31j2_legacy_quarantine_review_classifier_gate.json",
    "31J3_legacy_import_dependency_audit": "phase_31j3_legacy_import_dependency_audit_gate.json",
    "31J4_legacy_quarantine_dry_run": "phase_31j4_legacy_quarantine_dry_run_gate.json",
    "31J5_controlled_legacy_quarantine_application": "phase_31j5_controlled_legacy_quarantine_application_gate.json",
    "31J6_post_quarantine_verification": "phase_31j6_post_quarantine_verification_gate.json",
    "31K_repository_simplification_audit": "phase_31k_repository_simplification_audit_gate.json",
}


@dataclass(frozen=True)
class Programme31CompletionResult:
    status: str
    required_reports_seen: int
    missing_reports: list[str]
    failed_reports: list[str]
    module_engine_files: int
    required_module_engine_files_present: bool
    regen_migrated: bool
    combustion_chamber_migrated: bool
    controlled_replacement_verified: bool
    legacy_quarantine_verified: bool
    repository_simplification_verified: bool
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    next_programme: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


class Programme31CompletionGate:
    REQUIRED_MODULE_ENGINE_FILES = {
        "module_definition.py",
        "module_definition_loader.py",
        "module_definition_registry.py",
        "module_discovery_engine.py",
        "module_contract.py",
        "module_contract_builder.py",
        "module_verification.py",
        "module_verification_builder.py",
        "module_runtime_manifest.py",
        "module_runtime_integrator.py",
        "module_migration.py",
    }

    def __init__(self, root: Path, report_dir: Path):
        self.root = Path(root)
        self.report_dir = Path(report_dir)

    def load_report(self, filename: str) -> dict[str, Any] | None:
        path = self.report_dir / filename
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def module_engine_files_present(self) -> bool:
        existing = {
            path.name
            for path in (self.root / "leaf_qt" / "module_engine").glob("*.py")
            if path.is_file()
        }
        return self.REQUIRED_MODULE_ENGINE_FILES.issubset(existing)

    def count_module_engine_files(self) -> int:
        return len([
            path for path in (self.root / "leaf_qt" / "module_engine").glob("*.py")
            if path.is_file()
        ])

    def run(self) -> Programme31CompletionResult:
        reports = {
            key: self.load_report(filename)
            for key, filename in REQUIRED_PHASE_REPORTS.items()
        }

        missing = [key for key, payload in reports.items() if payload is None]
        failed = [
            key for key, payload in reports.items()
            if payload is not None and payload.get("status") != "PASS"
        ]

        regen_report = reports.get("31F_regen_migration") or {}
        chamber_report = reports.get("31G_combustion_chamber_migration") or {}
        replacement_report = reports.get("31I6_post_replacement_audit") or {}
        quarantine_report = reports.get("31J6_post_quarantine_verification") or {}
        simplification_report = reports.get("31K_repository_simplification_audit") or {}

        regen_migrated = (
            regen_report.get("migration_record", {}).get("status") == "PASS"
            and regen_report.get("module_id") == "regen"
        )

        combustion_chamber_migrated = (
            chamber_report.get("migration_record", {}).get("status") == "PASS"
            and chamber_report.get("module_id") == "combustion_chamber"
        )

        controlled_replacement_verified = (
            replacement_report.get("audit", {}).get("status") == "PASS"
            and replacement_report.get("audit", {}).get("total_remaining_old_phrase_count") == 0
        )

        legacy_quarantine_verified = (
            quarantine_report.get("verification", {}).get("status") == "PASS"
            and quarantine_report.get("verification", {}).get("failed_count") == 0
        )

        repository_simplification_verified = (
            simplification_report.get("audit", {}).get("status") == "PASS"
            and simplification_report.get("audit", {}).get("metrics", {}).get("quarantined_files", 0) >= 74
        )

        engineering_behaviour_changed = any(
            bool((payload or {}).get("engineering_behaviour_changed"))
            for payload in reports.values()
        )

        solver_execution_performed = any(
            bool((payload or {}).get("solver_execution_performed"))
            for payload in reports.values()
        )

        passed = (
            not missing
            and not failed
            and self.module_engine_files_present()
            and regen_migrated
            and combustion_chamber_migrated
            and controlled_replacement_verified
            and legacy_quarantine_verified
            and repository_simplification_verified
            and not engineering_behaviour_changed
            and not solver_execution_performed
        )

        return Programme31CompletionResult(
            status="PASS" if passed else "FAIL",
            required_reports_seen=len([payload for payload in reports.values() if payload is not None]),
            missing_reports=missing,
            failed_reports=failed,
            module_engine_files=self.count_module_engine_files(),
            required_module_engine_files_present=self.module_engine_files_present(),
            regen_migrated=regen_migrated,
            combustion_chamber_migrated=combustion_chamber_migrated,
            controlled_replacement_verified=controlled_replacement_verified,
            legacy_quarantine_verified=legacy_quarantine_verified,
            repository_simplification_verified=repository_simplification_verified,
            engineering_behaviour_changed=engineering_behaviour_changed,
            solver_execution_performed=solver_execution_performed,
            next_programme="Programme 32 — Nozzle Module using Modular Engine",
        )
