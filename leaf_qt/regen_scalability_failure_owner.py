
try:
    from leaf_qt.status_presentation import LegacyCompatibilityProducer, status_severity
except Exception:
    from leaf_qt.status_presentation import status_severity


def _leaf_16u42_status_severity(value):
    try:
        return status_severity(value)
    except Exception:
        text = str(value or "").upper()
        if _leaf_16u42_is_fail_like(text) or _leaf_16u42_is_fail_like(text) or "INVALID" in text or "ERROR" in text or "MISSING" in text:
            return "FAIL"
        if _leaf_16u42_is_warn_like(text) or "PARTIAL" in text or "MARGINAL" in text:
            return "WARN"
        if _leaf_16u42_is_pass_like(text) or "VALID" in text or "COMPLETE" in text:
            return "PASS"
        return "UNKNOWN"


def _leaf_16u42_is_fail_like(value):
    return _leaf_16u42_status_severity(value) == "FAIL"


def _leaf_16u42_is_warn_like(value):
    return _leaf_16u42_status_severity(value) == "WARN"


def _leaf_16u42_is_pass_like(value):
    return _leaf_16u42_status_severity(value) == "PASS"

"""



LEAF Regen Scalability Failure / Validation Owner
=================================================

Stage V.3 owner for scalability failure classification and validation readiness.

This module does not classify engine scale.
This module does not perform raw constraint checks.
This module does not own the readable report.
This module does not approve final scalability.

Ownership:
- Stage V.0 profile owner classifies scale.
- Stage V.1 constraint owner owns pass/fail constraint logic.
- Stage V.2 report owner owns the readable report.
- Stage V.3 failure/validation owner classifies failure reasons and trust level.
- Stage V.4 master gate approves or blocks Stage V.
"""


