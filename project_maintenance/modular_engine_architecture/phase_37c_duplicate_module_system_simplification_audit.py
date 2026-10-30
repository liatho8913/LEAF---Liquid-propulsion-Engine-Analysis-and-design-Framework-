from __future__ import annotations

import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = ROOT / "project_maintenance" / "modular_engine_architecture"
REPORT_DIR = MODULE_ROOT / "reports"


CANONICAL_MODULE_SYSTEM_PATHS = {
    "project_maintenance/modular_engine_architecture",
    "leaf_qt/module_engine",
    "leaf_qt/modular_engine",
    "leaf_qt/modules",
    "leaf_qt/engineering_modules",
    "leaf_qt/module_runtime",
    "leaf_qt/module_interface",
}


@dataclass(frozen=True)
class DuplicateModuleSystemCandidate:
    path: str
    category: str
    reason: str
    line_count: int
    imports_canonical_module_engine: bool
    safe_to_remove_now: bool
    recommended_action: str


@dataclass(frozen=True)
class DuplicateModuleSystemSimplificationAudit:
    schema: str
    scanned_python_files: int
    candidate_count: int
    dependency_candidate_count: int
    registry_candidate_count: int
    availability_candidate_count: int
    safe_to_remove_now_count: int
    candidates: list[DuplicateModuleSystemCandidate]
    deletion_performed: bool
    files_modified: int
    engineering_behaviour_changed: bool
    solver_execution_performed: bool
    passed: bool
    completion_notice: str
    next_programme: str


class DuplicateModuleSystemSimplificationAuditor:
    """
    Programme 37C.

    Finds candidate duplicate module systems for later simplification.

    Constitutional limits:
    - Audit only.
    - No deletion.
    - No mutation.
    - No engineering execution.
    - No replacement architecture created.
    """

    schema = "LEAF_DUPLICATE_MODULE_SYSTEM_SIMPLIFICATION_AUDIT_PHASE_37C_V1"

    def __init__(self, root: Path = ROOT) -> None:
        self.root = root

    def is_package_facade(self, path: Path) -> bool:
        if path.name != "__init__.py":
            return False

        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            return False

        return (
            "__all__" in text
            and "from ." in text
            and "import (" in text
        )

    def is_canonical_path(self, path: Path) -> bool:
        rel = str(path.relative_to(self.root)).replace("\\", "/").lower()
        return (
            any(token in rel for token in CANONICAL_MODULE_SYSTEM_PATHS)
            or self.is_package_facade(path)
        )

    def python_files(self) -> list[Path]:
        ignored_parts = {
            ".venv",
            "__pycache__",
            ".git",
            "_external_repository_quarantine",
            "_leaf_repository_cleanup_candidates",
        }

        out: list[Path] = []

        for path in self.root.rglob("*.py"):
            if any(part in ignored_parts for part in path.parts):
                continue
            out.append(path)

        return sorted(out)

    @staticmethod
    def classify_path(path: Path) -> str | None:
        name = path.name.lower()

        if "module" not in name:
            return None

        if "dependency" in name:
            return "dependency"

        if "registry" in name:
            return "registry"

        if "availability" in name:
            return "availability"

        return None

    def imports_canonical_module_engine(self, path: Path) -> bool:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.name.lower()
                    if "modular_engine" in name or "module_engine" in name:
                        return True

            if isinstance(node, ast.ImportFrom):
                module = (node.module or "").lower()
                if "modular_engine" in module or "module_engine" in module:
                    return True

        return False

    @staticmethod
    def line_count(path: Path) -> int:
        try:
            return len(path.read_text(encoding="utf-8").splitlines())
        except Exception:
            return 0

    def build_candidate(self, path: Path, category: str) -> DuplicateModuleSystemCandidate:
        rel = str(path.relative_to(self.root))
        line_count = self.line_count(path)
        imports_canonical = self.imports_canonical_module_engine(path)

        reason = (
            f"Filename suggests module {category} ownership outside canonical Modular Engine paths."
        )

        safe_to_remove_now = False

        recommended_action = (
            "REVIEW_FOR_REPLACEMENT_BY_CANONICAL_MODULE_ENGINE"
            if not imports_canonical
            else "REVIEW_AS_ADAPTER_OR_COMPATIBILITY_LAYER"
        )

        return DuplicateModuleSystemCandidate(
            path=rel,
            category=category,
            reason=reason,
            line_count=line_count,
            imports_canonical_module_engine=imports_canonical,
            safe_to_remove_now=safe_to_remove_now,
            recommended_action=recommended_action,
        )

    def build(self) -> DuplicateModuleSystemSimplificationAudit:
        files = self.python_files()
        candidates: list[DuplicateModuleSystemCandidate] = []

        for path in files:
            if self.is_canonical_path(path):
                continue

            category = self.classify_path(path)

            if category is None:
                continue

            candidates.append(self.build_candidate(path, category))

        dependency_count = sum(1 for c in candidates if c.category == "dependency")
        registry_count = sum(1 for c in candidates if c.category == "registry")
        availability_count = sum(1 for c in candidates if c.category == "availability")
        safe_count = sum(1 for c in candidates if c.safe_to_remove_now)

        passed = True

        return DuplicateModuleSystemSimplificationAudit(
            schema=self.schema,
            scanned_python_files=len(files),
            candidate_count=len(candidates),
            dependency_candidate_count=dependency_count,
            registry_candidate_count=registry_count,
            availability_candidate_count=availability_count,
            safe_to_remove_now_count=safe_count,
            candidates=candidates,
            deletion_performed=False,
            files_modified=0,
            engineering_behaviour_changed=False,
            solver_execution_performed=False,
            passed=passed,
            completion_notice="PASS_PHASE_37C_DUPLICATE_MODULE_SYSTEM_SIMPLIFICATION_AUDIT",
            next_programme="Programme 37D — Safe Duplicate Module System Retirement Plan",
        )


