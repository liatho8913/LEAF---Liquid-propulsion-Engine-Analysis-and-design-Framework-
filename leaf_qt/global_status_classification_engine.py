from __future__ import annotations

from typing import Any


STATUS_NOT_STARTED = "NOT_STARTED"
STATUS_RUNNING = "RUNNING"
STATUS_PASS = "PASS"
STATUS_REVIEW_REQUIRED = "REVIEW_REQUIRED"
STATUS_BLOCKED = "BLOCKED"
STATUS_FAIL = "FAIL"

CANONICAL_STATUSES = {
    STATUS_NOT_STARTED,
    STATUS_RUNNING,
    STATUS_PASS,
    STATUS_REVIEW_REQUIRED,
    STATUS_BLOCKED,
    STATUS_FAIL,
}

FINDING_INFO = "INFO"
FINDING_REVIEW = "REVIEW_REQUIRED"
FINDING_BLOCKED = "BLOCKED"
FINDING_FAIL = "FAIL"

FINDING_SEVERITIES = {
    FINDING_INFO,
    FINDING_REVIEW,
    FINDING_BLOCKED,
    FINDING_FAIL,
}

REVIEW_CATEGORIES = {
    "CLEANUP_DEBT",
    "ARCHIVE_ELIGIBLE",
    "MANUAL_REVIEW_REQUIRED",
    "OPTIMISATION_CONVERGED",
    "OPTIMISATION_PLATEAU",
    "MAX_GENERATIONS_REACHED",
    "CANDIDATE_AVAILABLE",
    "OPTIONAL_EXPORT_MISSING",
    "NONBLOCKING_DOCUMENTATION_REFERENCE",
}

BLOCKED_CATEGORIES = {
    "MISSING_REQUIRED_DATA",
    "MISSING_SOURCE_FILE",
    "MISSING_REGISTRY",
    "MISSING_REPORT",
    "BROKEN_IMPORT",
    "PLACEHOLDER_USED_FOR_PASS",
    "VALIDATION_INCOMPLETE",
    "SOLVER_PREREQUISITE_MISSING",
    "NO_STAGED_GEOMETRY",
    "NO_STATION_PROFILE",
}

FAIL_CATEGORIES = {
    "PHYSICS_INVALID",
    "SOLVER_FAILURE",
    "VALIDATION_FAILURE",
    "IMPOSSIBLE_GEOMETRY",
    "NEGATIVE_PRESSURE",
    "NEGATIVE_WALL_THICKNESS",
    "CEA_FAILURE",
    "CORRUPT_PAYLOAD",
    "UNHANDLED_EXCEPTION",
}

INFO_CATEGORIES = {
    "OK",
    "COMPLETE",
    "RUN_RECORD_CREATED",
    "EXPORT_CREATED",
    "REPORT_CREATED",
}


def make_finding(
    message: str,
    category: str,
    owner: str,
    evidence: Any | None = None,
    severity: str | None = None,
    allowlisted: bool = False,
) -> dict[str, Any]:
    return {
        "message": message,
        "category": category,
        "owner": owner,
        "severity": severity or infer_finding_severity(category),
        "allowlisted": allowlisted,
        "evidence": evidence,
    }


def infer_finding_severity(category: str) -> str:
    if category in FAIL_CATEGORIES:
        return FINDING_FAIL
    if category in BLOCKED_CATEGORIES:
        return FINDING_BLOCKED
    if category in REVIEW_CATEGORIES:
        return FINDING_REVIEW
    if category in INFO_CATEGORIES:
        return FINDING_INFO
    return FINDING_BLOCKED


def classify_status(
    findings: list[dict[str, Any]],
    *,
    lifecycle: str | None = None,
    production_gate: bool = False,
) -> dict[str, Any]:
    blockers = []
    normalised = []

    for finding in findings:
        message = str(finding.get("message", ""))
        category = str(finding.get("category", "UNKNOWN_CATEGORY"))
        owner = str(finding.get("owner", "") or "UNOWNED")
        severity = str(finding.get("severity") or infer_finding_severity(category))
        allowlisted = bool(finding.get("allowlisted", False))

        if owner == "UNOWNED":
            severity = FINDING_BLOCKED
            blockers.append(f"Unowned finding: {message}")

        if category == "UNKNOWN_CATEGORY":
            severity = FINDING_BLOCKED
            blockers.append(f"Unknown finding category: {message}")

        if production_gate and severity == FINDING_REVIEW and not allowlisted:
            severity = FINDING_BLOCKED
            blockers.append(f"Unallowlisted review finding in production gate: {message}")

        normalised.append(
            {
                "message": message,
                "category": category,
                "owner": owner,
                "severity": severity,
                "allowlisted": allowlisted,
                "evidence": finding.get("evidence"),
            }
        )

    severities = {finding["severity"] for finding in normalised}

    if lifecycle == STATUS_NOT_STARTED:
        status = STATUS_NOT_STARTED
    elif lifecycle == STATUS_RUNNING:
        status = STATUS_RUNNING
    elif FINDING_FAIL in severities:
        status = STATUS_FAIL
    elif FINDING_BLOCKED in severities or blockers:
        status = STATUS_BLOCKED
    elif FINDING_REVIEW in severities:
        status = STATUS_REVIEW_REQUIRED
    else:
        status = STATUS_PASS

    return {
        "status": status,
        "passed": status == STATUS_PASS,
        "can_continue": status in {STATUS_PASS, STATUS_REVIEW_REQUIRED, STATUS_RUNNING},
        "requires_human_review": status == STATUS_REVIEW_REQUIRED,
        "blocked": status == STATUS_BLOCKED,
        "failed": status == STATUS_FAIL,
        "finding_count": len(normalised),
        "findings": normalised,
        "blockers": blockers,
        "summary": f"{len(normalised)} findings classified; final status={status}.",
    }


def legacy_warn_to_finding(
    warning: str,
    *,
    owner: str,
    category: str = "MANUAL_REVIEW_REQUIRED",
    allowlisted: bool = False,
) -> dict[str, Any]:
    return make_finding(
        message=warning,
        category=category,
        owner=owner,
        allowlisted=allowlisted,
    )
