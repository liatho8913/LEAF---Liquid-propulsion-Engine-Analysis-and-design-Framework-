"""
Programme 27C: Standardisation Scanner.

Read-only project scanner for LEAF standardisation.

Design rules:
- Scan only.
- No mutation.
- No deletion.
- No archival.
- No automatic repair.
- Produce structured findings for later owner/report phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .rule_registry import (
    StandardisationRuleRegistry,
    build_default_standardisation_rule_registry,
)


class StandardisationFindingLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass(frozen=True)
class StandardisationFinding:
    finding_id: str
    level: StandardisationFindingLevel
    rule_id: str
    path: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "level": self.level.value,
            "rule_id": self.rule_id,
            "path": self.path,
            "message": self.message,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class StandardisationScanResult:
    schema: str
    root: str
    scanned_python_files: int
    scanned_report_files: int
    findings: Tuple[StandardisationFinding, ...]
    mutation_performed: bool = False

    def finding_counts(self) -> Dict[str, int]:
        counts = {level.value: 0 for level in StandardisationFindingLevel}
        for finding in self.findings:
            counts[finding.level.value] += 1
        return counts

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "root": self.root,
            "scanned_python_files": self.scanned_python_files,
            "scanned_report_files": self.scanned_report_files,
            "finding_counts": self.finding_counts(),
            "mutation_performed": self.mutation_performed,
            "findings": [finding.as_dict() for finding in self.findings],
        }


class StandardisationScanner:
    """
    Read-only standardisation scanner.

    This scanner intentionally starts with structural checks only. Later phases
    can expand rule-specific validation without creating new scanner systems.
    """

    EXCLUDED_PARTS = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".idea",
        "_leaf_repository_cleanup_candidates",
    }

    CANONICAL_FOLDERS = (
        "LEAF_Projects",
        "LEAF_Designs",
        "LEAF_Reports",
        "LEAF_Exports",
    )

    REQUIRED_PACKAGES = (
        "leaf_qt/workflow",
        "leaf_qt/standardisation",
    )

    def __init__(
        self,
        root: Path,
        registry: StandardisationRuleRegistry | None = None,
    ) -> None:
        self.root = Path(root)
        self.registry = registry or build_default_standardisation_rule_registry()

    def scan(self) -> StandardisationScanResult:
        findings: List[StandardisationFinding] = []

        python_files = tuple(self._iter_files(".py"))
        report_files = tuple(self._iter_report_files())

        findings.extend(self._scan_registry())
        findings.extend(self._scan_required_folders())
        findings.extend(self._scan_required_packages())
        findings.extend(self._scan_python_files(python_files))
        findings.extend(self._scan_report_files(report_files))

        return StandardisationScanResult(
            schema="LEAF_STANDARDISATION_SCANNER_PHASE_27C_V1",
            root=str(self.root),
            scanned_python_files=len(python_files),
            scanned_report_files=len(report_files),
            findings=tuple(findings),
            mutation_performed=False,
        )

    def _iter_files(self, suffix: str) -> Iterable[Path]:
        for path in self.root.rglob(f"*{suffix}"):
            rel = path.relative_to(self.root)
            if any(part in self.EXCLUDED_PARTS for part in rel.parts):
                continue
            yield path

    def _iter_report_files(self) -> Iterable[Path]:
        reports = self.root / "LEAF_Reports"
        if not reports.exists():
            return tuple()

        result: List[Path] = []
        for suffix in (".txt", ".json"):
            for path in reports.rglob(f"*{suffix}"):
                rel = path.relative_to(self.root)
                if any(part in self.EXCLUDED_PARTS for part in rel.parts):
                    continue
                result.append(path)
        return tuple(result)

    def _scan_registry(self) -> List[StandardisationFinding]:
        findings: List[StandardisationFinding] = []
        failures = self.registry.validate()

        for index, failure in enumerate(failures):
            findings.append(
                StandardisationFinding(
                    finding_id=f"registry_validation_{index}",
                    level=StandardisationFindingLevel.ERROR,
                    rule_id="standardisation_registry_valid",
                    path="leaf_qt/standardisation/rule_registry.py",
                    message=failure,
                )
            )

        return findings

    def _scan_required_folders(self) -> List[StandardisationFinding]:
        findings: List[StandardisationFinding] = []

        for folder in self.CANONICAL_FOLDERS:
            path = self.root / folder
            if not path.exists():
                findings.append(
                    StandardisationFinding(
                        finding_id=f"missing_canonical_folder_{folder}",
                        level=StandardisationFindingLevel.WARNING,
                        rule_id="canonical_user_storage_folders_only",
                        path=folder,
                        message=f"Canonical folder is missing: {folder}",
                    )
                )

        return findings

    def _scan_required_packages(self) -> List[StandardisationFinding]:
        findings: List[StandardisationFinding] = []

        for package in self.REQUIRED_PACKAGES:
            path = self.root / package
            init_path = path / "__init__.py"

            if not path.exists():
                findings.append(
                    StandardisationFinding(
                        finding_id=f"missing_required_package_{package.replace('/', '_')}",
                        level=StandardisationFindingLevel.ERROR,
                        rule_id="ownership_boundaries_are_explicit",
                        path=package,
                        message=f"Required platform package is missing: {package}",
                    )
                )
                continue

            if not init_path.exists():
                findings.append(
                    StandardisationFinding(
                        finding_id=f"missing_required_init_{package.replace('/', '_')}",
                        level=StandardisationFindingLevel.ERROR,
                        rule_id="modules_expose_standard_interfaces",
                        path=str(init_path.relative_to(self.root)),
                        message=f"Required package __init__.py missing: {package}",
                    )
                )

        return findings

    def _scan_python_files(self, python_files: Tuple[Path, ...]) -> List[StandardisationFinding]:
        findings: List[StandardisationFinding] = []

        for path in python_files:
            rel = str(path.relative_to(self.root))
            name = path.name

            if name.endswith("_gate.py") or "_gate_phase_" in name or "completion_gate" in name:
                text = path.read_text(encoding="utf-8", errors="replace")
                if "completion_notice" not in text:
                    findings.append(
                        StandardisationFinding(
                            finding_id=f"gate_missing_completion_notice_{len(findings)}",
                            level=StandardisationFindingLevel.ERROR,
                            rule_id="completion_gates_emit_completion_notice",
                            path=rel,
                            message="Gate-like Python file does not contain completion_notice.",
                        )
                    )

                if "json_path" not in text and ".json" not in text:
                    findings.append(
                        StandardisationFinding(
                            finding_id=f"gate_missing_json_report_{len(findings)}",
                            level=StandardisationFindingLevel.WARNING,
                            rule_id="completion_gates_emit_completion_notice",
                            path=rel,
                            message="Gate-like Python file may not emit a JSON report path.",
                        )
                    )

        return findings

    def _scan_report_files(self, report_files: Tuple[Path, ...]) -> List[StandardisationFinding]:
        findings: List[StandardisationFinding] = []

        for path in report_files:
            rel = str(path.relative_to(self.root))
            if path.suffix == ".json":
                text = path.read_text(encoding="utf-8", errors="replace")
                if '"schema"' not in text:
                    findings.append(
                        StandardisationFinding(
                            finding_id=f"json_report_missing_schema_{len(findings)}",
                            level=StandardisationFindingLevel.WARNING,
                            rule_id="schema_has_named_version",
                            path=rel,
                            message="JSON report does not expose a schema field.",
                        )
                    )

        return findings


def build_standardisation_scanner(
    root: Path,
    registry: StandardisationRuleRegistry | None = None,
) -> StandardisationScanner:
    return StandardisationScanner(root=root, registry=registry)
