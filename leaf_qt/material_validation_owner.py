"""
LEAF Material Validation Owner
==============================

REGEN MATERIAL VALIDATION / PHASE 16T.3K.10

Owns conservative material validation decisions.

Phase 16T.3K.10 adds structured status-adapter output while preserving the
legacy material validation owner contract.
"""

from __future__ import annotations

from typing import Any

from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


OWNER = "Material Validation Owner"


def attach_material_validation_owner(results):
    if not isinstance(results, dict):
        return results

    validation = build_material_validation_owner(results)
    results.update(validation)
    return results




def _leaf_49d_attach_material_intelligence_validation(
    results,
    validation_rules,
):
    """Validate Programme 49 material-intelligence claims.

    Missing compatibility evidence never becomes COMPATIBLE.
    Definitive COMPATIBLE / INCOMPATIBLE claims require sourced
    evidence, source-quality identification, and a citation.
    """

    results = (
        results
        if isinstance(results, dict)
        else {}
    )

    validation_rules = (
        validation_rules
        if isinstance(validation_rules, list)
        else []
    )

    thermal_status = str(
        results.get(
            "material_thermal_expansion_intelligence_status"
        )
        or
        "UNAVAILABLE"
    ).strip().upper()

    compatibility_status = str(
        results.get(
            "material_compatibility_status"
        )
        or
        "UNVERIFIED_NO_SOURCED_COMPATIBILITY_EVIDENCE"
    ).strip().upper()

    evidence = results.get(
        "material_compatibility_evidence"
    )

    source_quality = str(
        results.get(
            "material_compatibility_source_quality"
        )
        or
        ""
    ).strip()

    citation = str(
        results.get(
            "material_compatibility_source_citation"
        )
        or
        ""
    ).strip()

    unacceptable_quality = {
        "",
        "UNKNOWN",
        "PLACEHOLDER",
        "ASSUMED",
        "USER_ASSUMED",
    }

    source_quality_acceptable = (
        source_quality.upper()
        not in
        unacceptable_quality
    )

    evidence_sourced = bool(
        evidence
        and
        source_quality_acceptable
        and
        citation
    )

    definitive_claim = (
        compatibility_status
        in
        {
            "COMPATIBLE",
            "INCOMPATIBLE",
        }
    )

    claim_safe = (
        not definitive_claim
        or
        evidence_sourced
    )

    compatibility_pass = bool(
        compatibility_status
        ==
        "COMPATIBLE"
        and
        evidence_sourced
    )

    validation_rules.append(
        _rule(
            rule_id=(
                "MAT-VAL-THERMAL-EXPANSION-INTELLIGENCE"
            ),
            passed=(
                thermal_status
                ==
                "CALCULATED_FREE_THERMAL_STRAIN_DIFFERENTIAL"
            ),
            severity="WARNING",
            reason=(
                "Base-wall free thermal-expansion strain "
                "intelligence is unavailable or incomplete."
            ),
            corrective_action=(
                "Provide material CTE plus hot-side and "
                "coolant-side wall temperatures."
            ),
        )
    )

    validation_rules.append(
        _rule(
            rule_id=(
                "MAT-VAL-COMPATIBILITY-CLAIM-SOURCED"
            ),
            passed=claim_safe,
            severity="FAIL",
            reason=(
                "A definitive material compatibility claim "
                "requires sourced evidence and citation."
            ),
            corrective_action=(
                "Provide application-specific sourced "
                "compatibility evidence before declaring "
                "COMPATIBLE or INCOMPATIBLE."
            ),
        )
    )

    validation_rules.append(
        _rule(
            rule_id=(
                "MAT-VAL-COMPATIBILITY-EVIDENCE-AVAILABLE"
            ),
            passed=evidence_sourced,
            severity="WARNING",
            reason=(
                "Material compatibility remains unverified "
                "because acceptable sourced evidence is absent."
            ),
            corrective_action=(
                "Provide environment-specific compatibility "
                "evidence, source quality, and citation."
            ),
        )
    )

    results[
        "material_compatibility_status"
    ] = compatibility_status

    results[
        "material_compatibility_pass"
    ] = compatibility_pass

    results[
        "material_compatibility_enforcement_ready"
    ] = evidence_sourced

    results[
        "material_compatibility_evidence_sourced"
    ] = evidence_sourced

    results[
        "material_compatibility_source_quality"
    ] = source_quality

    results[
        "material_compatibility_source_citation"
    ] = citation

    return validation_rules


