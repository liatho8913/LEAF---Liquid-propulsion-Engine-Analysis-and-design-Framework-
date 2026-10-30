from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37c_duplicate_module_system_simplification_audit import (
    DuplicateModuleSystemSimplificationAuditor,
    ROOT,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"
RETIREMENT_ARCHIVE_ROOT = ROOT / "_leaf_repository_cleanup_candidates" / "module_system_retirement_candidates"


@dataclass(frozen=True)
class DuplicateModuleSystemRetirementPlanItem:
    path: str
    category: str
    risk_level: str
    replacement_owner: str
    archive_target: str
    removal_allowed_now: bool
    recommended_action: str
    reason: str


@dataclass(frozen=True)
class DuplicateModuleSystemRetirementPlan:
    schema: str
    source_schema: str
    candidate_count: int
    planned_retirement_count: int
    removal_allowed_now_count: int
    archive_root: str
    items: list[DuplicateModuleSystemRetirementPlanItem]
    deletion_performed: bool
    files_modified: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class DuplicateModuleSystemRetirementPlanner:
    """
    Programme 37D.

    Produces a safe retirement plan for duplicate module-system candidates.

    Constitutional limits:
    - Planning only.
    - No deletion.
    - No file mutation.
    - No new runtime/dependency/registry/report engine.
    """

    schema = "LEAF_DUPLICATE_MODULE_SYSTEM_RETIREMENT_PLAN_PHASE_37D_V1"

    def classify_risk(self, imports_canonical_module_engine: bool, line_count: int) -> str:
        if imports_canonical_module_engine:
            return "MEDIUM_COMPATIBILITY_LAYER_REVIEW_REQUIRED"

        if line_count <= 80:
            return "LOW_SMALL_STANDALONE_CANDIDATE"

        return "MEDIUM_REVIEW_REQUIRED"

    def replacement_owner(self, category: str) -> str:
        if category == "dependency":
            return "ModuleRuntimeIntegrator dependency visibility"

        if category == "registry":
            return "Canonical Modular Engine registry"

        if category == "availability":
            return "ModuleRuntimeIntegrator availability state"

        return "Canonical Modular Engine"

    def build_item(self, candidate) -> DuplicateModuleSystemRetirementPlanItem:
        archive_target = RETIREMENT_ARCHIVE_ROOT / candidate.path

        risk_level = self.classify_risk(
            candidate.imports_canonical_module_engine,
            candidate.line_count,
        )

        removal_allowed_now = False

        recommended_action = (
            "COMPARE_IMPORT_USAGE_THEN_ARCHIVE_IN_37E"
            if risk_level.startswith("LOW")
            else "REVIEW_REFERENCES_BEFORE_ARCHIVE"
        )

        return DuplicateModuleSystemRetirementPlanItem(
            path=candidate.path,
            category=candidate.category,
            risk_level=risk_level,
            replacement_owner=self.replacement_owner(candidate.category),
            archive_target=str(archive_target.relative_to(ROOT)),
            removal_allowed_now=removal_allowed_now,
            recommended_action=recommended_action,
            reason=(
                "Candidate may duplicate module-system responsibility outside the canonical "
                "Modular Engine ownership boundary. Retirement must be reference-checked before deletion."
            ),
        )

    def build(self) -> DuplicateModuleSystemRetirementPlan:
        audit = DuplicateModuleSystemSimplificationAuditor().build()

        items = [self.build_item(candidate) for candidate in audit.candidates]

        removal_allowed_now_count = sum(1 for item in items if item.removal_allowed_now)

        passed = (
            audit.passed
            and audit.deletion_performed is False
            and audit.files_modified == 0
        )

        return DuplicateModuleSystemRetirementPlan(
            schema=self.schema,
            source_schema=audit.schema,
            candidate_count=audit.candidate_count,
            planned_retirement_count=len(items),
            removal_allowed_now_count=removal_allowed_now_count,
            archive_root=str(RETIREMENT_ARCHIVE_ROOT.relative_to(ROOT)),
            items=items,
            deletion_performed=False,
            files_modified=0,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37D_SAFE_DUPLICATE_MODULE_SYSTEM_RETIREMENT_PLAN"
                if passed
                else "FAIL_PHASE_37D_SAFE_DUPLICATE_MODULE_SYSTEM_RETIREMENT_PLAN"
            ),
            next_programme="Programme 37E — Reference-Checked Duplicate Module System Archival",
        )


def write_report(report: DuplicateModuleSystemRetirementPlan) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37d_safe_duplicate_module_system_retirement_plan.json"
    txt_path = REPORT_DIR / "phase_37d_safe_duplicate_module_system_retirement_plan.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37D — Safe Duplicate Module System Retirement Plan",
        "",
        f"schema={report.schema}",
        f"source_schema={report.source_schema}",
        f"candidate_count={report.candidate_count}",
        f"planned_retirement_count={report.planned_retirement_count}",
        f"removal_allowed_now_count={report.removal_allowed_now_count}",
        f"archive_root={report.archive_root}",
        f"deletion_performed={report.deletion_performed}",
        f"files_modified={report.files_modified}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Retirement Plan Items",
        "",
    ]

    for item in report.items:
        lines.extend(
            [
                f"path={item.path}",
                f"category={item.category}",
                f"risk_level={item.risk_level}",
                f"replacement_owner={item.replacement_owner}",
                f"archive_target={item.archive_target}",
                f"removal_allowed_now={item.removal_allowed_now}",
                f"recommended_action={item.recommended_action}",
                f"reason={item.reason}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = DuplicateModuleSystemRetirementPlanner().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"candidate_count={report.candidate_count}")
    print(f"planned_retirement_count={report.planned_retirement_count}")
    print(f"removal_allowed_now_count={report.removal_allowed_now_count}")
    print(f"archive_root={report.archive_root}")
    print(f"deletion_performed={report.deletion_performed}")
    print(f"files_modified={report.files_modified}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
