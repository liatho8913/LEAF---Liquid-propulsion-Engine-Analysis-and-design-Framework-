"""
PHASE 11B.1P / PHASE 16T.3K.6
Regen Validation Master Gate

Determines whether regen validation is complete enough to be trusted by
downstream engineering, optimisation, reports, and GUI workflows.

Phase 16T.3K.6 adds structured status-adapter output while preserving the
legacy validation master-gate contract.
"""

from __future__ import annotations

from typing import Any

from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


OWNER = "Regen Validation Master Gate"


PASS_VALIDATION_STATUSES = {
    "PASS_REGEN_VALIDATION",
    "PASS_REGEN_VALIDATION_OWNER",
    "PASS_REGEN_VALIDATION_MASTER_GATE",
    "PASS_SOURCED_VALIDATION_MODE",
}

PLACEHOLDER_STATUSES = {
    "PLACEHOLDER_MODE",
    "PLACEHOLDER_ONLY",
    "WARN_PLACEHOLDER_MODE",
    "WARN_REGEN_VALIDATION_PLACEHOLDER_MODE",
    "WARN_REGEN_VALIDATION_PLACEHOLDER_ONLY",
}

PARTIAL_STATUSES = {
    "PARTIAL_SOURCE_MODE",
    "WARN_PARTIAL_SOURCE_MODE",
    "WARN_REGEN_VALIDATION_PARTIAL_SOURCE_MODE",
}


