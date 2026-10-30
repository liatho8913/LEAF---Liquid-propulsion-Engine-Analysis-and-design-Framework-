from __future__ import annotations

import json
import py_compile
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder, ROOT
from phase_37b_module_cascade_report_integration import ModuleCascadeReportIntegrator
from phase_37c_duplicate_module_system_simplification_audit import DuplicateModuleSystemSimplificationAuditor
from phase_37d_safe_duplicate_module_system_retirement_plan import DuplicateModuleSystemRetirementPlanner
from phase_37g_retained_duplicate_module_system_reference_resolution_plan import RetainedDuplicateModuleSystemReferenceResolver
from phase_37h_retained_duplicate_reference_replacement_readiness import RetainedDuplicateReferenceReplacementReadinessChecker


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


@dataclass(frozen=True)
class CloseoutCompileCheck:
    path: str
    passed: bool
    error: str


@dataclass(frozen=True)
class ModuleSystemSimplificationCloseoutReport:
    schema: str
    visibility_passed: bool
    cascade_passed: bool
    simplification_audit_passed: bool
    retirement_plan_passed: bool
    reference_resolution_passed: bool
    replacement_readiness_passed: bool
    registered_module_count: int
    active_module_count: int
    cascade_row_count: int
    duplicate_candidate_count: int
    planned_retirement_count: int
    retained_candidate_count: int
    retained_reference_count: int
    import_replacement_required_count: int
    manual_review_required_count: int
    compile_checks: list[CloseoutCompileCheck]
    compile_failure_count: int
    duplicate_module_systems_remaining: int
    module_discovery_preserved: bool
    cascade_visibility_preserved: bool
    repository_simplification_verified: bool
    deletion_performed: bool
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class ModuleSystemSimplificationCloseoutVerifier:
    schema = "LEAF_MODULE_SYSTEM_SIMPLIFICATION_CLOSEOUT_VERIFICATION_PHASE_37J_V1"

    def compile_targets(self) -> list[Path]:
        return [
            MODULE_ROOT / "phase_37a_module_dependency_visibility.py",
            MODULE_ROOT / "phase_37b_module_cascade_report_integration.py",
            MODULE_ROOT / "phase_37c_duplicate_module_system_simplification_audit.py",
            MODULE_ROOT / "phase_37d_safe_duplicate_module_system_retirement_plan.py",
            MODULE_ROOT / "phase_37g_retained_duplicate_module_system_reference_resolution_plan.py",
            MODULE_ROOT / "phase_37h_retained_duplicate_reference_replacement_readiness.py",
        ]

    def run_compile_checks(self) -> list[CloseoutCompileCheck]:
        checks: list[CloseoutCompileCheck] = []

        for path in self.compile_targets():
            try:
                py_compile.compile(str(path), doraise=True)
                checks.append(
                    CloseoutCompileCheck(
                        path=str(path.relative_to(ROOT)),
                        passed=True,
                        error="",
                    )
                )
            except Exception as exc:
                checks.append(
                    CloseoutCompileCheck(
                        path=str(path.relative_to(ROOT)),
                        passed=False,
                        error=str(exc),
                    )
                )

        return checks

    def build(self) -> ModuleSystemSimplificationCloseoutReport:
        visibility = ModuleDependencyVisibilityBuilder().build()
        cascade = ModuleCascadeReportIntegrator().build()
        audit = DuplicateModuleSystemSimplificationAuditor().build()
        retirement = DuplicateModuleSystemRetirementPlanner().build()
        resolution = RetainedDuplicateModuleSystemReferenceResolver().build()
        readiness = RetainedDuplicateReferenceReplacementReadinessChecker().build()

        compile_checks = self.run_compile_checks()
        compile_failure_count = sum(1 for check in compile_checks if not check.passed)

        module_discovery_preserved = (
            visibility.passed
            and visibility.registered_module_count == 3
            and visibility.active_module_count == 3
            and visibility.missing_module_dependency_count == 0
            and visibility.inactive_module_dependency_count == 0
        )

        cascade_visibility_preserved = (
            cascade.passed
            and len(cascade.cascade_rows) == visibility.registered_module_count
        )

        repository_simplification_verified = (
            audit.candidate_count == 0
            and retirement.planned_retirement_count == 0
            and resolution.retained_candidate_count == 0
            and readiness.total_reference_count == 0
            and readiness.import_replacement_required_count == 0
            and readiness.manual_review_required_count == 0
        )

        passed = (
            visibility.passed
            and cascade.passed
            and audit.passed
            and retirement.passed
            and resolution.passed
            and readiness.passed
            and module_discovery_preserved
            and cascade_visibility_preserved
            and repository_simplification_verified
            and compile_failure_count == 0
        )

        return ModuleSystemSimplificationCloseoutReport(
            schema=self.schema,
            visibility_passed=visibility.passed,
            cascade_passed=cascade.passed,
            simplification_audit_passed=audit.passed,
            retirement_plan_passed=retirement.passed,
            reference_resolution_passed=resolution.passed,
            replacement_readiness_passed=readiness.passed,
            registered_module_count=visibility.registered_module_count,
            active_module_count=visibility.active_module_count,
            cascade_row_count=len(cascade.cascade_rows),
            duplicate_candidate_count=audit.candidate_count,
            planned_retirement_count=retirement.planned_retirement_count,
            retained_candidate_count=resolution.retained_candidate_count,
            retained_reference_count=resolution.total_reference_count,
            import_replacement_required_count=readiness.import_replacement_required_count,
            manual_review_required_count=readiness.manual_review_required_count,
            compile_checks=compile_checks,
            compile_failure_count=compile_failure_count,
            duplicate_module_systems_remaining=audit.candidate_count,
            module_discovery_preserved=module_discovery_preserved,
            cascade_visibility_preserved=cascade_visibility_preserved,
            repository_simplification_verified=repository_simplification_verified,
            deletion_performed=False,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37J_MODULE_SYSTEM_SIMPLIFICATION_CLOSEOUT_VERIFICATION"
                if passed
                else "FAIL_PHASE_37J_MODULE_SYSTEM_SIMPLIFICATION_CLOSEOUT_VERIFICATION"
            ),
            next_programme="Programme 37K — Programme 37 Completion Gate",
        )


