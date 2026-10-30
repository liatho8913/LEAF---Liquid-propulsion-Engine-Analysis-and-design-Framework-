from __future__ import annotations
def status_severity(status: object) -> str:
    """Return canonical severity without importing status_presentation.

    This deliberately lives here to avoid a circular import:

        status_presentation -> structured_status_access
        structured_status_access -> status_presentation

    The public shared owner may re-export or reuse this behaviour, but this
    low-level access module must not import back upward.
    """
    text = str(status or "").strip().upper()

    if not text:
        return "UNKNOWN"

    if text.startswith("PASS"):
        return "PASS"

    if text.startswith("WARN") or text.startswith("WARNING"):
        return "WARN"

    if text.startswith("FAIL") or text.startswith("FAILED"):
        return "FAIL"

    if text.startswith("BLOCKED"):
        return "BLOCKED"

    if text.startswith("ERROR") or text.startswith("EXCEPTION"):
        return "ERROR"

    return "UNKNOWN"

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


PASS_LIKE = {"PASS", "PASSED", "OK", "VALID", "TRUE", "1", "AVAILABLE", "COMPLETE"}
WARN_LIKE = {"WARN", "WARNING", "REVIEW", "REVIEW_REQUIRED", "PARTIAL", "MARGINAL", "PLACEHOLDER"}
FAIL_LIKE = {"FAIL", "FAILED", "ERROR", "INVALID", "BLOCKED", "MISSING", "FALSE", "0"}

SEVERITY_ORDER = {
    "FAIL": 4,
    "BLOCKED": 4,
    "REVIEW_REQUIRED": 3,
    "WARN": 2,
    "INFO": 1,
    "UNKNOWN": 0,
}


@dataclass(frozen=True)
class StatusInterpretation:
    raw: Any
    canonical: str
    severity: str
    passed: bool
    warning: bool
    failed: bool
    blocked: bool
    source: str


def _normalise(value: Any) -> str:
    if value is True:
        return "PASS"
    if value is False or value is None:
        return "FAIL"
    return str(value).strip().upper()


def canonical_status(value: Any) -> str:
    text = _normalise(value)

    if text in {"INFO", "PASS"} or text in PASS_LIKE or status_severity(text) == "PASS":
        return "PASS"

    if text in {"FAIL", "BLOCKED"} or text in FAIL_LIKE or any(
        token in text for token in ("FAIL", "ERROR", "INVALID", "BLOCKED")
    ):
        return "FAIL"

    if text in {"WARN", "REVIEW_REQUIRED"} or text in WARN_LIKE or any(
        token in text for token in ("WARN", "REVIEW", "PARTIAL", "MARGINAL", "PLACEHOLDER")
    ):
        return "WARN"

    return "UNKNOWN"


def severity(value: Any) -> str:
    text = _normalise(value)

    if text in SEVERITY_ORDER and text != "UNKNOWN":
        return text

    canonical = canonical_status(value)
    if canonical == "PASS":
        return "INFO"
    if canonical == "WARN":
        return "WARN"
    if canonical == "FAIL":
        return "FAIL"
    return "REVIEW_REQUIRED"


def is_pass(value: Any) -> bool:
    return canonical_status(value) == "PASS"


def is_warn(value: Any) -> bool:
    return canonical_status(value) == "WARN"


def is_fail(value: Any) -> bool:
    return canonical_status(value) == "FAIL"


def should_block(value: Any) -> bool:
    return severity(value) in {"FAIL", "BLOCKED", "REVIEW_REQUIRED"}


def interpret_status(value: Any, *, source: str = "legacy") -> StatusInterpretation:
    canonical = canonical_status(value)
    sev = severity(value)
    return StatusInterpretation(
        raw=value,
        canonical=canonical,
        severity=sev,
        passed=canonical == "PASS",
        warning=canonical == "WARN",
        failed=canonical == "FAIL",
        blocked=sev in {"FAIL", "BLOCKED", "REVIEW_REQUIRED"},
        source=source,
    )


def highest_severity(values: Iterable[Any]) -> str:
    highest = "UNKNOWN"

    for value in values:
        current = severity(value)
        if SEVERITY_ORDER.get(current, 0) > SEVERITY_ORDER.get(highest, 0):
            highest = current

    return highest


def aggregate_status(values: Iterable[Any]) -> str:
    high = highest_severity(values)
    if high in {"FAIL", "BLOCKED"}:
        return "FAIL"
    if high in {"WARN", "REVIEW_REQUIRED"}:
        return "WARN"
    if high == "INFO":
        return "PASS"
    return "UNKNOWN"


def finding_severity(finding: Mapping[str, Any]) -> str:
    if "severity" in finding:
        return severity(finding.get("severity"))
    if "status" in finding:
        return severity(finding.get("status"))
    if "passed" in finding:
        return "INFO" if bool(finding.get("passed")) else "FAIL"
    return "REVIEW_REQUIRED"


def findings_highest_severity(findings: Iterable[Mapping[str, Any]]) -> str:
    return highest_severity(finding_severity(item) for item in findings)


def findings_pass(findings: Iterable[Mapping[str, Any]]) -> bool:
    return findings_highest_severity(findings) == "INFO"


def payload_status(payload: Mapping[str, Any]) -> str:
    if "canonical_status" in payload:
        return canonical_status(payload.get("canonical_status"))
    if "global_status" in payload:
        return canonical_status(payload.get("global_status"))
    if "status" in payload:
        return canonical_status(payload.get("status"))
    if "passed" in payload:
        return "PASS" if bool(payload.get("passed")) else "FAIL"
    if "findings" in payload and isinstance(payload.get("findings"), list):
        return aggregate_status(finding_severity(item) for item in payload.get("findings", []))
    return "UNKNOWN"
