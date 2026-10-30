from __future__ import annotations

from pathlib import Path
from typing import Any
import sys

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from project_maintenance.global_status_classification_engine_phase_16t3g import (
    STATUS_REVIEW_REQUIRED,
    STATUS_BLOCKED,
    STATUS_FAIL,
    make_finding,
    classify_status,
)


PHASE = "16T.3I"

PASS_STATUS = "PASS_LEGACY_WARN_ADAPTER_PHASE_16T3I"
REVIEW_STATUS = "REVIEW_REQUIRED_LEGACY_WARN_ADAPTER_PHASE_16T3I"
BLOCKED_STATUS = "BLOCKED_LEGACY_WARN_ADAPTER_PHASE_16T3I"
FAIL_STATUS = "FAIL_LEGACY_WARN_ADAPTER_PHASE_16T3I"

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"


BLOCKED_KEYWORDS = (
    "MISSING",
    "IMPORT_FAILED",
    "NO_DATA",
    "NO_PROFILE",
    "NO_PAYLOAD",
    "PLACEHOLDER",
    "NOT_VALID",
    "INCOMPLETE",
    "UNREGISTERED",
)

FAIL_KEYWORDS = (
    "FAIL",
    "ERROR",
    "EXCEPTION",
    "INVALID",
    "IMPOSSIBLE",
    "NEGATIVE",
    "CORRUPT",
)

REVIEW_KEYWORDS = (
    "WARN",
    "WARNING",
    "REVIEW",
    "WAITING",
    "RUNNING",
    "READY",
    "CANDIDATE",
    "MAX_GENERATIONS",
    "PLATEAU",
)


def infer_category_from_legacy_warning(warning: str) -> str:
    text = str(warning).upper()

    # Specific blocked cases must be checked before generic MISSING / WARN handling.
    if "PROFILE" in text:
        return "NO_STATION_PROFILE"

    if "IMPORT_FAILED" in text or "IMPORT" in text:
        return "BROKEN_IMPORT"

    if "REGISTRY" in text or "UNREGISTERED" in text:
        return "MISSING_REGISTRY"

    if "REPORT" in text:
        return "MISSING_REPORT"

    if "PLACEHOLDER" in text:
        return "PLACEHOLDER_USED_FOR_PASS"

    if "NO_STAGED_GEOMETRY" in text or ("NO" in text and "GEOMETRY" in text):
        return "NO_STAGED_GEOMETRY"

    if "PAYLOAD" in text or "NO_DATA" in text or "MISSING" in text or "INCOMPLETE" in text or "NOT_VALID" in text:
        return "MISSING_REQUIRED_DATA"

    # True engineering failures.
    if "NEGATIVE" in text:
        return "PHYSICS_INVALID"

    if "INVALID" in text:
        return "VALIDATION_FAILURE"

    if "ERROR" in text or "EXCEPTION" in text or "CORRUPT" in text or "IMPOSSIBLE" in text:
        return "UNHANDLED_EXCEPTION"

    # Review states.
    if "MAX_GENERATIONS" in text:
        return "MAX_GENERATIONS_REACHED"

    if "PLATEAU" in text:
        return "OPTIMISATION_PLATEAU"

    if "CANDIDATE" in text or "READY" in text:
        return "CANDIDATE_AVAILABLE"

    if "CLEANUP" in text or "ARCHIVE" in text:
        return "CLEANUP_DEBT"

    return "MANUAL_REVIEW_REQUIRED"


def adapt_legacy_warning(
    warning: str,
    *,
    owner: str,
    allowlisted: bool = False,
    category: str | None = None,
) -> dict[str, Any]:
    resolved_category = category or infer_category_from_legacy_warning(warning)

    return make_finding(
        message=str(warning),
        category=resolved_category,
        owner=owner,
        allowlisted=allowlisted,
    )


def adapt_legacy_status_payload(
    payload: dict[str, Any],
    *,
    owner: str,
    warning_key: str = "warnings",
    production_gate: bool = False,
    allowlisted_categories: set[str] | None = None,
) -> dict[str, Any]:
    allowlisted_categories = allowlisted_categories or set()

    warnings = payload.get(warning_key, [])
    if isinstance(warnings, str):
        warnings = [warnings]

    findings = []

    for warning in warnings:
        category = infer_category_from_legacy_warning(str(warning))
        findings.append(
            adapt_legacy_warning(
                str(warning),
                owner=owner,
                allowlisted=category in allowlisted_categories,
                category=category,
            )
        )

    status_result = classify_status(findings, production_gate=production_gate)

    adapted = dict(payload)
    adapted["structured_findings"] = findings
    adapted["global_status"] = status_result["status"]
    adapted["global_status_payload"] = status_result

    return adapted


def build_legacy_warn_adapter_report() -> str:
    examples = [
        "WARN_REGEN_CONVERGENCE_RUNNING",
        "WARN_REGEN_CONVERGENCE_MAX_GENERATIONS_REACHED",
        "WARN_REGEN_VIEWER_SIDE_PROFILE_PAYLOAD_EMPTY_PHASE_16R1",
        "WARN_IMPORT_FAILED_PHASE_16N6",
        "NEGATIVE_WALL_THICKNESS_WARNING",
    ]

    adapted = [
        adapt_legacy_warning(example, owner="Legacy Adapter Demo")
        for example in examples
    ]

    status_result = classify_status(adapted)

    lines = [
        "LEGACY WARN ADAPTER UTILITY",
        "===========================",
        f"Phase: {PHASE}",
        f"Status: {PASS_STATUS}",
        f"Passed: True",
        "",
        "PURPOSE",
        "-------",
        "Convert old WARN/WARNING strings into structured global-status findings without rewriting every legacy module at once.",
        "",
        "EXAMPLE ADAPTATION",
        "------------------",
    ]

    for finding in adapted:
        lines.append(
            f"- {finding['message']} -> category={finding['category']} | "
            f"severity={finding['severity']} | owner={finding['owner']}"
        )

    lines.extend([
        "",
        "COMBINED STATUS",
        "---------------",
        f"Status: {status_result['status']}",
        f"Summary: {status_result['summary']}",
        "",
        "SAFETY RULE",
        "-----------",
        "Legacy WARN strings may be preserved for compatibility, but final status should come from structured findings.",
    ])

    return "\n".join(lines)


def write_legacy_warn_adapter_report() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORT_DIR / "LEGACY_WARN_ADAPTER_PHASE_16T3I.txt"
    output.write_text(build_legacy_warn_adapter_report(), encoding="utf-8")
    return output


if __name__ == "__main__":
    report = write_legacy_warn_adapter_report()
    print(PASS_STATUS)
    print(report)