def build_material_validation_owner(results):
    results = results if isinstance(results, dict) else {}

    material_name = results.get(
        "material_source_provenance_material",
        results.get("selected_material", results.get("material", "UNKNOWN_MATERIAL")),
    )

    provenance_complete = bool(
        results.get("material_source_provenance_owner_complete")
        or results.get("phase_9e_material_source_provenance_owner_complete")
        or results.get("phase_9f_material_source_provenance_owner_complete")
    )

    validation_mode = results.get(
        "material_source_provenance_mode",
        results.get("material_validation_mode", "UNKNOWN_MODE"),
    )

    placeholder_count = _safe_int(
        results.get("material_source_provenance_placeholder_count")
        or results.get("material_placeholder_source_count"),
        default=0,
    )

    average_confidence = _safe_float(
        results.get("material_source_provenance_average_confidence")
        or results.get("material_source_confidence")
        or results.get("material_average_source_confidence"),
        default=0.0,
    )

    conservative_source_pass = bool(
        results.get("material_source_provenance_conservative_pass_allowed")
        or results.get("material_conservative_source_pass_allowed")
    )

    wall_temperature = _safe_float(
        results.get("material_query_temperature")
        or results.get("wall_temperature_hot_gas")
        or results.get("Twg")
        or results.get("T_wall_hot")
        or results.get("regen_axial_worst_wall_temperature"),
        default=0.0,
    )

    service_temperature = _safe_float_or_none(
        results.get("material_max_service_temperature")
        or results.get("material_service_temperature")
        or results.get("material_allowable_temperature")
        or results.get("material_melting_temperature")
    )

    material_margin = _safe_float_or_none(
        results.get("material_temperature_margin")
        or results.get("regen_axial_worst_material_margin")
    )

    if material_margin is None and service_temperature is not None:
        material_margin = service_temperature - wall_temperature

    margin_fraction = None
    if service_temperature is not None and service_temperature > 0 and material_margin is not None:
        margin_fraction = material_margin / service_temperature

    validation_rules = _build_material_validation_rules(
        provenance_complete=provenance_complete,
        validation_mode=validation_mode,
        placeholder_count=placeholder_count,
        average_confidence=average_confidence,
        conservative_source_pass=conservative_source_pass,
        wall_temperature=wall_temperature,
        service_temperature=service_temperature,
        material_margin=material_margin,
    )

    validation_rules = _leaf_49d_attach_material_intelligence_validation(
        results,
        validation_rules,
    )

    blocking_rules = [
        rule for rule in validation_rules
        if rule.get("blocking") is True
    ]

    warning_rules = [
        rule for rule in validation_rules
        if rule.get("severity") == "WARNING" and rule.get("passed") is False
    ]

    material_valid = not blocking_rules

    status = (
        "PASS_MATERIAL_VALIDATION_OWNER"
        if material_valid
        else "FAIL_MATERIAL_VALIDATION_OWNER"
    )

    structured_findings = _build_material_validation_findings(
        status=status,
        material_valid=material_valid,
        material_name=material_name,
        validation_mode=validation_mode,
        validation_rules=validation_rules,
        blocking_rules=blocking_rules,
        warning_rules=warning_rules,
    )

    global_status_payload = classify_status(
        structured_findings,
        production_gate=True,
    )

    text = build_material_validation_text(
        status=status,
        material_valid=material_valid,
        material_name=material_name,
        validation_mode=validation_mode,
        wall_temperature=wall_temperature,
        service_temperature=service_temperature,
        material_margin=material_margin,
        margin_fraction=margin_fraction,
        average_confidence=average_confidence,
        validation_rules=validation_rules,
        blocking_rules=blocking_rules,
        warning_rules=warning_rules,
        global_status_payload=global_status_payload,
    )

    return {
        "material_validation_owner_status": status,
        "material_thermal_expansion_intelligence_status": results.get("material_thermal_expansion_intelligence_status"),
        "material_thermal_stress_model_available": results.get("material_thermal_stress_model_available", False),
        "material_thermal_stress_model_status": results.get("material_thermal_stress_model_status"),
        "material_compatibility_status": results.get("material_compatibility_status"),
        "material_compatibility_pass": results.get("material_compatibility_pass", False),
        "material_compatibility_enforcement_ready": results.get("material_compatibility_enforcement_ready", False),
        "material_compatibility_evidence_sourced": results.get("material_compatibility_evidence_sourced", False),
        "material_compatibility_source_quality": results.get("material_compatibility_source_quality"),
        "material_compatibility_source_citation": results.get("material_compatibility_source_citation"),
        "material_validation_owner_complete": True,
        "material_validation_material": material_name,
        "material_validation_pass": material_valid,
        "material_validation_mode": validation_mode,
        "material_validation_query_temperature": wall_temperature,
        "material_validation_service_temperature": service_temperature,
        "material_validation_temperature_margin": material_margin,
        "material_validation_temperature_margin_fraction": margin_fraction,
        "material_validation_average_confidence": average_confidence,
        "material_validation_rules": validation_rules,
        "material_validation_blocking_rules": blocking_rules,
        "material_validation_warning_rules": warning_rules,
        "material_validation_blocking_rule_count": len(blocking_rules),
        "material_validation_warning_rule_count": len(warning_rules),
        "material_validation_structured_findings": structured_findings,
        "material_validation_global_status": global_status_payload["status"],
        "material_validation_global_status_payload": global_status_payload,
        "material_validation_text": text,
        "phase_material_validation_owner_complete": True,
        "phase_16t3k10_status_adapter_complete": True,
    }


