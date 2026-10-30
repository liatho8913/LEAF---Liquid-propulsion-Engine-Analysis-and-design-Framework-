"""
LEAF Coating Validation Owner
=============================

REGEN PHASE 9G / PHASE 16T.3K.8

Owns conservative coating validation decisions.

This module uses coating provenance evidence from Phase 9F.

It does NOT:
- replace regen thermal solver coating logic
- apply coating changes automatically
- approve material validation

Phase 16T.3K.8 adds structured status-adapter output while preserving the
legacy coating validation owner contract.
"""

from __future__ import annotations

from typing import Any

from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


OWNER = "Coating Validation Owner"


def attach_coating_validation_owner(results):
    if not isinstance(results, dict):
        return results

    validation = build_coating_validation_owner(results)
    results.update(validation)
    return validation if results is None else results


def build_coating_validation_owner(results):
    results = results if isinstance(results, dict) else {}

    coating_name = results.get(
        "coating_source_provenance_coating",
        results.get("selected_coating", "None"),
    )

    provenance_complete = bool(
        results.get("phase_9f_coating_source_provenance_owner_complete", False)
    )

    no_coating_selected = bool(
        results.get("coating_source_provenance_no_coating_selected", False)
    )

    validation_mode = results.get(
        "coating_source_provenance_mode",
        "UNKNOWN_MODE",
    )

    placeholder_count = _safe_int(
        results.get("coating_source_provenance_placeholder_count"),
        default=0,
    )

    average_confidence = _safe_float(
        results.get("coating_source_provenance_average_confidence"),
        default=0.0,
    )

    conservative_source_pass = bool(
        results.get("coating_source_provenance_conservative_pass_allowed", False)
    )

    coating_query_temperature = _safe_float(
        results.get("coating_query_temperature")
        or results.get("wall_temperature_hot_gas")
        or results.get("Twg")
        or results.get("T_wall_hot"),
        default=0.0,
    )

    coating_service_temperature = _safe_float_or_none(
        results.get("coating_max_service_temperature")
        or results.get("coating_service_temperature")
    )

    coating_margin = None
    coating_margin_fraction = None

    if coating_service_temperature is not None:
        coating_margin = coating_service_temperature - coating_query_temperature
        if coating_service_temperature > 0:
            coating_margin_fraction = coating_margin / coating_service_temperature

    validation_rules = _build_coating_validation_rules(
        provenance_complete=provenance_complete,
        no_coating_selected=no_coating_selected,
        validation_mode=validation_mode,
        placeholder_count=placeholder_count,
        average_confidence=average_confidence,
        conservative_source_pass=conservative_source_pass,
        coating_query_temperature=coating_query_temperature,
        coating_service_temperature=coating_service_temperature,
        coating_margin=coating_margin,
    )

    blocking_rules = [
        rule for rule in validation_rules
        if rule.get("blocking") is True
    ]

    warning_rules = [
        rule for rule in validation_rules
        if rule.get("severity") == "WARNING"
    ]

    coating_valid = not blocking_rules

    status = (
        "PASS_COATING_VALIDATION_OWNER"
        if coating_valid
        else "FAIL_COATING_VALIDATION_OWNER"
    )

    structured_findings = _build_coating_validation_findings(
        status=status,
        coating_valid=coating_valid,
        coating_name=coating_name,
        validation_mode=validation_mode,
        validation_rules=validation_rules,
        blocking_rules=blocking_rules,
        warning_rules=warning_rules,
    )

    global_status_payload = classify_status(
        structured_findings,
        production_gate=True,
    )

    text = build_coating_validation_text(
        status=status,
        coating_valid=coating_valid,
        coating_name=coating_name,
        no_coating_selected=no_coating_selected,
        validation_mode=validation_mode,
        coating_query_temperature=coating_query_temperature,
        coating_service_temperature=coating_service_temperature,
        coating_margin=coating_margin,
        coating_margin_fraction=coating_margin_fraction,
        average_confidence=average_confidence,
        validation_rules=validation_rules,
        blocking_rules=blocking_rules,
        warning_rules=warning_rules,
        global_status_payload=global_status_payload,
    )

    return {
        "coating_validation_owner_status": status,
        "coating_validation_owner_complete": True,
        "coating_validation_coating": coating_name,
        "coating_validation_pass": coating_valid,
        "coating_validation_no_coating_selected": no_coating_selected,
        "coating_validation_mode": validation_mode,
        "coating_validation_query_temperature": coating_query_temperature,
        "coating_validation_service_temperature": coating_service_temperature,
        "coating_validation_temperature_margin": coating_margin,
        "coating_validation_temperature_margin_fraction": coating_margin_fraction,
        "coating_validation_average_confidence": average_confidence,
        "coating_validation_rules": validation_rules,
        "coating_validation_blocking_rules": blocking_rules,
        "coating_validation_warning_rules": warning_rules,
        "coating_validation_blocking_rule_count": len(blocking_rules),
        "coating_validation_warning_rule_count": len(warning_rules),
        "coating_validation_structured_findings": structured_findings,
        "coating_validation_global_status": global_status_payload["status"],
        "coating_validation_global_status_payload": global_status_payload,
        "coating_validation_text": text,
        "phase_9g_coating_validation_owner_complete": True,
        "phase_16t3k8_status_adapter_complete": True,
    }


