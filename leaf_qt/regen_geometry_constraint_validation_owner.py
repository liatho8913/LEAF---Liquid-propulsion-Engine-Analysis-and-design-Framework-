"""
PHASE 16T.3K.12
Regen Geometry Constraint Validation Owner

Owns conservative validation of regenerative cooling geometry constraints.

Phase 16T.3K.12 adds structured findings and global_status while preserving
the legacy geometry constraint validation owner contract.
"""

from __future__ import annotations

from typing import Any

from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


OWNER = "Regen Geometry Constraint Validation Owner"


def attach_regen_geometry_constraint_validation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_geometry_constraint_validation_owner(results)
    results.update(payload)
    return results


def build_regen_geometry_constraint_validation_owner(results):
    results = results if isinstance(results, dict) else {}

    evidence = {
        "hot_gas_wall_thickness": _safe_float_or_none(
            results.get("hot_gas_wall_thickness")
            or results.get("candidate_hot_gas_wall_thickness")
            or results.get("wall_thickness")
        ),
        "coolant_channel_width": _safe_float_or_none(
            results.get("coolant_channel_width")
            or results.get("candidate_coolant_channel_width")
            or results.get("channel_width")
        ),
        "coolant_channel_height": _safe_float_or_none(
            results.get("coolant_channel_height")
            or results.get("candidate_coolant_channel_height")
            or results.get("channel_height")
        ),
        "rib_width": _safe_float_or_none(
            results.get("rib_width")
            or results.get("candidate_rib_width")
        ),
        "number_of_coolant_channels": _safe_float_or_none(
            _first_present(
                results,
                (
                    "number_of_coolant_channels",
                    "candidate_number_of_coolant_channels",
                    "n_channels",
                ),
            )
        ),
        "channel_fit_ratio": _safe_float_or_none(
            results.get("viewer_channel_fit_ratio")
            or results.get("channel_fit_ratio")
            or results.get("candidate_channel_fit_ratio")
        ),
        "cooling_coverage": _safe_float_or_none(
            results.get("viewer_cooling_coverage")
            or results.get("cooling_coverage")
            or results.get("candidate_cooling_coverage")
        ),
        "geometry_valid_flag": _as_bool_or_none(
            results.get("viewer_channel_geometry_valid")
            if "viewer_channel_geometry_valid" in results
            else results.get("regen_geometry_valid")
            if "regen_geometry_valid" in results
            else results.get("geometry_valid")
        ),
        "geometry_status": results.get("regen_geometry_status")
        or results.get("geometry_status")
        or results.get("candidate_geometry_status"),
        "overall_status": results.get("regen_overall_status")
        or results.get("overall_status")
        or results.get("candidate_overall_status"),
    }

    rules = _build_geometry_constraint_rules(evidence)

    blocking_rules = [
        rule for rule in rules
        if rule["blocking"] is True
    ]

    warning_rules = [
        rule for rule in rules
        if rule["severity"] == "WARNING" and rule["passed"] is False
    ]

    geometry_constraints_valid = not blocking_rules

    status = (
        "PASS_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
        if geometry_constraints_valid
        else "FAIL_REGEN_GEOMETRY_CONSTRAINT_VALIDATION_OWNER"
    )

    structured_findings = _build_geometry_constraint_findings(
        status=status,
        rules=rules,
        evidence=evidence,
    )

    global_status_payload = classify_status(
        structured_findings,
        production_gate=True,
    )

    report = build_regen_geometry_constraint_validation_report(
        status=status,
        geometry_constraints_valid=geometry_constraints_valid,
        evidence=evidence,
        rules=rules,
        blocking_rules=blocking_rules,
        warning_rules=warning_rules,
        global_status_payload=global_status_payload,
    )

    return {
        "regen_geometry_constraint_validation_owner_status": status,
        "regen_geometry_constraint_validation_owner_complete": True,
        "regen_geometry_constraint_validation_pass": geometry_constraints_valid,
        "regen_geometry_constraint_validation_evidence": evidence,
        "regen_geometry_constraint_validation_rules": rules,
        "regen_geometry_constraint_validation_blocking_rules": blocking_rules,
        "regen_geometry_constraint_validation_warning_rules": warning_rules,
        "regen_geometry_constraint_validation_blocking_rule_count": len(blocking_rules),
        "regen_geometry_constraint_validation_warning_rule_count": len(warning_rules),
        "regen_geometry_constraint_validation_structured_findings": structured_findings,
        "regen_geometry_constraint_validation_global_status": global_status_payload["status"],
        "regen_geometry_constraint_validation_global_status_payload": global_status_payload,
        "regen_geometry_constraint_validation_report": report,
        "phase_16t3k12_status_adapter_complete": True,
    }


