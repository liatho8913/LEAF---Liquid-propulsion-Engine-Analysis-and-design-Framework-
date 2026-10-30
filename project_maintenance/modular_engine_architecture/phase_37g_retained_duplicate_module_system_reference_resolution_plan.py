from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37d_safe_duplicate_module_system_retirement_plan import (
    DuplicateModuleSystemRetirementPlanner,
    ROOT,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"

IGNORED_PARTS = {
    ".venv",
    "__pycache__",
    ".git",
    "_external_repository_quarantine",
    "_leaf_repository_cleanup_candidates",
}


@dataclass(frozen=True)
class RetainedReference:
    referenced_candidate: str
    reference_path: str
    reference_kind: str
    recommended_replacement_owner: str
    replacement_action: str


@dataclass(frozen=True)
class RetainedDuplicateResolutionItem:
    candidate_path: str
    category: str
    reference_count: int
    references: list[RetainedReference]
    can_archive_after_resolution: bool
    recommended_next_action: str


@dataclass(frozen=True)
class RetainedDuplicateModuleSystemReferenceResolutionPlan:
    schema: str
    source_schema: str
    retained_candidate_count: int
    total_reference_count: int
    items: list[RetainedDuplicateResolutionItem]
    deletion_performed: bool
    files_modified: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class RetainedDuplicateModuleSystemReferenceResolver:
    """
    Programme 37G.

    Resolves why retained duplicate module-system candidates cannot yet be
    archived.

    Constitutional limits:
    - Planning only.
    - No deletion.
    - No mutation.
    - No new dependency/registry/report engine.
    """

    schema = "LEAF_RETAINED_DUPLICATE_MODULE_REFERENCE_RESOLUTION_PLAN_PHASE_37G_V1"

    def live_python_files(self) -> list[Path]:
        files: list[Path] = []

        for path in ROOT.rglob("*.py"):
            if any(part in IGNORED_PARTS for part in path.parts):
                continue
            files.append(path)

        return sorted(files)

    @staticmethod
    def replacement_owner(category: str) -> str:
        if category == "dependency":
            return "ModuleRuntimeIntegrator dependency visibility"
        if category == "registry":
            return "Canonical Modular Engine registry"
        if category == "availability":
            return "ModuleRuntimeIntegrator availability state"
        return "Canonical Modular Engine"

    @staticmethod
    def reference_tokens(candidate: Path) -> set[str]:
        rel = candidate.relative_to(ROOT)
        return {
            candidate.stem,
            rel.with_suffix("").as_posix(),
            rel.with_suffix("").as_posix().replace("/", "."),
        }

    @staticmethod
    def classify_reference(text: str, tokens: set[str]) -> str:
        if any(f"import {token}" in text for token in tokens):
            return "IMPORT_REFERENCE"
        if any(f"from {token}" in text for token in tokens):
            return "FROM_IMPORT_REFERENCE"
        return "TEXTUAL_REFERENCE"

    def references_to_candidate(self, candidate: Path, category: str) -> list[RetainedReference]:
        if not candidate.exists():
            return []

        tokens = self.reference_tokens(candidate)
        references: list[RetainedReference] = []

        for path in self.live_python_files():
            if path.resolve() == candidate.resolve():
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

            if not any(token in text for token in tokens):
                continue

            references.append(
                RetainedReference(
                    referenced_candidate=str(candidate.relative_to(ROOT)),
                    reference_path=str(path.relative_to(ROOT)),
                    reference_kind=self.classify_reference(text, tokens),
                    recommended_replacement_owner=self.replacement_owner(category),
                    replacement_action=(
                        "REPLACE_WITH_CANONICAL_MODULE_ENGINE_CALL"
                        if category in {"dependency", "registry", "availability"}
                        else "REVIEW_AND_REPLACE_WITH_CANONICAL_OWNER"
                    ),
                )
            )

        return references

    def build(self) -> RetainedDuplicateModuleSystemReferenceResolutionPlan:
        plan = DuplicateModuleSystemRetirementPlanner().build()

        items: list[RetainedDuplicateResolutionItem] = []

        for candidate in plan.items:
            candidate_path = ROOT / candidate.path

            references = self.references_to_candidate(candidate_path, candidate.category)

            if not references:
                continue

            items.append(
                RetainedDuplicateResolutionItem(
                    candidate_path=candidate.path,
                    category=candidate.category,
                    reference_count=len(references),
                    references=references,
                    can_archive_after_resolution=True,
                    recommended_next_action="PATCH_REFERENCES_THEN_ARCHIVE_RETAINED_CANDIDATE",
                )
            )

        total_reference_count = sum(item.reference_count for item in items)

        passed = plan.passed

        return RetainedDuplicateModuleSystemReferenceResolutionPlan(
            schema=self.schema,
            source_schema=plan.schema,
            retained_candidate_count=len(items),
            total_reference_count=total_reference_count,
            items=items,
            deletion_performed=False,
            files_modified=0,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37G_RETAINED_DUPLICATE_MODULE_SYSTEM_REFERENCE_RESOLUTION_PLAN"
                if passed
                else "FAIL_PHASE_37G_RETAINED_DUPLICATE_MODULE_SYSTEM_REFERENCE_RESOLUTION_PLAN"
            ),
            next_programme="Programme 37H — Retained Duplicate Reference Replacement",
        )


def write_report(report: RetainedDuplicateModuleSystemReferenceResolutionPlan) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37g_retained_duplicate_module_system_reference_resolution_plan.json"
    txt_path = REPORT_DIR / "phase_37g_retained_duplicate_module_system_reference_resolution_plan.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37G — Retained Duplicate Module System Reference Resolution Plan",
        "",
        f"schema={report.schema}",
        f"source_schema={report.source_schema}",
        f"retained_candidate_count={report.retained_candidate_count}",
        f"total_reference_count={report.total_reference_count}",
        f"deletion_performed={report.deletion_performed}",
        f"files_modified={report.files_modified}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Retained Candidates",
        "",
    ]

    for item in report.items:
        lines.extend(
            [
                f"candidate_path={item.candidate_path}",
                f"category={item.category}",
                f"reference_count={item.reference_count}",
                f"can_archive_after_resolution={item.can_archive_after_resolution}",
                f"recommended_next_action={item.recommended_next_action}",
                "",
                "references:",
            ]
        )

        for ref in item.references:
            lines.extend(
                [
                    f"  reference_path={ref.reference_path}",
                    f"  reference_kind={ref.reference_kind}",
                    f"  replacement_owner={ref.recommended_replacement_owner}",
                    f"  replacement_action={ref.replacement_action}",
                    "",
                ]
            )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = RetainedDuplicateModuleSystemReferenceResolver().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"total_reference_count={report.total_reference_count}")
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
