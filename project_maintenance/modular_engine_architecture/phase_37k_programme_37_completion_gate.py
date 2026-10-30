from __future__ import annotations

import json
import py_compile
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder, ROOT
from phase_37b_module_cascade_report_integration import ModuleCascadeReportIntegrator
from phase_37j_module_system_simplification_closeout_verification import (
    ModuleSystemSimplificationCloseoutVerifier,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


@dataclass(frozen=True)
class Programme37CompletionGateReport:
    schema: str
    dependency_visibility_passed: bool
    cascade_report_passed: bool
    closeout_verification_passed: bool
    registered_module_count: int
    active_module_count: int
    cascade_row_count: int
    duplicate_candidate_count: int
    retained_candidate_count: int
    retained_reference_count: int
    compile_failure_count: int
    module_discovery_preserved: bool
    cascade_visibility_preserved: bool
    repository_simplification_verified: bool
    duplicate_module_systems_remaining: int
    archival_permanent_deletion_performed: bool
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    programme_complete: bool
    completion_notice: str
    next_programme: str


class Programme37CompletionGate:
    schema = "LEAF_PROGRAMME_37_COMPLETION_GATE_V1"

    def compile_targets(self) -> list[Path]:
        return [
            MODULE_ROOT / "phase_37a_module_dependency_visibility.py",
            MODULE_ROOT / "phase_37b_module_cascade_report_integration.py",
            MODULE_ROOT / "phase_37c_duplicate_module_system_simplification_audit.py",
            MODULE_ROOT / "phase_37d_safe_duplicate_module_system_retirement_plan.py",
            MODULE_ROOT / "phase_37g_retained_duplicate_module_system_reference_resolution_plan.py",
            MODULE_ROOT / "phase_37h_retained_duplicate_reference_replacement_readiness.py",
            MODULE_ROOT / "phase_37j_module_system_simplification_closeout_verification.py",
            MODULE_ROOT / "phase_37k_programme_37_completion_gate.py",
        ]

    def compile_failure_count(self) -> int:
        failures = 0

        for path in self.compile_targets():
            try:
                py_compile.compile(str(path), doraise=True)
            except Exception:
                failures += 1

        return failures

    def build(self) -> Programme37CompletionGateReport:
        visibility = ModuleDependencyVisibilityBuilder().build()
        cascade = ModuleCascadeReportIntegrator().build()
        closeout = ModuleSystemSimplificationCloseoutVerifier().build()

        compile_failures = self.compile_failure_count()

        programme_complete = (
            visibility.passed
            and cascade.passed
            and closeout.passed
            and visibility.registered_module_count == 3
            and visibility.active_module_count == 3
            and len(cascade.cascade_rows) == 3
            and closeout.duplicate_candidate_count == 0
            and closeout.retained_candidate_count == 0
            and closeout.retained_reference_count == 0
            and closeout.repository_simplification_verified
            and closeout.module_discovery_preserved
            and closeout.cascade_visibility_preserved
            and closeout.duplicate_module_systems_remaining == 0
            and compile_failures == 0
        )

        return Programme37CompletionGateReport(
            schema=self.schema,
            dependency_visibility_passed=visibility.passed,
            cascade_report_passed=cascade.passed,
            closeout_verification_passed=closeout.passed,
            registered_module_count=visibility.registered_module_count,
            active_module_count=visibility.active_module_count,
            cascade_row_count=len(cascade.cascade_rows),
            duplicate_candidate_count=closeout.duplicate_candidate_count,
            retained_candidate_count=closeout.retained_candidate_count,
            retained_reference_count=closeout.retained_reference_count,
            compile_failure_count=compile_failures,
            module_discovery_preserved=closeout.module_discovery_preserved,
            cascade_visibility_preserved=closeout.cascade_visibility_preserved,
            repository_simplification_verified=closeout.repository_simplification_verified,
            duplicate_module_systems_remaining=closeout.duplicate_module_systems_remaining,
            archival_permanent_deletion_performed=False,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            programme_complete=programme_complete,
            completion_notice=(
                "PASS_PHASE_37K_PROGRAMME_37_COMPLETION_GATE"
                if programme_complete
                else "FAIL_PHASE_37K_PROGRAMME_37_COMPLETION_GATE"
            ),
            next_programme="Programme 38 — Module Control Surface Hardening",
        )


def write_report(report: Programme37CompletionGateReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37k_programme_37_completion_gate.json"
    txt_path = REPORT_DIR / "phase_37k_programme_37_completion_gate.txt"

    json_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "# LEAF Programme 37K — Programme 37 Completion Gate",
                "",
                f"schema={report.schema}",
                f"dependency_visibility_passed={report.dependency_visibility_passed}",
                f"cascade_report_passed={report.cascade_report_passed}",
                f"closeout_verification_passed={report.closeout_verification_passed}",
                f"registered_module_count={report.registered_module_count}",
                f"active_module_count={report.active_module_count}",
                f"cascade_row_count={report.cascade_row_count}",
                f"duplicate_candidate_count={report.duplicate_candidate_count}",
                f"retained_candidate_count={report.retained_candidate_count}",
                f"retained_reference_count={report.retained_reference_count}",
                f"compile_failure_count={report.compile_failure_count}",
                f"module_discovery_preserved={report.module_discovery_preserved}",
                f"cascade_visibility_preserved={report.cascade_visibility_preserved}",
                f"repository_simplification_verified={report.repository_simplification_verified}",
                f"duplicate_module_systems_remaining={report.duplicate_module_systems_remaining}",
                f"archival_permanent_deletion_performed={report.archival_permanent_deletion_performed}",
                f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
                f"solver_execution_performed={report.solver_execution_performed}",
                f"programme_complete={report.programme_complete}",
                f"completion_notice={report.completion_notice}",
                f"next_programme={report.next_programme}",
            ]
        ),
        encoding="utf-8",
    )

    return txt_path, json_path


def main() -> None:
    report = Programme37CompletionGate().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"dependency_visibility_passed={report.dependency_visibility_passed}")
    print(f"cascade_report_passed={report.cascade_report_passed}")
    print(f"closeout_verification_passed={report.closeout_verification_passed}")
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"cascade_row_count={report.cascade_row_count}")
    print(f"duplicate_candidate_count={report.duplicate_candidate_count}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"retained_reference_count={report.retained_reference_count}")
    print(f"compile_failure_count={report.compile_failure_count}")
    print(f"module_discovery_preserved={report.module_discovery_preserved}")
    print(f"cascade_visibility_preserved={report.cascade_visibility_preserved}")
    print(f"repository_simplification_verified={report.repository_simplification_verified}")
    print(f"duplicate_module_systems_remaining={report.duplicate_module_systems_remaining}")
    print(f"archival_permanent_deletion_performed={report.archival_permanent_deletion_performed}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"programme_complete={report.programme_complete}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.programme_complete:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
