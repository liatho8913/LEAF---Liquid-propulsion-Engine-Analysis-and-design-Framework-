from __future__ import annotations

from typing import Any

from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


FINAL_SIGNOFF_REQUIRED_STATUSES = {
    "foundation_attachment_pipeline_status": "PASS",
    "foundation_result_key_audit_status": "PASS",
    "foundation_save_load_verification_status": "PASS_FOUNDATION_SAVE_LOAD_VERIFICATION",
    "foundation_ui_launch_verification_status": "PASS_FOUNDATION_UI_LAUNCH_VERIFICATION",
}

OWNER = "Foundation Final Sign-Off Controller"


def _foundation_signoff_findings(
    *,
    blocking: list[str],
    warnings: list[str],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    for reason in blocking:
        findings.append(
            make_finding(
                message=reason,
                category="VALIDATION_FAILURE",
                owner=OWNER,
            )
        )

    for reason in warnings:
        findings.append(
            make_finding(
                message=reason,
                category="MANUAL_REVIEW_REQUIRED",
                owner=OWNER,
            )
        )

    if not findings:
        findings.append(
            make_finding(
                message="Foundation final sign-off complete.",
                category="COMPLETE",
                owner=OWNER,
            )
        )

    return findings


def evaluate_foundation_final_signoff(results):
    if not isinstance(results, dict):
        findings = [
            make_finding(
                message="Foundation final sign-off requires a result dictionary.",
                category="VALIDATION_FAILURE",
                owner=OWNER,
            )
        ]
        global_status_payload = classify_status(findings, production_gate=True)

        return {
            "foundation_final_signoff_status": "FAIL_INVALID_RESULTS",
            "foundation_final_signoff_complete": False,
            "foundation_final_signoff_blocking_reasons": [
                "Foundation final sign-off requires a result dictionary."
            ],
            "foundation_final_signoff_warning_reasons": [],
            "foundation_final_signoff_structured_findings": findings,
            "foundation_final_signoff_global_status": global_status_payload["status"],
            "foundation_final_signoff_global_status_payload": global_status_payload,
            "foundation_final_signoff_text": (
                "Foundation final sign-off requires a result dictionary."
            ),
        }

    blocking = []
    warnings = []

    for key, expected in FINAL_SIGNOFF_REQUIRED_STATUSES.items():
        actual = results.get(key)

        if actual != expected:
            blocking.append(
                f"{key} expected {expected}, got {actual}"
            )

    verification_status = results.get("foundation_verification_status")

    if verification_status not in {
        None,
        "PASS_FOUNDATION_VERIFICATION",
    }:
        blocking.append(
            f"foundation_verification_status is not passing: {verification_status}"
        )

    passed_count = int(results.get("foundation_verification_passed_count", 0) or 0)
    failed_count = int(results.get("foundation_verification_failed_count", 0) or 0)

    if failed_count != 0:
        blocking.append(
            f"foundation_verification_failed_count must be 0, got {failed_count}"
        )

    if passed_count <= 0:
        warnings.append(
            "foundation_verification_passed_count is zero or missing."
        )

    findings = _foundation_signoff_findings(
        blocking=blocking,
        warnings=warnings,
    )
    global_status_payload = classify_status(findings, production_gate=True)

    if blocking:
        status = "FAIL_FOUNDATION_FINAL_SIGNOFF"
        complete = False
    elif warnings:
        status = "WARN_FOUNDATION_FINAL_SIGNOFF_REVIEW"
        complete = False
    else:
        status = "PASS_FOUNDATION_FINAL_SIGNOFF"
        complete = True

    return {
        "foundation_final_signoff_status": status,
        "foundation_final_signoff_complete": complete,
        "foundation_final_signoff_blocking_reasons": blocking,
        "foundation_final_signoff_warning_reasons": warnings,
        "foundation_final_signoff_structured_findings": findings,
        "foundation_final_signoff_global_status": global_status_payload["status"],
        "foundation_final_signoff_global_status_payload": global_status_payload,
        "foundation_final_signoff_text": build_foundation_final_signoff_report(
            status=status,
            complete=complete,
            blocking=blocking,
            warnings=warnings,
            results=results,
            global_status_payload=global_status_payload,
        ),
    }


def build_foundation_final_signoff_report(
    status,
    complete,
    blocking,
    warnings,
    results,
    global_status_payload=None,
):
    lines = [
        "LEAF FINAL FOUNDATION SIGN-OFF",
        "==============================",
        "",
        f"Status: {status}",
        f"Foundation sign-off complete: {complete}",
        "",
        "Required Statuses:",
    ]

    for key, expected in FINAL_SIGNOFF_REQUIRED_STATUSES.items():
        lines.append(f"- {key}: {results.get(key)} | expected: {expected}")

    lines.extend([
        "",
        "Verification Harness:",
        f"- foundation_verification_status: {results.get('foundation_verification_status')}",
        f"- foundation_verification_passed_count: {results.get('foundation_verification_passed_count')}",
        f"- foundation_verification_failed_count: {results.get('foundation_verification_failed_count')}",
        "",
        "Blocking Reasons:",
    ])

    lines.extend([f"- {item}" for item in blocking] or ["- None."])

    lines.append("")
    lines.append("Warnings:")
    lines.extend([f"- {item}" for item in warnings] or ["- None."])

    if global_status_payload is not None:
        lines.extend([
            "",
            "Global Status Engine:",
            f"- canonical_status: {global_status_payload.get('status')}",
            f"- finding_count: {global_status_payload.get('finding_count')}",
            f"- blocked: {global_status_payload.get('blocked')}",
            f"- failed: {global_status_payload.get('failed')}",
        ])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Final foundation sign-off only passes when all foundation verification systems pass.")
    lines.append("- This is the last gate before returning to regen geometry completion.")
    lines.append("- A failed sign-off means foundations are not yet complete.")
    lines.append("- Structured findings now control canonical global status classification.")

    return "\n".join(lines)