def _build_coating_validation_findings(
        status,
        coating_valid,
        coating_name,
        validation_mode,
        validation_rules,
        blocking_rules,
        warning_rules,
):
    evidence = {
        "status": status,
        "coating_valid": coating_valid,
        "coating_name": coating_name,
        "validation_mode": validation_mode,
        "blocking_rule_count": len(blocking_rules),
        "warning_rule_count": len(warning_rules),
    }

    findings = []

    for rule in validation_rules:
        if rule.get("passed") is True:
            continue

        category = _category_for_rule(rule)

        findings.append(
            make_finding(
                message=str(rule.get("reason")),
                category=category,
                owner=OWNER,
                evidence={
                    **evidence,
                    "rule_id": rule.get("rule_id"),
                    "corrective_action": rule.get("corrective_action"),
                    "legacy_rule_severity": rule.get("severity"),
                },
            )
        )

    if not findings:
        findings.append(
            make_finding(
                message="Coating validation owner completed successfully.",
                category="COMPLETE",
                owner=OWNER,
                evidence=evidence,
            )
        )

    return findings


def _category_for_rule(rule):
    rule_id = str(rule.get("rule_id", ""))
    severity = str(rule.get("severity", "")).upper()

    if rule_id == "COAT-VAL-PROVENANCE-COMPLETE":
        return "VALIDATION_INCOMPLETE"

    if rule_id == "COAT-VAL-SOURCED-MODE":
        if "PLACEHOLDER" in str(rule.get("reason", "")).upper():
            return "PLACEHOLDER_USED_FOR_PASS"
        return "VALIDATION_INCOMPLETE"

    if rule_id == "COAT-VAL-NO-PLACEHOLDER-SOURCES":
        return "PLACEHOLDER_USED_FOR_PASS"

    if rule_id in {
        "COAT-VAL-SOURCE-CONFIDENCE",
        "COAT-VAL-SOURCE-CONSERVATIVE-PASS",
        "COAT-VAL-SERVICE-TEMP-AVAILABLE",
    }:
        return "VALIDATION_INCOMPLETE"

    if rule_id == "COAT-VAL-TEMPERATURE-MARGIN":
        return "PHYSICS_INVALID"

    if severity == "WARNING":
        return "MANUAL_REVIEW_REQUIRED"

    return "VALIDATION_FAILURE"