def attach_regen_scalability_failure_owner(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_regen_scalability_failure_owner(results)
    results.update(audit)
    return results


def evaluate_regen_scalability_failure_owner(results):
    results = results if isinstance(results, dict) else {}

    profile_complete = bool(
        results.get("stage_v0_regen_scalability_profile_complete", False)
    )

    constraint_complete = bool(
        results.get("stage_v1_regen_scalability_constraint_owner_complete")
        or results.get("stage_v1_regen_scalability_framework_complete")
        or False
    )

    report_complete = bool(
        results.get("stage_v2_regen_scalability_report_owner_complete")
        or results.get("stage_v2_regen_scalability_report_ownership_complete")
        or False
    )

    constraint_status = str(
        results.get("regen_scalability_constraint_owner_status")
        or results.get("regen_scalability_framework_status")
        or "UNKNOWN"
    ).upper()

    report_status = str(
        results.get("regen_scalability_report_owner_status", "UNKNOWN")
    ).upper()

    blocking_reasons = _as_list(
        results.get("regen_scalability_constraint_owner_blocking_reasons")
        or results.get("regen_scalability_blocking_reasons")
    )

    warning_reasons = _as_list(
        results.get("regen_scalability_constraint_owner_warning_reasons")
        or results.get("regen_scalability_warning_reasons")
    )

    missing_inputs = _as_list(
        results.get("regen_scalability_constraint_owner_missing_inputs")
    )

    evidence = _as_list(
        results.get("regen_scalability_constraint_owner_evidence")
    )

    report_owner_blocking = _as_list(
        results.get("regen_scalability_report_owner_blocking_reasons")
    )

    failure_categories = classify_scalability_failure_categories(
        profile_complete=profile_complete,
        constraint_complete=constraint_complete,
        report_complete=report_complete,
        constraint_status=constraint_status,
        report_status=report_status,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        missing_inputs=missing_inputs,
        report_owner_blocking=report_owner_blocking,
    )

    trust_level = determine_scalability_trust_level(
        failure_categories=failure_categories,
        constraint_complete=constraint_complete,
        report_complete=report_complete,
        warning_reasons=warning_reasons,
        blocking_reasons=blocking_reasons,
    )

    can_proceed_to_master_gate = (
        trust_level == "TRUSTED_SCALABILITY_READY"
    )

    if can_proceed_to_master_gate:
        status = "PASS_REGEN_SCALABILITY_FAILURE_OWNER"
        complete = True
    elif blocking_reasons or report_owner_blocking or not profile_complete:
        status = "FAIL_REGEN_SCALABILITY_FAILURE_OWNER"
        complete = False
    else:
        status = "WARN_REGEN_SCALABILITY_FAILURE_OWNER_REVIEW_REQUIRED"
        complete = False

    text = build_regen_scalability_failure_owner_text(
        status=status,
        complete=complete,
        trust_level=trust_level,
        can_proceed_to_master_gate=can_proceed_to_master_gate,
        profile_complete=profile_complete,
        constraint_complete=constraint_complete,
        report_complete=report_complete,
        constraint_status=constraint_status,
        report_status=report_status,
        failure_categories=failure_categories,
        blocking_reasons=blocking_reasons,
        warning_reasons=warning_reasons,
        missing_inputs=missing_inputs,
        evidence=evidence,
        report_owner_blocking=report_owner_blocking,
    )

    return {
        "regen_scalability_failure_owner_status": status,
        "regen_scalability_failure_owner_complete": complete,
        "regen_scalability_failure_owner_trust_level": trust_level,
        "regen_scalability_failure_owner_can_proceed_to_master_gate": can_proceed_to_master_gate,
        "regen_scalability_failure_owner_failure_categories": failure_categories,
        "regen_scalability_failure_owner_blocking_reasons": blocking_reasons,
        "regen_scalability_failure_owner_warning_reasons": warning_reasons,
        "regen_scalability_failure_owner_missing_inputs": missing_inputs,
        "regen_scalability_failure_owner_evidence": evidence,
        "regen_scalability_failure_owner_text": text,
        "stage_v3_regen_scalability_failure_owner_complete": complete,
    }


def classify_scalability_failure_categories(
    profile_complete,
    constraint_complete,
    report_complete,
    constraint_status,
    report_status,
    blocking_reasons,
    warning_reasons,
    missing_inputs,
    report_owner_blocking,
):
    categories = []

    if not profile_complete:
        categories.append("PROFILE_METADATA_MISSING")

    if constraint_status in {"UNKNOWN", "", "NONE", "N/A"}:
        categories.append("CONSTRAINT_OWNER_MISSING")

    if not constraint_complete:
        if blocking_reasons:
            categories.append("SCALABILITY_BLOCKED")
        elif warning_reasons:
            categories.append("SCALABILITY_REVIEW_REQUIRED")
        else:
            categories.append("CONSTRAINT_OWNER_INCOMPLETE")

    if not report_complete:
        categories.append("REPORT_OWNER_INCOMPLETE")

    if report_owner_blocking:
        categories.append("REPORT_OWNERSHIP_BLOCKED")

    if missing_inputs:
        categories.append("SCALABILITY_INPUT_VISIBILITY_INCOMPLETE")

    if _leaf_16u42_is_fail_like(constraint_status) or _leaf_16u42_is_fail_like(constraint_status):
        categories.append("CONSTRAINT_STATUS_FAIL")

    if _leaf_16u42_is_warn_like(constraint_status):
        categories.append("CONSTRAINT_STATUS_WARN")

    if _leaf_16u42_is_fail_like(report_status) or _leaf_16u42_is_fail_like(report_status):
        categories.append("REPORT_STATUS_FAIL")

    if not categories:
        categories.append("NO_FAILURE_DETECTED")

    return _dedupe(categories)


def determine_scalability_trust_level(
    failure_categories,
    constraint_complete,
    report_complete,
    warning_reasons,
    blocking_reasons,
):
    categories = set(failure_categories)

    hard_fail_categories = {
        "PROFILE_METADATA_MISSING",
        "CONSTRAINT_OWNER_MISSING",
        "SCALABILITY_BLOCKED",
        "REPORT_OWNERSHIP_BLOCKED",
        "CONSTRAINT_STATUS_FAIL",
        "REPORT_STATUS_FAIL",
    }

    if categories.intersection(hard_fail_categories):
        return "UNTRUSTED_SCALABILITY_BLOCKED"

    if blocking_reasons:
        return "UNTRUSTED_SCALABILITY_BLOCKED"

    if warning_reasons:
        return "PARTIAL_SCALABILITY_REVIEW_REQUIRED"

    if not constraint_complete or not report_complete:
        return "PARTIAL_SCALABILITY_ARCHITECTURE_INCOMPLETE"

    if categories == {"NO_FAILURE_DETECTED"}:
        return "TRUSTED_SCALABILITY_READY"

    return "PARTIAL_SCALABILITY_REVIEW_REQUIRED"


def build_regen_scalability_failure_owner_text(
    status,
    complete,
    trust_level,
    can_proceed_to_master_gate,
    profile_complete,
    constraint_complete,
    report_complete,
    constraint_status,
    report_status,
    failure_categories,
    blocking_reasons,
    warning_reasons,
    missing_inputs,
    evidence,
    report_owner_blocking,
):
    lines = [
        "LEAF STAGE V.3 REGEN SCALABILITY FAILURE / VALIDATION OWNER",
        "=============================================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        f"Trust level: {trust_level}",
        f"Can proceed to Stage V.4 master gate: {can_proceed_to_master_gate}",
        "",
        "Owned By:",
        "- regen_scalability_failure_owner.py",
        "",
        "Scope:",
        "- Owns scalability failure classification.",
        "- Owns scalability validation readiness.",
        "- Does not perform raw constraint checks.",
        "- Does not own the readable report.",
        "- Does not approve final Stage V signoff.",
        "",
        "Architecture Evidence:",
        f"- Stage V.0 profile complete: {profile_complete}",
        f"- Stage V.1 constraint owner complete: {constraint_complete}",
        f"- Stage V.2 report owner complete: {report_complete}",
        f"- Stage V.1 constraint status: {constraint_status}",
        f"- Stage V.2 report status: {report_status}",
        "",
        "Failure Categories:",
    ]

    lines.extend([f"- {item}" for item in failure_categories] or ["- None."])

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Warning Reasons:")
    lines.extend([f"- {item}" for item in warning_reasons] or ["- None."])

    lines.append("")
    lines.append("Missing Inputs:")
    lines.extend([f"- {item}" for item in missing_inputs] or ["- None."])

    lines.append("")
    lines.append("Report Owner Blocking:")
    lines.extend([f"- {item}" for item in report_owner_blocking] or ["- None."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    lines.append("")
    lines.append("Next Required Action:")

    if trust_level == "TRUSTED_SCALABILITY_READY":
        lines.append("- Continue to Stage V.4 scalability master gate.")
    elif trust_level == "UNTRUSTED_SCALABILITY_BLOCKED":
        lines.append("- Resolve blocking scalability failures before master gate approval.")
    elif trust_level == "PARTIAL_SCALABILITY_REVIEW_REQUIRED":
        lines.append("- Review and resolve warning-level scalability issues.")
    else:
        lines.append("- Complete missing Stage V architecture before continuing.")

    lines.append("")
    lines.append("Rule:")
    lines.append("- Stage V.3 decides whether scalability evidence is ready for the master gate.")
    lines.append("- Stage V.3 does not approve final scalability.")
    lines.append("- Final approval belongs to Stage V.4 master gate.")

    return "\n".join(lines)


def _as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def _dedupe(items):
    seen = set()
    output = []

    for item in items:
        if item not in seen:
            output.append(item)
            seen.add(item)

    return output