def write_report(report: DuplicateModuleSystemSimplificationAudit) -> tuple[Path, Path]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = REPORT_DIR / "phase_37c_duplicate_module_system_simplification_audit.json"
    txt_path = REPORT_DIR / "phase_37c_duplicate_module_system_simplification_audit.txt"

    json_path.write_text(
        json.dumps(asdict(report), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    lines: list[str] = [
        "# LEAF Programme 37C — Duplicate Module System Simplification Audit",
        "",
        f"schema={report.schema}",
        f"scanned_python_files={report.scanned_python_files}",
        f"candidate_count={report.candidate_count}",
        f"dependency_candidate_count={report.dependency_candidate_count}",
        f"registry_candidate_count={report.registry_candidate_count}",
        f"availability_candidate_count={report.availability_candidate_count}",
        f"safe_to_remove_now_count={report.safe_to_remove_now_count}",
        f"deletion_performed={report.deletion_performed}",
        f"files_modified={report.files_modified}",
        f"engineering_behaviour_changed={report.engineering_behaviour_changed}",
        f"solver_execution_performed={report.solver_execution_performed}",
        f"passed={report.passed}",
        f"completion_notice={report.completion_notice}",
        f"next_programme={report.next_programme}",
        "",
        "## Candidates",
        "",
    ]

    for candidate in report.candidates:
        lines.extend(
            [
                f"path={candidate.path}",
                f"category={candidate.category}",
                f"reason={candidate.reason}",
                f"line_count={candidate.line_count}",
                f"imports_canonical_module_engine={candidate.imports_canonical_module_engine}",
                f"safe_to_remove_now={candidate.safe_to_remove_now}",
                f"recommended_action={candidate.recommended_action}",
                "",
            ]
        )

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    return txt_path, json_path


def main() -> None:
    report = DuplicateModuleSystemSimplificationAuditor().build()
    txt_path, json_path = write_report(report)

    print(report.completion_notice)
    print(f"scanned_python_files={report.scanned_python_files}")
    print(f"candidate_count={report.candidate_count}")
    print(f"dependency_candidate_count={report.dependency_candidate_count}")
    print(f"registry_candidate_count={report.registry_candidate_count}")
    print(f"availability_candidate_count={report.availability_candidate_count}")
    print(f"safe_to_remove_now_count={report.safe_to_remove_now_count}")
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
