from __future__ import annotations

from pathlib import Path
from typing import Any


PHASE = "16T.3E"

PASS_STATUS = "PASS_WARNING_ESCALATION_POLICY_PHASE_16T3E"
WARN_STATUS = "WARN_WARNING_ESCALATION_POLICY_PHASE_16T3E"
FAIL_STATUS = "FAIL_WARNING_ESCALATION_POLICY_PHASE_16T3E"

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "_leaf_artifacts" / "reports"

BLOCKING_CATEGORIES = {
    "MISSING_REQUIRED_DATA",
    "MISSING_SOURCE_FILE",
    "PHYSICS_INVALID",
    "SOLVER_FAILURE",
    "VALIDATION_FAILURE",
    "PRODUCTION_GATE_WARNING",
    "UNOWNED_WARNING",
    "UNKNOWN_WARNING_CATEGORY",
    "PLACEHOLDER_USED_FOR_PASS",
    "BROKEN_IMPORT",
    "MISSING_REPORT",
    "MISSING_REGISTRY",
}

NONBLOCKING_CATEGORIES = {
    "CLEANUP_DEBT",
    "ARCHIVE_ELIGIBLE",
    "DUPLICATE_REPORT_REFERENCE",
    "MANUAL_REVIEW_REQUIRED",
    "OPTIONAL_EXPORT_MISSING",
    "NONBLOCKING_DOCUMENTATION_REFERENCE",
}


def classify_warning(
    message: str,
    category: str | None = None,
    owner: str | None = None,
    production_gate: bool = False,
    allowlisted: bool = False,
) -> dict[str, Any]:
    cat = category or "UNKNOWN_WARNING_CATEGORY"

    blockers = []
    allowed = False

    if not owner:
        blockers.append("Warning has no owner.")

    if cat in BLOCKING_CATEGORIES:
        blockers.append(f"Warning category is blocking: {cat}")

    if cat not in BLOCKING_CATEGORIES and cat not in NONBLOCKING_CATEGORIES:
        blockers.append(f"Warning category is unknown: {cat}")

    if production_gate and not allowlisted:
        blockers.append("Production gate warning is not allowlisted.")

    if not blockers:
        allowed = True

    return {
        "message": message,
        "category": cat,
        "owner": owner or "UNOWNED",
        "production_gate": production_gate,
        "allowlisted": allowlisted,
        "allowed_as_warning": allowed,
        "escalates_to_fail": bool(blockers),
        "blockers": blockers,
    }


def evaluate_warning_policy(
    warnings: list[dict[str, Any]],
    production_gate: bool = False,
) -> dict[str, Any]:
    evaluated = []

    for warning in warnings:
        evaluated.append(
            classify_warning(
                message=str(warning.get("message", "")),
                category=warning.get("category"),
                owner=warning.get("owner"),
                production_gate=bool(warning.get("production_gate", production_gate)),
                allowlisted=bool(warning.get("allowlisted", False)),
            )
        )

    escalated = [item for item in evaluated if item["escalates_to_fail"]]
    allowed = [item for item in evaluated if item["allowed_as_warning"]]

    if escalated:
        status = FAIL_STATUS
    elif allowed:
        status = WARN_STATUS
    else:
        status = PASS_STATUS

    return {
        "phase": PHASE,
        "status": status,
        "passed": not escalated,
        "warning_count": len(evaluated),
        "allowed_warning_count": len(allowed),
        "escalated_warning_count": len(escalated),
        "evaluated": evaluated,
        "blockers": [
            f"{item['message']} :: {'; '.join(item['blockers'])}"
            for item in escalated
        ],
        "warnings": [
            f"{item['message']} :: category={item['category']} owner={item['owner']}"
            for item in allowed
        ],
        "summary": f"{len(evaluated)} warnings evaluated; {len(escalated)} escalated to FAIL.",
    }


def build_warning_policy_report() -> str:
    examples = [
        {
            "message": "24 archive-eligible development checks found.",
            "category": "ARCHIVE_ELIGIBLE",
            "owner": "Verification Registry",
            "allowlisted": True,
        },
        {
            "message": "Missing required solver pressure field.",
            "category": "MISSING_REQUIRED_DATA",
            "owner": "Solver Owner",
        },
        {
            "message": "Unclassified warning example.",
        },
    ]

    audit = evaluate_warning_policy(examples)

    lines = [
        "GLOBAL WARNING ESCALATION POLICY",
        "================================",
        f"Phase: {PHASE}",
        f"Status: {audit['status']}",
        f"Passed: {audit['passed']}",
        f"Summary: {audit['summary']}",
        "",
        "POLICY",
        "------",
        "WARN is only allowed when the issue is non-blocking, categorised, owned, and either acceptable outside production gates or explicitly allowlisted.",
        "Production/sign-off gates must escalate unresolved or unallowlisted warnings to FAIL.",
        "",
        "BLOCKING CATEGORIES",
        "-------------------",
    ]

    for category in sorted(BLOCKING_CATEGORIES):
        lines.append(f"- {category}")

    lines.extend(["", "NONBLOCKING CATEGORIES", "----------------------"])

    for category in sorted(NONBLOCKING_CATEGORIES):
        lines.append(f"- {category}")

    lines.extend(["", "EXAMPLE EVALUATION", "------------------"])

    for item in audit["evaluated"]:
        lines.append(
            f"- {item['message']} | category={item['category']} | "
            f"owner={item['owner']} | warning_allowed={item['allowed_as_warning']} | "
            f"fail={item['escalates_to_fail']}"
        )

    lines.extend([
        "",
        "SAFETY RULE",
        "-----------",
        "Warnings are not treated as success unless they are owned, categorised, non-blocking, and permitted by the active gate policy.",
    ])

    return "\n".join(lines)


def write_warning_policy_report() -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output = REPORT_DIR / "WARNING_ESCALATION_POLICY_PHASE_16T3E.txt"
    output.write_text(build_warning_policy_report(), encoding="utf-8")
    return output


if __name__ == "__main__":
    report = write_warning_policy_report()
    demo_audit = evaluate_warning_policy([
        {
            "message": "24 archive-eligible development checks found.",
            "category": "ARCHIVE_ELIGIBLE",
            "owner": "Verification Registry",
            "allowlisted": True,
        },
        {
            "message": "Missing required solver pressure field.",
            "category": "MISSING_REQUIRED_DATA",
            "owner": "Solver Owner",
        },
        {
            "message": "Unclassified warning example.",
        },
    ])
    print(demo_audit["status"])
    print(report)