def _build_material_validation_findings(
    status,
    material_valid,
    material_name,
    validation_mode,
    validation_rules,
    blocking_rules,
    warning_rules,
):
    evidence = {
        "status": status,
        "material_valid": material_valid,
        "material_name": material_name,
        "validation_mode": validation_mode,
        "blocking_rule_count": len(blocking_rules),
        "warning_rule_count": len(warning_rules),
    }

    findings = []

    for rule in validation_rules:
        if rule.get("passed") is True:
            continue

        findings.append(
            make_finding(
                message=str(rule.get("reason")),
                category=_category_for_rule(rule),
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
                message="Material validation owner completed successfully.",
                category="COMPLETE",
                owner=OWNER,
                evidence=evidence,
            )
        )

    return findings


def _category_for_rule(rule):
    rule_id = str(rule.get("rule_id", ""))
    severity = str(rule.get("severity", "")).upper()

    if rule_id == "MAT-VAL-PROVENANCE-COMPLETE":
        return "VALIDATION_INCOMPLETE"

    if rule_id == "MAT-VAL-SOURCED-MODE":
        if "PLACEHOLDER" in str(rule.get("reason", "")).upper():
            return "PLACEHOLDER_USED_FOR_PASS"
        return "VALIDATION_INCOMPLETE"

    if rule_id == "MAT-VAL-NO-PLACEHOLDER-SOURCES":
        return "PLACEHOLDER_USED_FOR_PASS"

    if rule_id in {
        "MAT-VAL-SOURCE-CONFIDENCE",
        "MAT-VAL-SOURCE-CONSERVATIVE-PASS",
        "MAT-VAL-SERVICE-TEMP-AVAILABLE",
    }:
        return "VALIDATION_INCOMPLETE"

    if rule_id == "MAT-VAL-TEMPERATURE-MARGIN":
        return "PHYSICS_INVALID"

    if severity == "WARNING":
        return "MANUAL_REVIEW_REQUIRED"

    return "VALIDATION_FAILURE"


