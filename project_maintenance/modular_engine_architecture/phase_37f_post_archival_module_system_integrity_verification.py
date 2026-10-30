from __future__ import annotations

import json
import py_compile
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder, ROOT
from phase_37b_module_cascade_report_integration import ModuleCascadeReportIntegrator
from phase_37e_reference_checked_duplicate_module_system_archival import (
    ReferenceCheckedDuplicateModuleSystemArchiver,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


@dataclass(frozen=True)
class CompileCheckResult:
    path: str
    passed: bool
    error: str


@dataclass(frozen=True)
class PostArchivalModuleSystemIntegrityReport:
    schema: str
    visibility_schema: str
    cascade_schema: str
    archival_schema: str
    registered_module_count: int
    active_module_count: int
    missing_module_dependency_count: int
    inactive_module_dependency_count: int
    cascade_row_count: int
    archived_count: int
    retained_count: int
    rollback_available_count: int
    compile_checks: list[CompileCheckResult]
    compile_failure_count: int
    module_discovery_preserved: bool
    cascade_reporting_preserved: bool
    rollback_paths_preserved: bool
    permanent_deletion_detected: bool
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class PostArchivalModuleSystemIntegrityVerifier:
    """
    Programme 37F.

    Verifies that 37E archival did not break existing Modular Engine visibility.

    Constitutional limits:
    - Verification only.
    - No deletion.
    - No mutation.
    - No solver execution.
    - No engineering behaviour changes.
    """

    schema = "LEAF_POST_ARCHIVAL_MODULE_SYSTEM_INTEGRITY_VERIFICATION_PHASE_37F_V1"

    def compile_targets(self) -> list[Path]:
        return [
            MODULE_ROOT / "phase_37a_module_dependency_visibility.py",
            MODULE_ROOT / "phase_37b_module_cascade_report_integration.py",
            MODULE_ROOT / "phase_37c_duplicate_module_system_simplification_audit.py",
            MODULE_ROOT / "phase_37d_safe_duplicate_module_system_retirement_plan.py",
            MODULE_ROOT / "phase_37e_reference_checked_duplicate_module_system_archival.py",
        ]

    def run_compile_checks(self) -> list[CompileCheckResult]:
        results: list[CompileCheckResult] = []

        for path in self.compile_targets():
            try:
                py_compile.compile(str(path), doraise=True)
                results.append(
                    CompileCheckResult(
                        path=str(path.relative_to(ROOT)),
                        passed=True,
                        error="",
                    )
                )
            except Exception as exc:
                results.append(
                    CompileCheckResult(
                        path=str(path.relative_to(ROOT)),
                        passed=False,
                        error=str(exc),
                    )
                )

        return results

    def build(self) -> PostArchivalModuleSystemIntegrityReport:
        visibility = ModuleDependencyVisibilityBuilder().build()
        cascade = ModuleCascadeReportIntegrator().build()
        archival = ReferenceCheckedDuplicateModuleSystemArchiver().build()

        compile_checks = self.run_compile_checks()
        compile_failure_count = sum(1 for result in compile_checks if not result.passed)

        rollback_available_count = sum(
            1 for result in archival.results
            if result.archived and result.rollback_available
        )

        module_discovery_preserved = (
            visibility.passed
            and visibility.registered_module_count >= 3
            and visibility.active_module_count == visibility.registered_module_count
            and visibility.missing_module_dependency_count == 0
            and visibility.inactive_module_dependency_count == 0
        )

        cascade_reporting_preserved = (
            cascade.passed
            and cascade.registered_module_count == visibility.registered_module_count
            and len(cascade.cascade_rows) == visibility.registered_module_count
        )

        rollback_paths_preserved = rollback_available_count == archival.archived_count

        permanent_deletion_detected = archival.deletion_performed

        passed = (
            module_discovery_preserved
            and cascade_reporting_preserved
            and rollback_paths_preserved
            and not permanent_deletion_detected
            and compile_failure_count == 0
        )

        return PostArchivalModuleSystemIntegrityReport(
            schema=self.schema,
            visibility_schema=visibility.schema,
            cascade_schema=cascade.schema,
            archival_schema=archival.schema,
            registered_module_count=visibility.registered_module_count,
            active_module_count=visibility.active_module_count,
            missing_module_dependency_count=visibility.missing_module_dependency_count,
            inactive_module_dependency_count=visibility.inactive_module_dependency_count,
            cascade_row_count=len(cascade.cascade_rows),
            archived_count=archival.archived_count,
            retained_count=archival.retained_count,
            rollback_available_count=rollback_available_count,
            compile_checks=compile_checks,
            compile_failure_count=compile_failure_count,
            module_discovery_preserved=module_discovery_preserved,
            cascade_reporting_preserved=cascade_reporting_preserved,
            rollback_paths_preserved=rollback_paths_preserved,
            permanent_deletion_detected=permanent_deletion_detected,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37F_POST_ARCHIVAL_MODULE_SYSTEM_INTEGRITY_VERIFICATION"
                if passed
                else "FAIL_PHASE_37F_POST_ARCHIVAL_MODULE_SYSTEM_INTEGRITY_VERIFICATION"
            ),
            next_programme="Programme 37G — Retained Duplicate Module System Reference Resolution Plan",
        )


def write_report(report: PostArchivalModuleSystemIntegrityReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37f_post_archival_module_system_integrity_verification.json"
    txt_path = REPORT_DIR / "phase_37f_post_archival_module_system_integrity_verification.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37F — Post-Archival Module System Integrity Verification",
        "",
        f"schema={report.schema}",
        f"visibility_schema={report.visibility_schema}",
        f"cascade_schema={report.cascade_schema}",
        f"archival_schema={report.archival_schema}",
        f"registered_module_count={report.registered_module_count}",
        f"active_module_count={report.active_module_count}",
        f"missing_module_dependency_count={report.missing_module_dependency_count}",
        f"inactive_module_dependency_count={report.inactive_module_dependency_count}",
        f"cascade_row_count={report.cascade_row_count}",
        f"archived_count={report.archived_count}",
        f"retained_count={report.retained_count}",
        f"rollback_available_count={report.rollback_available_count}",
        f"compile_failure_count={report.compile_failure_count}",
        f"module_discovery_preserved={report.module_discovery_preserved}",
        f"cascade_reporting_preserved={report.cascade_reporting_preserved}",
        f"rollback_paths_preserved={report.rollback_paths_preserved}",
        f"permanent_deletion_detected={report.permanent_deletion_detected}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Compile Checks",
        "",
    ]

    for check in report.compile_checks:
        lines.extend(
            [
                f"path={check.path}",
                f"passed={check.passed}",
                f"error={check.error}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = PostArchivalModuleSystemIntegrityVerifier().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"missing_module_dependency_count={report.missing_module_dependency_count}")
    print(f"inactive_module_dependency_count={report.inactive_module_dependency_count}")
    print(f"cascade_row_count={report.cascade_row_count}")
    print(f"archived_count={report.archived_count}")
    print(f"retained_count={report.retained_count}")
    print(f"rollback_available_count={report.rollback_available_count}")
    print(f"compile_failure_count={report.compile_failure_count}")
    print(f"module_discovery_preserved={report.module_discovery_preserved}")
    print(f"cascade_reporting_preserved={report.cascade_reporting_preserved}")
    print(f"rollback_paths_preserved={report.rollback_paths_preserved}")
    print(f"permanent_deletion_detected={report.permanent_deletion_detected}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
