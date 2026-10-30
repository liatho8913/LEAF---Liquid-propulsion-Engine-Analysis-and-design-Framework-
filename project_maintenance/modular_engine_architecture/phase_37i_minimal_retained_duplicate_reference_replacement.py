from __future__ import annotations

import ast
import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37h_retained_duplicate_reference_replacement_readiness import (
    RetainedDuplicateReferenceReplacementReadinessChecker,
    ROOT,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"
BACKUP_ROOT = ROOT / "_leaf_repository_cleanup_candidates" / "module_reference_replacement_backups" / "phase_37i"


CANONICAL_REPLACEMENT_IMPORTS = {
    "dependency": "from project_maintenance.modular_engine_architecture.phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder",
    "registry": "from project_maintenance.modular_engine_architecture.phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder",
    "availability": "from project_maintenance.modular_engine_architecture.phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder",
}


@dataclass(frozen=True)
class MinimalReferenceReplacementResult:
    candidate_path: str
    reference_path: str
    category: str
    backup_path: str
    import_reference_detected: bool
    patched: bool
    compile_passed: bool
    error: str
    action: str


@dataclass(frozen=True)
class MinimalRetainedDuplicateReferenceReplacementReport:
    schema: str
    source_schema: str
    eligible_import_reference_count: int
    patched_file_count: int
    skipped_reference_count: int
    compile_failure_count: int
    backup_count: int
    results: list[MinimalReferenceReplacementResult]
    deletion_performed: bool
    files_modified: int
    retained_candidate_deleted: bool
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class MinimalRetainedDuplicateReferenceReplacer:
    """
    Programme 37I.

    Patches only confirmed import references identified by 37H.

    Constitutional limits:
    - No deletion.
    - No solver execution.
    - No engineering behaviour changes.
    - No manual-review text replacement.
    - No report-history mutation.
    """

    schema = "LEAF_MINIMAL_RETAINED_DUPLICATE_REFERENCE_REPLACEMENT_PHASE_37I_V1"

    @staticmethod
    def candidate_stem(candidate_path: str) -> str:
        return Path(candidate_path).stem

    @staticmethod
    def candidate_module(candidate_path: str) -> str:
        return Path(candidate_path).with_suffix("").as_posix().replace("/", ".")

    def backup_file(self, path: Path) -> Path:
        rel = path.relative_to(ROOT)
        backup_path = BACKUP_ROOT / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        return backup_path

    def replace_imports(self, text: str, candidate_path: str, category: str) -> tuple[str, bool]:
        candidate_stem = self.candidate_stem(candidate_path)
        candidate_module = self.candidate_module(candidate_path)
        replacement_import = CANONICAL_REPLACEMENT_IMPORTS.get(
            category,
            "from project_maintenance.modular_engine_architecture.phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder",
        )

        lines = text.splitlines()
        changed = False
        output: list[str] = []

        for line in lines:
            stripped = line.strip()

            if stripped.startswith("import ") and (
                candidate_stem in stripped or candidate_module in stripped
            ):
                indent = line[: len(line) - len(line.lstrip())]
                output.append(indent + replacement_import)
                changed = True
                continue

            if stripped.startswith("from ") and (
                candidate_stem in stripped or candidate_module in stripped
            ):
                indent = line[: len(line) - len(line.lstrip())]
                output.append(indent + replacement_import)
                changed = True
                continue

            output.append(line)

        if not changed:
            return text, False

        return "\n".join(output) + ("\n" if text.endswith("\n") else ""), True

    @staticmethod
    def compile_file(path: Path) -> tuple[bool, str]:
        try:
            ast.parse(path.read_text(encoding="utf-8"))
            return True, ""
        except Exception as exc:
            return False, str(exc)

    def build(self) -> MinimalRetainedDuplicateReferenceReplacementReport:
        readiness = RetainedDuplicateReferenceReplacementReadinessChecker().build()

        eligible = [
            ref for ref in readiness.references
            if ref.replacement_classification == "IMPORT_REPLACEMENT_REQUIRED"
        ]

        results: list[MinimalReferenceReplacementResult] = []

        for ref in eligible:
            path = ROOT / ref.reference_path
            backup_path = Path("")

            try:
                original = path.read_text(encoding="utf-8")
                backup_path = self.backup_file(path)

                patched_text, patched = self.replace_imports(
                    original,
                    ref.candidate_path,
                    ref.category,
                )

                if patched:
                    path.write_text(patched_text, encoding="utf-8")

                compile_passed, error = self.compile_file(path)

                results.append(
                    MinimalReferenceReplacementResult(
                        candidate_path=ref.candidate_path,
                        reference_path=ref.reference_path,
                        category=ref.category,
                        backup_path=str(backup_path.relative_to(ROOT)),
                        import_reference_detected=True,
                        patched=patched,
                        compile_passed=compile_passed,
                        error=error,
                        action=(
                            "IMPORT_REFERENCE_PATCHED"
                            if patched and compile_passed
                            else "PATCHED_BUT_COMPILE_FAILED"
                            if patched
                            else "NO_IMPORT_LINE_PATCHED"
                        ),
                    )
                )

            except Exception as exc:
                results.append(
                    MinimalReferenceReplacementResult(
                        candidate_path=ref.candidate_path,
                        reference_path=ref.reference_path,
                        category=ref.category,
                        backup_path=str(backup_path.relative_to(ROOT)) if backup_path else "",
                        import_reference_detected=True,
                        patched=False,
                        compile_passed=False,
                        error=str(exc),
                        action="PATCH_FAILED",
                    )
                )

        patched_file_count = sum(1 for result in results if result.patched)
        compile_failure_count = sum(1 for result in results if not result.compile_passed)
        backup_count = sum(1 for result in results if result.backup_path)

        skipped_reference_count = readiness.total_reference_count - len(eligible)

        passed = (
            readiness.passed
            and len(eligible) == readiness.import_replacement_required_count
            and compile_failure_count == 0
            and patched_file_count == len(eligible)
            and backup_count == len(eligible)
        )

        return MinimalRetainedDuplicateReferenceReplacementReport(
            schema=self.schema,
            source_schema=readiness.schema,
            eligible_import_reference_count=len(eligible),
            patched_file_count=patched_file_count,
            skipped_reference_count=skipped_reference_count,
            compile_failure_count=compile_failure_count,
            backup_count=backup_count,
            results=results,
            deletion_performed=False,
            files_modified=patched_file_count,
            retained_candidate_deleted=False,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37I_MINIMAL_RETAINED_DUPLICATE_REFERENCE_REPLACEMENT"
                if passed
                else "FAIL_PHASE_37I_MINIMAL_RETAINED_DUPLICATE_REFERENCE_REPLACEMENT"
            ),
            next_programme="Programme 37J — Retained Duplicate Candidate Re-Audit and Archival",
        )