def attach_regen_validation_master_gate(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_validation_master_gate(results)
    results.update(payload)
    return results


def _first_present(results: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in results:
            return results.get(key)
    return None


def _build_regen_validation_findings(
    *,
    status: str,
    reason: str,
    evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    if status == "PASS_REGEN_VALIDATION_MASTER_GATE":
        category = "COMPLETE"
    elif "PLACEHOLDER" in status:
        category = "PLACEHOLDER_DATA"
    elif "PARTIAL" in status:
        category = "MANUAL_REVIEW_REQUIRED"
    elif "INCOMPLETE" in status or "MISSING" in status:
        category = "VALIDATION_INCOMPLETE"
    elif "FAIL" in status:
        category = "VALIDATION_FAILURE"
    else:
        category = "MANUAL_REVIEW_REQUIRED"

    return [
        make_finding(
            message=reason,
            category=category,
            owner=OWNER,
            evidence=evidence,
        )
    ]


def build_regen_validation_master_gate(results):
    current_contract_keys = (
        "regen_source_validation_gate_status",
        "regen_source_validation_pass_allowed",
        "regen_property_table_owner_status",
        "regen_property_table_owner_pass_allowed",
        "regen_conservative_validation_gate_status",
        "material_temperature_limit_precheck_complete",
        "material_temperature_limit_precheck_pass",
    )

    validation_complete = all(
        key in results
        for key in current_contract_keys
    )

    source_gate_status = results.get(
        "regen_source_validation_gate_status"
    )

    source_pass_allowed = (
        results.get(
            "regen_source_validation_pass_allowed"
        )
        is True
    )

    property_table_status = results.get(
        "regen_property_table_owner_status"
    )

    property_table_pass_allowed = (
        results.get(
            "regen_property_table_owner_pass_allowed"
        )
        is True
    )

    conservative_gate_status = results.get(
        "regen_conservative_validation_gate_status"
    )

    material_temperature_limit_precheck_complete = (
        results.get(
            "material_temperature_limit_precheck_complete"
        )
        is True
    )

    material_temperature_limit_precheck_pass = (
        results.get(
            "material_temperature_limit_precheck_pass"
        )
        is True
    )

    validation_status = _first_present(
        results,
        (
            "regen_validation_status",
            "regen_validation_owner_status",
            "regen_validation_mode_status",
        ),
    )

    validation_mode = _first_present(
        results,
        (
            "regen_validation_mode",
            "material_validation_mode",
            "coating_validation_mode",
        ),
    )

    sourced_validation = bool(
        _first_present(
            results,
            (
                "regen_sourced_validation_complete",
                "sourced_validation_complete",
                "regen_validation_sourced",
            ),
        )
    )

    placeholder_only = bool(
        _first_present(
            results,
            (
                "regen_placeholder_only",
                "placeholder_only",
                "validation_placeholder_only",
            ),
        )
    )

    partial_source = bool(
        _first_present(
            results,
            (
                "regen_partial_source_mode",
                "partial_source_mode",
                "validation_partial_source_mode",
            ),
        )
    )

    evidence = {
        "regen_validation_complete": validation_complete,
        "regen_validation_status": validation_status,
        "regen_validation_mode": validation_mode,
        "sourced_validation_complete": sourced_validation,
        "placeholder_only": placeholder_only,
        "partial_source": partial_source,
    }

    validation_status_text = str(validation_status or "").upper()
    validation_mode_text = str(validation_mode or "").upper()

    if not validation_complete:
        status = "FAIL_REGEN_VALIDATION_MASTER_GATE_INCOMPLETE"
        ready = False
        reason = "Regen validation owner has not completed."

    elif (
        placeholder_only
        or validation_status in PLACEHOLDER_STATUSES
        or validation_mode in PLACEHOLDER_STATUSES
        or "PLACEHOLDER" in validation_status_text
        or "PLACEHOLDER" in validation_mode_text
    ):
        status = "WARN_REGEN_VALIDATION_MASTER_GATE_PLACEHOLDER_ONLY"
        ready = False
        reason = "Placeholder-only validation cannot produce production sign-off."

    elif (
        partial_source
        or validation_status in PARTIAL_STATUSES
        or validation_mode in PARTIAL_STATUSES
        or "PARTIAL" in validation_status_text
        or "PARTIAL" in validation_mode_text
    ):
        status = "WARN_REGEN_VALIDATION_MASTER_GATE_PARTIAL_SOURCE_REVIEW"
        ready = False
        reason = "Partial-source validation requires manual review before sign-off."

    elif (
        not source_pass_allowed
        or conservative_gate_status != "PASS_ALLOWED"
    ):
        status = "FAIL_REGEN_VALIDATION_MASTER_GATE_SOURCE_BLOCKED"
        ready = False
        reason = (
            "Current source-validation ownership contract "
            "does not allow final regen validation PASS."
        )

    elif not property_table_pass_allowed:
        status = "FAIL_REGEN_VALIDATION_MASTER_GATE_PROPERTY_TABLE_BLOCKED"
        ready = False
        reason = (
            "Current property-table ownership contract "
            "does not allow final regen validation PASS."
        )

    elif not material_temperature_limit_precheck_complete:
        status = (
            "FAIL_REGEN_VALIDATION_MASTER_GATE_THERMAL_LIMIT_INCOMPLETE"
        )
        ready = False
        reason = (
            "Material temperature-limit precheck is incomplete."
        )

    elif not material_temperature_limit_precheck_pass:
        status = (
            "FAIL_REGEN_VALIDATION_MASTER_GATE_THERMAL_LIMIT_BLOCKED"
        )
        ready = False
        reason = (
            "Material wall temperature exceeds the active "
            "material temperature limit."
        )

    elif "FAIL" in validation_status_text or "INVALID" in validation_status_text:
        status = "FAIL_REGEN_VALIDATION_MASTER_GATE_FAILED"
        ready = False
        reason = "Regen validation failed."

    elif (
        validation_status in PASS_VALIDATION_STATUSES
        or validation_mode == "SOURCED_VALIDATION_MODE"
        or sourced_validation
        or (
            source_gate_status == "PASS_SOURCED_VALIDATION"
            and source_pass_allowed
            and property_table_status == "PASS_PROPERTY_TABLE_OWNER"
            and property_table_pass_allowed
            and conservative_gate_status == "PASS_ALLOWED"
        )
    ):
        status = "PASS_REGEN_VALIDATION_MASTER_GATE"
        ready = True
        reason = "Regen validation is complete and sourced."

    else:
        status = "FAIL_REGEN_VALIDATION_MASTER_GATE_MISSING_PASS_STATUS"
        ready = False
        reason = "Regen validation did not provide a recognised passing sourced status."

    structured_findings = _build_regen_validation_findings(
        status=status,
        reason=reason,
        evidence=evidence,
    )

    global_status_payload = classify_status(
        structured_findings,
        production_gate=True,
    )

    report = build_regen_validation_master_gate_report(
        status=status,
        ready=ready,
        reason=reason,
        global_status_payload=global_status_payload,
    )

    return {
        "regen_validation_master_gate_complete": True,
        "phase_11b_1p_regen_validation_master_gate_complete": True,
        "phase_16t3w6_status_adapter_complete": True,
        "phase_16t3w6_regen_validation_master_gate_status_adapter_complete": True,
        "regen_validation_master_gate_status_adapter_complete": True,
        "regen_validation_master_gate_adapter_report": report,
        "regen_validation_master_gate_status": status,
        "regen_validation_master_gate_ready": ready,
        "regen_validation_master_gate_pass_allowed": ready,
        "regen_validation_master_gate_reason": reason,
        "regen_validation_master_gate_structured_findings": structured_findings,
        "regen_validation_master_gate_global_status": global_status_payload["status"],
        "regen_validation_master_gate_global_status_payload": global_status_payload,
        "structured_findings": structured_findings,
        "global_status": global_status_payload["status"],
        "global_status_payload": global_status_payload,
        "adapter_report": report,
        "regen_validation_master_gate_report": report,
    }


def build_regen_validation_master_gate_report(
    status,
    ready,
    reason,
    global_status_payload=None,
):
    lines = [
        "LEAF PHASE 11B.1P REGEN VALIDATION MASTER GATE",
        "================================================",
        "",
        f"Status: {status}",
        f"Ready: {ready}",
        "",
        "Reason:",
        f"- {reason}",
    ]

    if global_status_payload is not None:
        lines.extend([
            "",
            "Global Status Engine:",
            f"- canonical_status: {global_status_payload.get('status')}",
            f"- finding_count: {global_status_payload.get('finding_count')}",
            f"- blocked: {global_status_payload.get('blocked')}",
            f"- failed: {global_status_payload.get('failed')}",
        ])

    lines.extend([
        "",
        "Rule:",
        "- Sourced complete validation maps to PASS.",
        "- Placeholder-only validation can never produce production sign-off.",
        "- Partial-source validation requires review and blocks production sign-off.",
        "- Failed/invalid validation maps to FAIL.",
        "- Structured findings now control canonical global status classification.",
    ])

    return "\n".join(lines)
