REQUIRED_RECOMMENDATION_OWNER_KEYS = (
    "recommendation_owner_items",
    "recommendation_owner_count",
    "recommendation_owner_status",
    "recommendation_owner_text",
    "recommendation_owner_primary_recommendation",
    "recommendation_owner_primary_reason",
    "recommendation_owner_primary_priority_score",
)

REQUIRED_STAGE_T4_KEYS = (
    "recommendation_owner_rejected_items",
    "recommendation_owner_rejected_count",
    "recommendation_owner_evidence_status",
    "recommendation_owner_primary_source",
)


def attach_recommendation_ownership_final_audit(results):
    if not isinstance(results, dict):
        return results

    audit = audit_recommendation_ownership(results)

    for key, value in audit.items():
        results[key] = value

    return results


def audit_recommendation_ownership(results):
    missing_required = []
    missing_stage_t4 = []
    failed_checks = []
    warnings = []

    for key in REQUIRED_RECOMMENDATION_OWNER_KEYS:
        if key not in results:
            missing_required.append(key)

    for key in REQUIRED_STAGE_T4_KEYS:
        if key not in results:
            missing_stage_t4.append(key)

    items = results.get("recommendation_owner_items", [])

    if not isinstance(items, list):
        failed_checks.append("recommendation_owner_items is not a list.")
        items = []

    if items:
        _audit_items(items, failed_checks, warnings)

    status = str(results.get("recommendation_owner_status") or "")

    if not status:
        failed_checks.append("recommendation_owner_status is missing or blank.")

    if results.get("recommendation_owner_count") != len(items):
        failed_checks.append("recommendation_owner_count does not match recommendation_owner_items length.")

    primary = results.get("recommendation_owner_primary_recommendation")

    if items and not primary:
        failed_checks.append("Primary recommendation is missing even though recommendation items exist.")

    if results.get("recommendation_explanation_text") and results.get("recommendation_owner_text"):
        warnings.append(
            "Legacy recommendation_explanation_text and recommendation_owner_text both exist. "
            "This is allowed during transition, but recommendation_owner_text must be treated as authoritative."
        )

    if missing_required:
        failed_checks.append("Missing required Stage T owner keys: " + ", ".join(missing_required))

    if missing_stage_t4:
        warnings.append(
            "Missing Stage T.4 evidence keys: " + ", ".join(missing_stage_t4)
        )

    final_status = "PASS"

    if failed_checks:
        final_status = "FAIL"
    elif warnings:
        final_status = "WARN"

    text = build_recommendation_ownership_final_audit_text(
        status=final_status,
        missing_required=missing_required,
        missing_stage_t4=missing_stage_t4,
        failed_checks=failed_checks,
        warnings=warnings,
        item_count=len(items),
    )

    return {
        "recommendation_ownership_final_audit_status": final_status,
        "recommendation_ownership_final_audit_missing_required_keys": missing_required,
        "recommendation_ownership_final_audit_missing_stage_t4_keys": missing_stage_t4,
        "recommendation_ownership_final_audit_failed_checks": failed_checks,
        "recommendation_ownership_final_audit_warnings": warnings,
        "recommendation_ownership_final_audit_item_count": len(items),
        "recommendation_ownership_final_audit_text": text,
        "stage_t_recommendation_ownership_complete": final_status == "PASS",
    }


def _audit_items(items, failed_checks, warnings):
    required_fields = (
        "recommendation",
        "reason",
        "evidence",
        "tradeoff",
        "expected_outcome",
        "risk",
        "confidence",
        "next_action",
        "severity",
        "source",
        "priority_score",
        "priority_rank",
        "evidence_status",
    )

    ranks = []

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            failed_checks.append(f"Recommendation item {index} is not a dictionary.")
            continue

        for field in required_fields:
            if field not in item:
                failed_checks.append(f"Recommendation item {index} is missing field: {field}")
                continue

            value = item.get(field)

            if isinstance(value, str) and not value.strip():
                failed_checks.append(f"Recommendation item {index} has blank field: {field}")

        if item.get("evidence_status") != "SUPPORTED":
            failed_checks.append(
                f"Recommendation item {index} is not marked SUPPORTED."
            )

        rank = item.get("priority_rank")

        if isinstance(rank, int):
            ranks.append(rank)
        else:
            warnings.append(f"Recommendation item {index} has non-integer priority_rank.")

    if ranks and sorted(ranks) != list(range(1, len(ranks) + 1)):
        failed_checks.append("Recommendation priority ranks are not sequential.")


def build_recommendation_ownership_final_audit_text(
        status,
        missing_required,
        missing_stage_t4,
        failed_checks,
        warnings,
        item_count,
):
    lines = [
        "LEAF RECOMMENDATION OWNERSHIP FINAL AUDIT",
        "=========================================",
        "",
        f"Status: {status}",
        f"Recommendation item count: {item_count}",
        "",
        "Purpose:",
        "- Verify that Recommendation Ownership is complete before moving to Stage U.",
        "- Ensure recommendations are ranked, supported, sourced, and report-owned.",
        "",
        "Failed Checks:",
    ]

    if failed_checks:
        for item in failed_checks:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Warnings:")

    if warnings:
        for item in warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Missing Required Stage T Keys:")

    if missing_required:
        for key in missing_required:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Missing Stage T.4 Evidence Keys:")

    if missing_stage_t4:
        for key in missing_stage_t4:
            lines.append(f"- {key}")
    else:
        lines.append("- None.")

    lines.append("")
    lines.append("Completion Rule:")
    lines.append("- Stage T is complete only when this audit returns PASS.")

    return "\n".join(lines)