def write_report(report: ModuleSystemSimplificationCloseoutReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37j_module_system_simplification_closeout_verification.json"
    txt_path = REPORT_DIR / "phase_37j_module_system_simplification_closeout_verification.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines = [
        "# LEAF Programme 37J — Module System Simplification Closeout Verification",
        "",
        f"schema={report.schema}",
        f"visibility_passed={report.visibility_passed}",
        f"cascade_passed={report.cascade_passed}",
        f"simplification_audit_passed={report.simplification_audit_passed}",
        f"retirement_plan_passed={report.retirement_plan_passed}",
        f"reference_resolution_passed={report.reference_resolution_passed}",
        f"replacement_readiness_passed={report.replacement_readiness_passed}",
        f"registered_module_count={report.registered_module_count}",
        f"active_module_count={report.active_module_count}",
        f"cascade_row_count={report.cascade_row_count}",
        f"duplicate_candidate_count={report.duplicate_candidate_count}",
        f"planned_retirement_count={report.planned_retirement_count}",
        f"retained_candidate_count={report.retained_candidate_count}",
        f"retained_reference_count={report.retained_reference_count}",
        f"import_replacement_required_count={report.import_replacement_required_count}",
        f"manual_review_required_count={report.manual_review_required_count}",
        f"compile_failure_count={report.compile_failure_count}",
        f"duplicate_module_systems_remaining={report.duplicate_module_systems_remaining}",
        f"module_discovery_preserved={report.module_discovery_preserved}",
        f"cascade_visibility_preserved={report.cascade_visibility_preserved}",
        f"repository_simplification_verified={report.repository_simplification_verified}",
        f"deletion_performed={report.deletion_performed}",
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
    report = ModuleSystemSimplificationCloseoutVerifier().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"cascade_row_count={report.cascade_row_count}")
    print(f"duplicate_candidate_count={report.duplicate_candidate_count}")
    print(f"planned_retirement_count={report.planned_retirement_count}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"retained_reference_count={report.retained_reference_count}")
    print(f"import_replacement_required_count={report.import_replacement_required_count}")
    print(f"manual_review_required_count={report.manual_review_required_count}")
    print(f"compile_failure_count={report.compile_failure_count}")
    print(f"module_discovery_preserved={report.module_discovery_preserved}")
    print(f"cascade_visibility_preserved={report.cascade_visibility_preserved}")
    print(f"repository_simplification_verified={report.repository_simplification_verified}")
    print(f"deletion_performed={report.deletion_performed}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