def _build_coating_validation_rules(
        provenance_complete,
        no_coating_selected,
        validation_mode,
        placeholder_count,
        average_confidence,
        conservative_source_pass,
        coating_query_temperature,
        coating_service_temperature,
        coating_margin,
):
    rules = []

    rules.append(_rule(
        rule_id="COAT-VAL-PROVENANCE-COMPLETE",
        passed=provenance_complete,
        severity="FAIL",
        reason="Coating source/provenance ownership must be complete.",
        corrective_action="Complete Phase 9F and ensure coating source records exist.",
    ))

    if no_coating_selected:
        rules.append(_rule(
            rule_id="COAT-VAL-NO-COATING-SELECTED",
            passed=True,
            severity="INFO",
            reason="No coating selected; coating validation is structurally valid as an uncoated configuration.",
            corrective_action="No coating action required unless a coating is intentionally selected.",
        ))
        return rules

    rules.append(_rule(
        rule_id="COAT-VAL-SOURCED-MODE",
        passed=(validation_mode == "SOURCED_VALIDATION_MODE"),
        severity="FAIL",
        reason=(
            "Coating validation requires SOURCED_VALIDATION_MODE. "
            f"Current mode is {validation_mode}."
        ),
        corrective_action="Replace placeholder coating data with sourced coating records.",
    ))

    rules.append(_rule(
        rule_id="COAT-VAL-NO-PLACEHOLDER-SOURCES",
        passed=(placeholder_count == 0),
        severity="FAIL",
        reason="Placeholder coating sources are present and cannot produce conservative coating PASS.",
        corrective_action="Replace placeholder coating sources with sourced records.",
    ))

    rules.append(_rule(
        rule_id="COAT-VAL-SOURCE-CONFIDENCE",
        passed=(average_confidence >= 0.75),
        severity="FAIL",
        reason=(
            "Average coating source confidence is below required threshold "
            f"(value={average_confidence}, required>=0.75)."
        ),
        corrective_action="Use higher-confidence coating sources.",
    ))

    rules.append(_rule(
        rule_id="COAT-VAL-SOURCE-CONSERVATIVE-PASS",
        passed=conservative_source_pass,
        severity="FAIL",
        reason="Coating provenance owner has not allowed conservative source pass.",
        corrective_action="Resolve coating provenance blockers before coating validation.",
    ))

    rules.append(_rule(
        rule_id="COAT-VAL-SERVICE-TEMP-AVAILABLE",
        passed=(coating_service_temperature is not None),
        severity="FAIL",
        reason="No coating service temperature is available.",
        corrective_action="Add sourced coating service temperature data.",
    ))

    if coating_service_temperature is not None:
        rules.append(_rule(
            rule_id="COAT-VAL-TEMPERATURE-MARGIN",
            passed=(coating_margin is not None and coating_margin > 0),
            severity="FAIL",
            reason=(
                "Coating operating temperature exceeds coating service limit "
                f"(query={coating_query_temperature}, limit={coating_service_temperature})."
            ),
            corrective_action="Reduce wall temperature, change coating, improve cooling, or remove invalid coating assumption.",
        ))

        rules.append(_rule(
            rule_id="COAT-VAL-TEMPERATURE-MARGIN-WARNING",
            passed=(coating_margin is not None and coating_margin >= 0.10 * coating_service_temperature),
            severity="WARNING",
            reason=(
                "Coating temperature margin is below 10 percent of service limit "
                f"(margin={coating_margin}, limit={coating_service_temperature})."
            ),
            corrective_action="Increase coating thermal margin where possible.",
        ))

    return rules


def build_coating_validation_text(
        status,
        coating_valid,
        coating_name,
        no_coating_selected,
        validation_mode,
        coating_query_temperature,
        coating_service_temperature,
        coating_margin,
        coating_margin_fraction,
        average_confidence,
        validation_rules,
        blocking_rules,
        warning_rules,
        global_status_payload=None,
):
    lines = [
        "LEAF REGEN PHASE 9G COATING VALIDATION OWNER",
        "=============================================",
        "",
        f"Status: {status}",
        f"Coating valid: {coating_valid}",
        f"Coating: {coating_name}",
        f"No coating selected: {no_coating_selected}",
        f"Validation mode: {validation_mode}",
        f"Query temperature: {coating_query_temperature}",
        f"Service temperature: {coating_service_temperature}",
        f"Temperature margin: {coating_margin}",
        f"Temperature margin fraction: {coating_margin_fraction}",
        f"Average source confidence: {average_confidence}",
        f"Blocking rule count: {len(blocking_rules)}",
        f"Warning rule count: {len(warning_rules)}",
        "",
        "Owned By:",
        "- coating_validation_owner.py",
        "",
        "Scope:",
        "- Owns conservative coating validation decisions.",
        "- Owns coating validation rules.",
        "- Owns coating temperature margin checks.",
        "- Owns placeholder/source-confidence blocking.",
        "- Does not replace regen thermal coating logic yet.",
        "",
        "Validation Rules:",
    ]

    for rule in validation_rules:
        lines.append("")
        lines.append(f"- Rule ID: {rule.get('rule_id')}")
        lines.append(f"  Passed: {rule.get('passed')}")
        lines.append(f"  Severity: {rule.get('severity')}")
        lines.append(f"  Blocking: {rule.get('blocking')}")
        lines.append(f"  Reason: {rule.get('reason')}")
        lines.append(f"  Corrective Action: {rule.get('corrective_action')}")

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
    lines.append("Next Required Action:")
    lines.append(
        "- After Phase 9G is verified, build Phase 9H material & coating foundation audit."
    )
    lines.append("- Structured findings now control canonical global status classification.")

    return "\n".join(lines)


def _rule(rule_id, passed, severity, reason, corrective_action):
    severity = str(severity).upper()
    blocking = (not bool(passed)) and severity == "FAIL"

    return {
        "rule_id": rule_id,
        "passed": bool(passed),
        "severity": severity,
        "blocking": blocking,
        "reason": reason,
        "corrective_action": corrective_action,
    }


def _safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _safe_float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)
