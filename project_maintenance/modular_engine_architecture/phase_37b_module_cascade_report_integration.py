from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37a_module_dependency_visibility import (
    ModuleDependencyVisibilityBuilder,
    ROOT,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


@dataclass(frozen=True)
class ModuleCascadeReportRow:
    module: str
    status: str
    activation_cascade: list[str]
    deactivation_cascade: list[str]
    module_dependencies: list[str]
    infrastructure_dependencies: list[str]


@dataclass(frozen=True)
class ModuleCascadeReport:
    schema: str
    source_schema: str
    report_owner: str
    registered_module_count: int
    active_module_count: int
    cascade_rows: list[ModuleCascadeReportRow]
    missing_module_dependency_count: int
    inactive_module_dependency_count: int
    duplicate_dependency_systems_detected: int
    duplicate_registry_systems_detected: int
    duplicate_availability_systems_detected: int
    new_dependency_engine_created: bool
    new_registry_created: bool
    new_report_engine_created: bool
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class ModuleCascadeReportIntegrator:
    """
    Programme 37B.

    Converts existing 37A visibility into a report-owned cascade summary.

    Constitutional limits:
    - Reuses 37A visibility builder.
    - Does not own dependencies.
    - Does not own registration.
    - Does not create report infrastructure.
    - Does not alter module activation.
    """

    schema = "LEAF_MODULE_CASCADE_REPORT_INTEGRATION_PHASE_37B_V1"

    def build(self) -> ModuleCascadeReport:
        visibility = ModuleDependencyVisibilityBuilder().build()

        rows = [
            ModuleCascadeReportRow(
                module=node.name,
                status=node.status,
                activation_cascade=node.activation_cascade,
                deactivation_cascade=node.deactivation_cascade,
                module_dependencies=node.module_dependencies,
                infrastructure_dependencies=node.infrastructure_dependencies,
            )
            for node in visibility.module_nodes
        ]

        passed = (
            visibility.passed
            and visibility.missing_module_dependency_count == 0
            and visibility.inactive_module_dependency_count == 0
            and bool(rows)
        )

        return ModuleCascadeReport(
            schema=self.schema,
            source_schema=visibility.schema,
            report_owner="LEAF Operating System Report Infrastructure",
            registered_module_count=visibility.registered_module_count,
            active_module_count=visibility.active_module_count,
            cascade_rows=rows,
            missing_module_dependency_count=visibility.missing_module_dependency_count,
            inactive_module_dependency_count=visibility.inactive_module_dependency_count,
            duplicate_dependency_systems_detected=visibility.duplicate_dependency_systems_detected,
            duplicate_registry_systems_detected=visibility.duplicate_registry_systems_detected,
            duplicate_availability_systems_detected=visibility.duplicate_availability_systems_detected,
            new_dependency_engine_created=False,
            new_registry_created=False,
            new_report_engine_created=False,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37B_MODULE_CASCADE_REPORT_INTEGRATION"
                if passed
                else "FAIL_PHASE_37B_MODULE_CASCADE_REPORT_INTEGRATION"
            ),
            next_programme="Programme 37C — Duplicate Module System Simplification Audit",
        )


def write_report(report: ModuleCascadeReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37b_module_cascade_report.json"
    txt_path = REPORT_DIR / "phase_37b_module_cascade_report.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37B — Module Cascade Report Integration",
        "",
        f"schema={report.schema}",
        f"source_schema={report.source_schema}",
        f"report_owner={report.report_owner}",
        f"registered_module_count={report.registered_module_count}",
        f"active_module_count={report.active_module_count}",
        f"missing_module_dependency_count={report.missing_module_dependency_count}",
        f"inactive_module_dependency_count={report.inactive_module_dependency_count}",
        f"duplicate_dependency_systems_detected={report.duplicate_dependency_systems_detected}",
        f"duplicate_registry_systems_detected={report.duplicate_registry_systems_detected}",
        f"duplicate_availability_systems_detected={report.duplicate_availability_systems_detected}",
        f"new_dependency_engine_created={report.new_dependency_engine_created}",
        f"new_registry_created={report.new_registry_created}",
        f"new_report_engine_created={report.new_report_engine_created}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Cascades",
        "",
    ]

    for row in report.cascade_rows:
        lines.extend(
            [
                f"module={row.module}",
                f"status={row.status}",
                f"module_dependencies={row.module_dependencies}",
                f"infrastructure_dependencies={row.infrastructure_dependencies}",
                f"activation_cascade={row.activation_cascade}",
                f"deactivation_cascade={row.deactivation_cascade}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = ModuleCascadeReportIntegrator().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"registered_module_count={report.registered_module_count}")
    print(f"active_module_count={report.active_module_count}")
    print(f"missing_module_dependency_count={report.missing_module_dependency_count}")
    print(f"inactive_module_dependency_count={report.inactive_module_dependency_count}")
    print(f"new_dependency_engine_created={report.new_dependency_engine_created}")
    print(f"new_registry_created={report.new_registry_created}")
    print(f"new_report_engine_created={report.new_report_engine_created}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