def _build_material_validation_rules(
    provenance_complete,
    validation_mode,
    placeholder_count,
    average_confidence,
    conservative_source_pass,
    wall_temperature,
    service_temperature,
    material_margin,
):
    rules = []

    rules.append(_rule(
        rule_id="MAT-VAL-PROVENANCE-COMPLETE",
        passed=provenance_complete,
        severity="FAIL",
        reason="Material source/provenance ownership must be complete.",
        corrective_action="Complete material provenance ownership and ensure source records exist.",
    ))

    rules.append(_rule(
        rule_id="MAT-VAL-SOURCED-MODE",
        passed=(validation_mode == "SOURCED_VALIDATION_MODE"),
        severity="FAIL",
        reason=(
            "Material validation requires SOURCED_VALIDATION_MODE. "
            f"Current mode is {validation_mode}."
        ),
        corrective_action="Replace placeholder material data with sourced material records.",
    ))

    rules.append(_rule(
        rule_id="MAT-VAL-NO-PLACEHOLDER-SOURCES",
        passed=(placeholder_count == 0),
        severity="FAIL",
        reason="Placeholder material sources are present and cannot produce conservative material PASS.",
        corrective_action="Replace placeholder material sources with sourced records.",
    ))

    rules.append(_rule(
        rule_id="MAT-VAL-SOURCE-CONFIDENCE",
        passed=(average_confidence >= 0.75),
        severity="FAIL",
        reason=(
            "Average material source confidence is below required threshold "
            f"(value={average_confidence}, required>=0.75)."
        ),
        corrective_action="Use higher-confidence material sources.",
    ))

    rules.append(_rule(
        rule_id="MAT-VAL-SOURCE-CONSERVATIVE-PASS",
        passed=conservative_source_pass,
        severity="FAIL",
        reason="Material provenance owner has not allowed conservative source pass.",
        corrective_action="Resolve material provenance blockers before material validation.",
    ))

    rules.append(_rule(
        rule_id="MAT-VAL-SERVICE-TEMP-AVAILABLE",
        passed=(service_temperature is not None),
        severity="FAIL",
        reason="No material service temperature is available.",
        corrective_action="Add sourced material service/allowable temperature data.",
    ))

    if service_temperature is not None:
        rules.append(_rule(
            rule_id="MAT-VAL-TEMPERATURE-MARGIN",
            passed=(material_margin is not None and material_margin > 0),
            severity="FAIL",
            reason=(
                "Material operating temperature exceeds material service limit "
                f"(query={wall_temperature}, limit={service_temperature}, margin={material_margin})."
            ),
            corrective_action="Reduce wall temperature, improve cooling, change material, or reject invalid geometry.",
        ))

        rules.append(_rule(
            rule_id="MAT-VAL-TEMPERATURE-MARGIN-WARNING",
            passed=(material_margin is not None and material_margin >= 0.10 * service_temperature),
            severity="WARNING",
            reason=(
                "Material temperature margin is below 10 percent of service limit "
                f"(margin={material_margin}, limit={service_temperature})."
            ),
            corrective_action="Increase material thermal margin where possible.",
        ))

    return rules


def build_material_validation_text(
    status,
    material_valid,
    material_name,
    validation_mode,
    wall_temperature,
    service_temperature,
    material_margin,
    margin_fraction,
    average_confidence,
    validation_rules,
    blocking_rules,
    warning_rules,
    global_status_payload=None,
):
    lines = [
        "LEAF MATERIAL VALIDATION OWNER",
        "==============================",
        "",
        f"Status: {status}",
        f"Material valid: {material_valid}",
        f"Material: {material_name}",
        f"Validation mode: {validation_mode}",
        f"Wall/query temperature: {wall_temperature}",
        f"Service temperature: {service_temperature}",
        f"Temperature margin: {material_margin}",
        f"Temperature margin fraction: {margin_fraction}",
        f"Average source confidence: {average_confidence}",
        f"Blocking rule count: {len(blocking_rules)}",
        f"Warning rule count: {len(warning_rules)}",
        "",
        "Owned By:",
        "- material_validation_owner.py",
        "",
        "Scope:",
        "- Owns conservative material validation decisions.",
        "- Owns material source-confidence and placeholder blocking.",
        "- Owns material service-temperature checks.",
        "- Owns material wall-temperature margin checks.",
        "- Does not replace regen thermal solver logic.",
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
    lines.append("Rule:")
    lines.append("- Sourced material validation may pass only with complete provenance.")
    lines.append("- Placeholder material data can never produce production sign-off.")
    lines.append("- Unsafe wall-temperature margin fails through the global status engine.")
    lines.append("- Warning-only low margins block production sign-off until reviewed.")
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
