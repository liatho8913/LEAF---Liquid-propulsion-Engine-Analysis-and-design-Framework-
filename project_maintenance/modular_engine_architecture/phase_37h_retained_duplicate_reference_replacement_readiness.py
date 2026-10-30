from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37g_retained_duplicate_module_system_reference_resolution_plan import (
    RetainedDuplicateModuleSystemReferenceResolver,
    ROOT,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


@dataclass(frozen=True)
class ReplacementReadinessReference:
    candidate_path: str
    reference_path: str
    category: str
    reference_kind: str
    contains_python_import: bool
    contains_runtime_usage: bool
    contains_text_only_reference: bool
    replacement_classification: str
    recommended_action: str


@dataclass(frozen=True)
class RetainedDuplicateReferenceReplacementReadinessReport:
    schema: str
    source_schema: str
    retained_candidate_count: int
    total_reference_count: int
    auto_replace_allowed_count: int
    manual_review_required_count: int
    text_only_reference_count: int
    import_replacement_required_count: int
    references: list[ReplacementReadinessReference]
    deletion_performed: bool
    files_modified: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class RetainedDuplicateReferenceReplacementReadinessChecker:
    """
    Programme 37H.

    Classifies retained duplicate references before mutation.

    Constitutional limits:
    - No mutation.
    - No deletion.
    - No solver execution.
    - No engineering behaviour changes.
    - Prevents blind text replacement.
    """

    schema = "LEAF_RETAINED_DUPLICATE_REFERENCE_REPLACEMENT_READINESS_PHASE_37H_V1"

    @staticmethod
    def read_text(path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except Exception:
            return ""

    @staticmethod
    def ast_imports_candidate(text: str, candidate_path: str) -> bool:
        candidate_stem = Path(candidate_path).stem
        candidate_module = Path(candidate_path).with_suffix("").as_posix().replace("/", ".")

        try:
            tree = ast.parse(text)
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.endswith(candidate_stem) or alias.name == candidate_module:
                        return True

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.endswith(candidate_stem) or module == candidate_module:
                    return True

        return False

    @staticmethod
    def contains_runtime_usage(text: str, candidate_path: str) -> bool:
        stem = Path(candidate_path).stem

        runtime_tokens = {
            f"{stem}.",
            f"{stem}(",
            f"from {stem}",
            f"import {stem}",
        }

        return any(token in text for token in runtime_tokens)

    @staticmethod
    def classify(
        reference_kind: str,
        contains_python_import: bool,
        contains_runtime_usage: bool,
        reference_path: str,
    ) -> tuple[str, str]:
        lower_path = reference_path.lower()

        if "/reports/" in lower_path or lower_path.endswith(".txt") or lower_path.endswith(".json"):
            return (
                "TEXT_ONLY_REFERENCE",
                "DO_NOT_PATCH_REPORT_HISTORY",
            )

        if contains_python_import:
            return (
                "IMPORT_REPLACEMENT_REQUIRED",
                "PATCH_IMPORT_TO_CANONICAL_MODULE_ENGINE_OWNER_IN_37I",
            )

        if contains_runtime_usage:
            return (
                "MANUAL_REVIEW_REQUIRED",
                "REVIEW_RUNTIME_CALL_BEFORE_PATCHING",
            )

        if reference_kind == "TEXTUAL_REFERENCE":
            return (
                "TEXT_ONLY_REFERENCE",
                "LEAVE_AS_HISTORICAL_OR_REPORT_REFERENCE",
            )

        return (
            "MANUAL_REVIEW_REQUIRED",
            "REVIEW_BEFORE_MUTATION",
        )

    def build(self) -> RetainedDuplicateReferenceReplacementReadinessReport:
        resolution = RetainedDuplicateModuleSystemReferenceResolver().build()

        readiness_refs: list[ReplacementReadinessReference] = []

        for item in resolution.items:
            for ref in item.references:
                reference_path = ROOT / ref.reference_path
                text = self.read_text(reference_path)

                contains_python_import = self.ast_imports_candidate(
                    text,
                    item.candidate_path,
                )

                contains_runtime_usage = self.contains_runtime_usage(
                    text,
                    item.candidate_path,
                )

                classification, action = self.classify(
                    ref.reference_kind,
                    contains_python_import,
                    contains_runtime_usage,
                    ref.reference_path,
                )

                readiness_refs.append(
                    ReplacementReadinessReference(
                        candidate_path=item.candidate_path,
                        reference_path=ref.reference_path,
                        category=item.category,
                        reference_kind=ref.reference_kind,
                        contains_python_import=contains_python_import,
                        contains_runtime_usage=contains_runtime_usage,
                        contains_text_only_reference=classification == "TEXT_ONLY_REFERENCE",
                        replacement_classification=classification,
                        recommended_action=action,
                    )
                )

        auto_count = sum(
            1 for ref in readiness_refs
            if ref.replacement_classification == "AUTO_REPLACE_ALLOWED"
        )
        manual_count = sum(
            1 for ref in readiness_refs
            if ref.replacement_classification == "MANUAL_REVIEW_REQUIRED"
        )
        text_count = sum(
            1 for ref in readiness_refs
            if ref.replacement_classification == "TEXT_ONLY_REFERENCE"
        )
        import_count = sum(
            1 for ref in readiness_refs
            if ref.replacement_classification == "IMPORT_REPLACEMENT_REQUIRED"
        )

        passed = resolution.passed and len(readiness_refs) == resolution.total_reference_count

        return RetainedDuplicateReferenceReplacementReadinessReport(
            schema=self.schema,
            source_schema=resolution.schema,
            retained_candidate_count=resolution.retained_candidate_count,
            total_reference_count=resolution.total_reference_count,
            auto_replace_allowed_count=auto_count,
            manual_review_required_count=manual_count,
            text_only_reference_count=text_count,
            import_replacement_required_count=import_count,
            references=readiness_refs,
            deletion_performed=False,
            files_modified=0,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37H_RETAINED_DUPLICATE_REFERENCE_REPLACEMENT_READINESS"
                if passed
                else "FAIL_PHASE_37H_RETAINED_DUPLICATE_REFERENCE_REPLACEMENT_READINESS"
            ),
            next_programme="Programme 37I — Minimal Retained Duplicate Reference Replacement",
        )


def write_report(report: RetainedDuplicateReferenceReplacementReadinessReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37h_retained_duplicate_reference_replacement_readiness.json"
    txt_path = REPORT_DIR / "phase_37h_retained_duplicate_reference_replacement_readiness.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37H — Retained Duplicate Reference Replacement Readiness",
        "",
        f"schema={report.schema}",
        f"source_schema={report.source_schema}",
        f"retained_candidate_count={report.retained_candidate_count}",
        f"total_reference_count={report.total_reference_count}",
        f"auto_replace_allowed_count={report.auto_replace_allowed_count}",
        f"manual_review_required_count={report.manual_review_required_count}",
        f"text_only_reference_count={report.text_only_reference_count}",
        f"import_replacement_required_count={report.import_replacement_required_count}",
        f"deletion_performed={report.deletion_performed}",
        f"files_modified={report.files_modified}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Reference Classifications",
        "",
    ]

    for ref in report.references:
        lines.extend(
            [
                f"candidate_path={ref.candidate_path}",
                f"reference_path={ref.reference_path}",
                f"category={ref.category}",
                f"reference_kind={ref.reference_kind}",
                f"contains_python_import={ref.contains_python_import}",
                f"contains_runtime_usage={ref.contains_runtime_usage}",
                f"contains_text_only_reference={ref.contains_text_only_reference}",
                f"replacement_classification={ref.replacement_classification}",
                f"recommended_action={ref.recommended_action}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = RetainedDuplicateReferenceReplacementReadinessChecker().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"retained_candidate_count={report.retained_candidate_count}")
    print(f"total_reference_count={report.total_reference_count}")
    print(f"auto_replace_allowed_count={report.auto_replace_allowed_count}")
    print(f"manual_review_required_count={report.manual_review_required_count}")
    print(f"text_only_reference_count={report.text_only_reference_count}")
    print(f"import_replacement_required_count={report.import_replacement_required_count}")
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
