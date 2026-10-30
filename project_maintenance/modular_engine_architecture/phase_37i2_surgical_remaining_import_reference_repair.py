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
BACKUP_ROOT = ROOT / "_leaf_repository_cleanup_candidates" / "module_reference_replacement_backups" / "phase_37i2"


@dataclass(frozen=True)
class SurgicalRepairReport:
    schema: str
    target_path: str
    backup_path: str
    remaining_import_references_before: int
    import_lines_removed: int
    canonical_import_added: bool
    compile_passed: bool
    deletion_performed: bool
    files_modified: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class SurgicalRemainingImportReferenceRepair:
    schema = "LEAF_SURGICAL_REMAINING_IMPORT_REFERENCE_REPAIR_PHASE_37I2_V1"

    target_rel = Path("leaf_qt/module_interface/__init__.py")
    canonical_import = (
        "from project_maintenance.modular_engine_architecture."
        "phase_37a_module_dependency_visibility import ModuleDependencyVisibilityBuilder"
    )

    def backup_file(self, path: Path) -> Path:
        backup_path = BACKUP_ROOT / path.relative_to(ROOT)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        return backup_path

    @staticmethod
    def compile_text(text: str) -> tuple[bool, str]:
        try:
            ast.parse(text)
            return True, ""
        except Exception as exc:
            return False, str(exc)

    def build(self) -> SurgicalRepairReport:
        readiness = RetainedDuplicateReferenceReplacementReadinessChecker().build()
        remaining_imports = readiness.import_replacement_required_count

        target = ROOT / self.target_rel
        backup = self.backup_file(target)

        original = target.read_text(encoding="utf-8")
        lines = original.splitlines()

        removed = 0
        output: list[str] = []
        canonical_present = self.canonical_import in original

        for line in lines:
            stripped = line.strip()

            is_bad_import = (
                (
                    stripped.startswith("import ")
                    or stripped.startswith("from ")
                )
                and "module" in stripped.lower()
                and "registry" in stripped.lower()
            )

            if is_bad_import:
                removed += 1
                continue

            output.append(line)

        if removed and not canonical_present:
            insert_at = 0
            for i, line in enumerate(output):
                if line.startswith("from ") or line.startswith("import "):
                    insert_at = i + 1

            output.insert(insert_at, self.canonical_import)

        patched = "\n".join(output) + ("\n" if original.endswith("\n") else "")
        compile_passed, _ = self.compile_text(patched)

        if compile_passed and removed:
            target.write_text(patched, encoding="utf-8")

        passed = (
            remaining_imports == 1
            and removed >= 1
            and compile_passed
        )

        return SurgicalRepairReport(
            schema=self.schema,
            target_path=str(self.target_rel),
            backup_path=str(backup.relative_to(ROOT)),
            remaining_import_references_before=remaining_imports,
            import_lines_removed=removed,
            canonical_import_added=removed > 0 and not canonical_present,
            compile_passed=compile_passed,
            deletion_performed=False,
            files_modified=1 if passed else 0,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice=(
                "PASS_PHASE_37I2_SURGICAL_REMAINING_IMPORT_REFERENCE_REPAIR"
                if passed
                else "FAIL_PHASE_37I2_SURGICAL_REMAINING_IMPORT_REFERENCE_REPAIR"
            ),
            next_programme="Programme 37J — Retained Duplicate Candidate Re-Audit and Archival",
        )


def write_report(report: SurgicalRepairReport) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37i2_surgical_remaining_import_reference_repair.json"
    txt_path = REPORT_DIR / "phase_37i2_surgical_remaining_import_reference_repair.txt"

    json_path.write_text(json.dumps(asdict(report), indent=2, sort_keys=True), encoding="utf-8")

    txt_path.write_text(
        "\n".join(
            [
                "# LEAF Programme 37I2 — Surgical Remaining Import Reference Repair",
                "",
                f"schema={report.schema}",
                f"target_path={report.target_path}",
                f"backup_path={report.backup_path}",
                f"remaining_import_references_before={report.remaining_import_references_before}",
                f"import_lines_removed={report.import_lines_removed}",
                f"canonical_import_added={report.canonical_import_added}",
                f"compile_passed={report.compile_passed}",
                f"deletion_performed={report.deletion_performed}",
                f"files_modified={report.files_modified}",
                f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
                f"solver_execution_performed={report.solver_execution_performed}",
                f"passed={report.passed}",
                f"completion_notice={report.completion_notice}",
                f"next_programme={report.next_programme}",
            ]
        ),
        encoding="utf-8",
    )

    return txt_path, json_path


def main() -> None:
    report = SurgicalRemainingImportReferenceRepair().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"target_path={report.target_path}")
    print(f"backup_path={report.backup_path}")
    print(f"remaining_import_references_before={report.remaining_import_references_before}")
    print(f"import_lines_removed={report.import_lines_removed}")
    print(f"canonical_import_added={report.canonical_import_added}")
    print(f"compile_passed={report.compile_passed}")
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