def _build_geometry_constraint_rules(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    rules = []

    dimension_keys = [
        "hot_gas_wall_thickness",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
    ]

    for key in dimension_keys:
        value = evidence.get(key)

        rules.append(_rule(
            rule_id=f"GEOM-CONSTRAINT-{key.upper()}-AVAILABLE",
            passed=value is not None,
            severity="FAIL",
            reason=f"{key} must be available for geometry constraint validation.",
            corrective_action=f"Provide {key} before accepting regen geometry.",
        ))

        if value is not None:
            rules.append(_rule(
                rule_id=f"GEOM-CONSTRAINT-{key.upper()}-POSITIVE",
                passed=value > 0,
                severity="FAIL",
                reason=f"{key} must be positive; got {value}.",
                corrective_action=f"Repair regen geometry because {key} is not physically valid.",
            ))

    n_channels = evidence.get("number_of_coolant_channels")

    rules.append(_rule(
        rule_id="GEOM-CONSTRAINT-CHANNEL-COUNT-AVAILABLE",
        passed=n_channels is not None,
        severity="FAIL",
        reason="number_of_coolant_channels must be available.",
        corrective_action="Provide channel count before accepting regen geometry.",
    ))

    if n_channels is not None:
        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-CHANNEL-COUNT-POSITIVE",
            passed=n_channels > 0,
            severity="FAIL",
            reason=f"number_of_coolant_channels must be positive; got {n_channels}.",
            corrective_action="Repair channel count before accepting regen geometry.",
        ))

        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-CHANNEL-COUNT-INTEGER-LIKE",
            passed=abs(n_channels - round(n_channels)) < 1e-9,
            severity="FAIL",
            reason=f"number_of_coolant_channels must be integer-like; got {n_channels}.",
            corrective_action="Use an integer channel count.",
        ))

    fit_ratio = evidence.get("channel_fit_ratio")

    if fit_ratio is not None:
        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-FIT-RATIO-MAX",
            passed=fit_ratio <= 1.0,
            severity="FAIL",
            reason=f"channel_fit_ratio exceeds available circumference envelope; got {fit_ratio}.",
            corrective_action="Reduce channel width/count/rib or increase available circumference.",
        ))

        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-FIT-RATIO-LOW-WARNING",
            passed=fit_ratio >= 0.25,
            severity="WARNING",
            reason=f"channel_fit_ratio is very low; geometry may be under-utilising available circumference: {fit_ratio}.",
            corrective_action="Review channel count/width/rib balance for manufacturability and cooling coverage.",
        ))

    coverage = evidence.get("cooling_coverage")

    if coverage is not None:
        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-COOLING-COVERAGE-RANGE",
            passed=0.0 <= coverage <= 1.0,
            severity="FAIL",
            reason=f"cooling_coverage must be between 0 and 1; got {coverage}.",
            corrective_action="Repair cooling coverage calculation or geometry inputs.",
        ))

        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-COOLING-COVERAGE-WARNING",
            passed=coverage >= 0.5,
            severity="WARNING",
            reason=f"cooling_coverage is below review threshold: {coverage}.",
            corrective_action="Review whether cooling coverage is sufficient for the design.",
        ))

    geometry_valid_flag = evidence.get("geometry_valid_flag")

    if geometry_valid_flag is not None:
        rules.append(_rule(
            rule_id="GEOM-CONSTRAINT-GEOMETRY-VALID-FLAG",
            passed=geometry_valid_flag is True,
            severity="FAIL",
            reason=f"geometry_valid flag is not passing: {geometry_valid_flag}.",
            corrective_action="Repair geometry before acceptance.",
        ))

    for key in ("geometry_status", "overall_status"):
        value = evidence.get(key)

        if value is None:
            continue

        text = str(value).upper()

        rules.append(_rule(
            rule_id=f"GEOM-CONSTRAINT-{key.upper()}-NO-FAIL",
            passed=("FAIL" not in text and "INVALID" not in text),
            severity="FAIL",
            reason=f"{key} reports non-passing geometry state: {value}.",
            corrective_action="Repair failing geometry subsystem before acceptance.",
        ))

        rules.append(_rule(
            rule_id=f"GEOM-CONSTRAINT-{key.upper()}-NO-WARN",
            passed=("WARN" not in text and "REVIEW" not in text and "PLACEHOLDER" not in text),
            severity="WARNING",
            reason=f"{key} requires review before production sign-off: {value}.",
            corrective_action="Resolve or explicitly review geometry warning before production sign-off.",
        ))

    return rules