def write_report(report: MinimalRetainedDuplicateReferenceReplacementReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37i_minimal_retained_duplicate_reference_replacement.json"
    txt_path = REPORT_DIR / "phase_37i_minimal_retained_duplicate_reference_replacement.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37I — Minimal Retained Duplicate Reference Replacement",
        "",
        f"schema={report.schema}",
        f"source_schema={report.source_schema}",
        f"eligible_import_reference_count={report.eligible_import_reference_count}",
        f"patched_file_count={report.patched_file_count}",
        f"skipped_reference_count={report.skipped_reference_count}",
        f"compile_failure_count={report.compile_failure_count}",
        f"backup_count={report.backup_count}",
        f"deletion_performed={report.deletion_performed}",
        f"files_modified={report.files_modified}",
        f"retained_candidate_deleted={report.retained_candidate_deleted}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Replacement Results",
        "",
    ]

    for result in report.results:
        lines.extend(
            [
                f"candidate_path={result.candidate_path}",
                f"reference_path={result.reference_path}",
                f"category={result.category}",
                f"backup_path={result.backup_path}",
                f"import_reference_detected={result.import_reference_detected}",
                f"patched={result.patched}",
                f"compile_passed={result.compile_passed}",
                f"error={result.error}",
                f"action={result.action}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = MinimalRetainedDuplicateReferenceReplacer().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"eligible_import_reference_count={report.eligible_import_reference_count}")
    print(f"patched_file_count={report.patched_file_count}")
    print(f"skipped_reference_count={report.skipped_reference_count}")
    print(f"compile_failure_count={report.compile_failure_count}")
    print(f"backup_count={report.backup_count}")
    print(f"deletion_performed={report.deletion_performed}")
    print(f"files_modified={report.files_modified}")
    print(f"retained_candidate_deleted={report.retained_candidate_deleted}")
    print(f"engineering_behaviour_changed={report.engineering_behaviour_changed}")
    print(f"solver_execution_performed={report.solver_execution_performed}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_programme={report.next_programme}")

    if not report.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
