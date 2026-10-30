from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Mapping


@dataclass(frozen=True)
class ArchitectureFinding:
    status: str
    code: str
    message: str
    path: str | None = None
    evidence: Mapping[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status.upper() in {"PASS", "OK", "SUCCESS"}


@dataclass(frozen=True)
class ArchitectureReport:
    schema: str
    title: str
    summary: Mapping[str, Any]
    findings: list[ArchitectureFinding] = field(default_factory=list)
    payload: Mapping[str, Any] = field(default_factory=dict)
    safe_to_modify_files: bool = False

    @property
    def passed(self) -> bool:
        return all(finding.passed for finding in self.findings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "title": self.title,
            "summary": dict(self.summary),
            "findings": [asdict(finding) for finding in self.findings],
            "payload": dict(self.payload),
            "safe_to_modify_files": self.safe_to_modify_files,
            "passed": self.passed,
        }