def _build_geometry_constraint_findings(status, rules, evidence):
    findings = []

    for rule in rules:
        if rule["passed"]:
            continue

        findings.append(
            make_finding(
                message=rule["reason"],
                category=_category_for_rule(rule),
                owner=OWNER,
                evidence={
                    **evidence,
                    "rule_id": rule["rule_id"],
                    "corrective_action": rule["corrective_action"],
                    "legacy_rule_severity": rule["severity"],
                    "owner_status": status,
                },
            )
        )

    if not findings:
        findings.append(
            make_finding(
                message="Regen geometry constraint validation completed successfully.",
                category="COMPLETE",
                owner=OWNER,
                evidence={**evidence, "owner_status": status},
            )
        )

    return findings


def _category_for_rule(rule: dict[str, Any]) -> str:
    rule_id = rule["rule_id"]
    severity = rule["severity"]

    if "AVAILABLE" in rule_id:
        return "VALIDATION_INCOMPLETE"

    if (
        "POSITIVE" in rule_id
        or "RANGE" in rule_id
        or "FIT-RATIO-MAX" in rule_id
        or "CHANNEL-COUNT-INTEGER-LIKE" in rule_id
    ):
        return "PHYSICS_INVALID"

    if "NO-FAIL" in rule_id or "VALID-FLAG" in rule_id:
        return "PHYSICS_INVALID"

    if severity == "WARNING":
        return "MANUAL_REVIEW_REQUIRED"

    return "VALIDATION_FAILURE"


def build_regen_geometry_constraint_validation_report(
    status,
    geometry_constraints_valid,
    evidence,
    rules,
    blocking_rules,
    warning_rules,
    global_status_payload=None,
):
    lines = [
        "LEAF PHASE 16T.3K.12 — REGEN GEOMETRY CONSTRAINT VALIDATION OWNER",
        "==================================================================",
        "",
        f"Status: {status}",
        f"Geometry constraints valid: {geometry_constraints_valid}",
        f"Blocking rule count: {len(blocking_rules)}",
        f"Warning rule count: {len(warning_rules)}",
        "",
        "Evidence:",
    ]

    for key, value in evidence.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "Validation Rules:"])

    for rule in rules:
        lines.append("")
        lines.append(f"- Rule ID: {rule['rule_id']}")
        lines.append(f"  Passed: {rule['passed']}")
        lines.append(f"  Severity: {rule['severity']}")
        lines.append(f"  Blocking: {rule['blocking']}")
        lines.append(f"  Reason: {rule['reason']}")
        lines.append(f"  Corrective Action: {rule['corrective_action']}")

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
        "- Regen geometry must be physically valid before candidate acceptance.",
        "- Missing geometry blocks production sign-off.",
        "- Negative or impossible geometry fails through the global status engine.",
        "- Warning-only geometry states block production sign-off until reviewed.",
        "- Legacy geometry constraint validation status remains available.",
    ])

    return "\n".join(lines)


def _rule(rule_id, passed, severity, reason, corrective_action):
    severity = str(severity).upper()

    return {
        "rule_id": rule_id,
        "passed": bool(passed),
        "severity": severity,
        "blocking": (not bool(passed)) and severity == "FAIL",
        "reason": reason,
        "corrective_action": corrective_action,
    }



def _first_present(results, keys):
    for key in keys:
        if key in results:
            return results.get(key)
    return None

def _safe_float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_bool_or_none(value):
    if value is None:
        return None
    return bool(value)
