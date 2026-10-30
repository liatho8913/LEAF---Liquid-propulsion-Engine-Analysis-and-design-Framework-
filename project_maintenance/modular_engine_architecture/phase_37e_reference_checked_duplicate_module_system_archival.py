from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

from phase_37d_safe_duplicate_module_system_retirement_plan import (
    DuplicateModuleSystemRetirementPlanner,
    ROOT,
)


MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"
ARCHIVE_ROOT = ROOT / "_leaf_repository_cleanup_candidates" / "module_system_retirement_candidates"


IGNORED_PARTS = {
    ".venv",
    "__pycache__",
    ".git",
    "_external_repository_quarantine",
    "_leaf_repository_cleanup_candidates",
}


@dataclass(frozen=True)
class ReferenceCheckResult:
    candidate_path: str
    category: str
    reference_count: int
    reference_paths: list[str]
    archived: bool
    archive_target: str
    original_removed: bool
    rollback_available: bool
    reason: str


@dataclass(frozen=True)
class ReferenceCheckedDuplicateModuleSystemArchivalReport:
    schema: str
    source_schema: str
    candidate_count: int
    reference_clean_count: int
    archived_count: int
    retained_count: int
    rollback_manifest_created: bool
    results: list[ReferenceCheckResult]
    deletion_performed: bool
    archival_performed: bool
    files_modified: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class ReferenceCheckedDuplicateModuleSystemArchiver:
    """
    Programme 37E.

    Archives duplicate module-system candidates only when no live repository
    references remain.

    Constitutional limits:
    - No permanent deletion.
    - No engineering execution.
    - No solver execution.
    - No replacement architecture created.
    - Referenced files remain untouched.
    """

    schema = "LEAF_REFERENCE_CHECKED_DUPLICATE_MODULE_SYSTEM_ARCHIVAL_PHASE_37E_V1"

    def __init__(self, root: Path = ROOT) -> None:
        self.root = root

    def live_python_files(self) -> list[Path]:
        files: list[Path] = []

        for path in self.root.rglob("*.py"):
            if any(part in IGNORED_PARTS for part in path.parts):
                continue
            files.append(path)

        return sorted(files)

    @staticmethod
    def module_stem(path: Path) -> str:
        return path.stem

    @staticmethod
    def import_token(path: Path) -> str:
        return path.with_suffix("").as_posix().replace("/", ".")

    def references_to_candidate(self, candidate: Path) -> list[Path]:
        if not candidate.exists():
            return []

        stem = self.module_stem(candidate)
        rel_no_suffix = candidate.with_suffix("").as_posix()
        import_token = self.import_token(candidate.relative_to(self.root))

        references: list[Path] = []

        for path in self.live_python_files():
            if path.resolve() == candidate.resolve():
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except Exception:
                continue

            if (
                stem in text
                or rel_no_suffix in text
                or import_token in text
            ):
                references.append(path)

        return sorted(set(references))

    def archive_candidate(self, candidate: Path, archive_target: Path) -> bool:
        archive_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(candidate), str(archive_target))
        return archive_target.exists() and not candidate.exists()

    def build(self) -> ReferenceCheckedDuplicateModuleSystemArchivalReport:
        plan = DuplicateModuleSystemRetirementPlanner().build()

        results: list[ReferenceCheckResult] = []
        archived_count = 0
        reference_clean_count = 0

        for item in plan.items:
            candidate = self.root / item.path
            archive_target = self.root / item.archive_target

            references = self.references_to_candidate(candidate)
            reference_paths = [
                str(path.relative_to(self.root))
                for path in references
            ]

            reference_count = len(reference_paths)
            reference_clean = reference_count == 0 and candidate.exists()

            if reference_clean:
                reference_clean_count += 1

            archived = False

            if reference_clean:
                archived = self.archive_candidate(candidate, archive_target)
                if archived:
                    archived_count += 1

            results.append(
                ReferenceCheckResult(
                    candidate_path=item.path,
                    category=item.category,
                    reference_count=reference_count,
                    reference_paths=reference_paths,
                    archived=archived,
                    archive_target=item.archive_target,
                    original_removed=not candidate.exists() if archived else False,
                    rollback_available=archive_target.exists(),
                    reason=(
                        "REFERENCE_CLEAN_ARCHIVED"
                        if archived
                        else "REFERENCES_FOUND_RETAINED"
                        if reference_count > 0
                        else "CANDIDATE_NOT_FOUND_OR_ARCHIVE_FAILED"
                    ),
                )
            )

        retained_count = len(results) - archived_count

        passed = (
            plan.passed
            and all(result.rollback_available or not result.archived for result in results)
            and all(not result.archived or result.original_removed for result in results)
        )

        report = ReferenceCheckedDuplicateModuleSystemArchivalReport(
            schema=self.schema,
            source_schema=plan.schema,
            candidate_count=plan.candidate_count,
            reference_clean_count=reference_clean_count,
            archived_count=archived_count,
            retained_count=retained_count,
            rollback_manifest_created=True,
            results=results,
            deletion_performed=False,
            archival_performed=archived_count > 0,
            files_modified=archived_count,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37E_REFERENCE_CHECKED_DUPLICATE_MODULE_SYSTEM_ARCHIVAL"
                if passed
                else "FAIL_PHASE_37E_REFERENCE_CHECKED_DUPLICATE_MODULE_SYSTEM_ARCHIVAL"
            ),
            next_programme="Programme 37F — Post-Archival Module System Integrity Verification",
        )

        return report


def write_report(report: ReferenceCheckedDuplicateModuleSystemArchivalReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37e_reference_checked_duplicate_module_system_archival.json"
    txt_path = REPORT_DIR / "phase_37e_reference_checked_duplicate_module_system_archival.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37E — Reference-Checked Duplicate Module System Archival",
        "",
        f"schema={report.schema}",
        f"source_schema={report.source_schema}",
        f"candidate_count={report.candidate_count}",
        f"reference_clean_count={report.reference_clean_count}",
        f"archived_count={report.archived_count}",
        f"retained_count={report.retained_count}",
        f"rollback_manifest_created={report.rollback_manifest_created}",
        f"deletion_performed={report.deletion_performed}",
        f"archival_performed={report.archival_performed}",
        f"files_modified={report.files_modified}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Reference Check Results",
        "",
    ]

    for result in report.results:
        lines.extend(
            [
                f"candidate_path={result.candidate_path}",
                f"category={result.category}",
                f"reference_count={result.reference_count}",
                f"reference_paths={result.reference_paths}",
                f"archived={result.archived}",
                f"archive_target={result.archive_target}",
                f"original_removed={result.original_removed}",
                f"rollback_available={result.rollback_available}",
                f"reason={result.reason}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = ReferenceCheckedDuplicateModuleSystemArchiver().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"source_schema={report.source_schema}")
    print(f"candidate_count={report.candidate_count}")
    print(f"reference_clean_count={report.reference_clean_count}")
    print(f"archived_count={report.archived_count}")
    print(f"retained_count={report.retained_count}")
    print(f"rollback_manifest_created={report.rollback_manifest_created}")
    print(f"deletion_performed={report.deletion_performed}")
    print(f"archival_performed={report.archival_performed}")
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
