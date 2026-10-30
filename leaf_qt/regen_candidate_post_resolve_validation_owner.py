"""
PHASE 16T.3K.11
Regen Candidate Post-Resolve Validation Owner

Validates candidate payloads after geometry/results have been resolved.

Adds structured findings and global_status while preserving the legacy
post-resolve validation owner contract.
"""

from __future__ import annotations

from typing import Any

from leaf_qt.global_status_classification_engine import (
    classify_status,
    make_finding,
)


OWNER = "Regen Candidate Post Resolve Validation Owner"


def attach_regen_candidate_post_resolve_validation_owner(results):
    if not isinstance(results, dict):
        return results

    payload = build_regen_candidate_post_resolve_validation_owner(results)
    results.update(payload)
    return results


def build_regen_candidate_post_resolve_validation_owner(results):
    results = results if isinstance(results, dict) else {}

    candidate_id = results.get("candidate_id") or results.get("regen_candidate_id") or "UNKNOWN_CANDIDATE"

    resolved = bool(
        results.get("regen_candidate_resolved")
        or results.get("candidate_resolved")
        or results.get("post_resolve_candidate_resolved")
    )

    selected = bool(
        results.get("winner_selected")
        or results.get("selected")
        or results.get("candidate_selected")
    )

    geometry_valid = _as_bool_or_none(
        results.get("post_resolve_geometry_valid")
        if "post_resolve_geometry_valid" in results
        else results.get("viewer_channel_geometry_valid")
        if "viewer_channel_geometry_valid" in results
        else results.get("regen_geometry_valid")
    )

    solver_valid = _as_bool_or_none(
        results.get("post_resolve_solver_valid")
        if "post_resolve_solver_valid" in results
        else results.get("solver_valid")
        if "solver_valid" in results
        else results.get("regen_solver_valid")
    )

    validation_status = results.get("regen_validation_master_gate_status") or results.get("regen_validation_status")
    geometry_status = results.get("regen_geometry_status")
    overall_status = results.get("regen_overall_status")

    fit_ratio = _safe_float_or_none(
        results.get("viewer_channel_fit_ratio")
        or results.get("channel_fit_ratio")
        or results.get("candidate_channel_fit_ratio")
    )

    wall_thickness = _safe_float_or_none(
        results.get("hot_gas_wall_thickness")
        or results.get("candidate_hot_gas_wall_thickness")
    )

    channel_width = _safe_float_or_none(
        results.get("coolant_channel_width")
        or results.get("candidate_coolant_channel_width")
    )

    channel_height = _safe_float_or_none(
        results.get("coolant_channel_height")
        or results.get("candidate_coolant_channel_height")
    )

    evidence = {
        "candidate_id": candidate_id,
        "resolved": resolved,
        "selected": selected,
        "geometry_valid": geometry_valid,
        "solver_valid": solver_valid,
        "validation_status": validation_status,
        "geometry_status": geometry_status,
        "overall_status": overall_status,
        "fit_ratio": fit_ratio,
        "wall_thickness": wall_thickness,
        "channel_width": channel_width,
        "channel_height": channel_height,
    }

    rules = _build_rules(evidence)
    blocking_rules = [r for r in rules if r["blocking"]]
    warning_rules = [r for r in rules if r["severity"] == "WARNING" and not r["passed"]]

    post_resolve_valid = not blocking_rules

    status = (
        "PASS_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
        if post_resolve_valid
        else "FAIL_REGEN_CANDIDATE_POST_RESOLVE_VALIDATION_OWNER"
    )

    structured_findings = _build_findings(
        status=status,
        rules=rules,
        evidence=evidence,
    )

    global_status_payload = classify_status(
        structured_findings,
        production_gate=True,
    )

    report = build_regen_candidate_post_resolve_validation_report(
        status=status,
        post_resolve_valid=post_resolve_valid,
        evidence=evidence,
        rules=rules,
        blocking_rules=blocking_rules,
        warning_rules=warning_rules,
        global_status_payload=global_status_payload,
    )

    return {
        "regen_candidate_post_resolve_validation_owner_status": status,
        "regen_candidate_post_resolve_validation_owner_complete": True,
        "regen_candidate_post_resolve_validation_pass": post_resolve_valid,
        "regen_candidate_post_resolve_validation_candidate_id": candidate_id,
        "regen_candidate_post_resolve_validation_rules": rules,
        "regen_candidate_post_resolve_validation_blocking_rules": blocking_rules,
        "regen_candidate_post_resolve_validation_warning_rules": warning_rules,
        "regen_candidate_post_resolve_validation_structured_findings": structured_findings,
        "regen_candidate_post_resolve_validation_global_status": global_status_payload["status"],
        "regen_candidate_post_resolve_validation_global_status_payload": global_status_payload,
        "regen_candidate_post_resolve_validation_report": report,
        "phase_16t3k11_status_adapter_complete": True,
    }


def _build_rules(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    rules = []

    rules.append(_rule(
        "POST-RESOLVE-CANDIDATE-RESOLVED",
        evidence["resolved"] is True,
        "FAIL",
        "Candidate must be resolved before post-resolve validation can pass.",
        "Resolve candidate geometry/results before accepting it.",
    ))

    rules.append(_rule(
        "POST-RESOLVE-CANDIDATE-SELECTED",
        evidence["selected"] is True,
        "WARNING",
        "Candidate is not explicitly marked as selected/winner.",
        "Confirm whether this candidate is the intended selected candidate.",
    ))

    rules.append(_rule(
        "POST-RESOLVE-GEOMETRY-VALID",
        evidence["geometry_valid"] is True,
        "FAIL",
        "Resolved candidate geometry is not valid.",
        "Repair candidate geometry or reject the candidate.",
    ))

    rules.append(_rule(
        "POST-RESOLVE-SOLVER-VALID",
        evidence["solver_valid"] is not False,
        "FAIL",
        "Resolved candidate solver state is invalid.",
        "Regenerate solver outputs after candidate resolution.",
    ))

    for key in ("validation_status", "geometry_status", "overall_status"):
        value = evidence.get(key)
        if value is None:
            continue

        text = str(value).upper()

        rules.append(_rule(
            f"POST-RESOLVE-{key.upper()}",
            ("FAIL" not in text and "INVALID" not in text),
            "FAIL",
            f"{key} is non-passing after candidate resolution: {value}",
            "Reject the candidate or repair the subsystem that produced the failing status.",
        ))

        rules.append(_rule(
            f"POST-RESOLVE-{key.upper()}-WARNING",
            ("WARN" not in text and "REVIEW" not in text and "PLACEHOLDER" not in text),
            "WARNING",
            f"{key} requires review after candidate resolution: {value}",
            "Review warning/review status before production sign-off.",
        ))

    if evidence["fit_ratio"] is not None:
        rules.append(_rule(
            "POST-RESOLVE-FIT-RATIO",
            evidence["fit_ratio"] <= 1.0,
            "FAIL",
            f"Candidate channel fit ratio exceeds allowable envelope: {evidence['fit_ratio']}.",
            "Reduce channel count/width/rib or revise geometry.",
        ))

    for key in ("wall_thickness", "channel_width", "channel_height"):
        value = evidence.get(key)
        if value is None:
            continue

        rules.append(_rule(
            f"POST-RESOLVE-{key.upper()}-POSITIVE",
            value > 0,
            "FAIL",
            f"{key} must be positive after resolution; got {value}.",
            "Repair candidate geometry before acceptance.",
        ))

    return rules


def _build_findings(status: str, rules: list[dict[str, Any]], evidence: dict[str, Any]):
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
                message="Regen candidate post-resolve validation completed successfully.",
                category="COMPLETE",
                owner=OWNER,
                evidence={**evidence, "owner_status": status},
            )
        )

    return findings


def _category_for_rule(rule: dict[str, Any]) -> str:
    rule_id = rule["rule_id"]
    severity = rule["severity"]

    if "GEOMETRY" in rule_id or "FIT-RATIO" in rule_id or "POSITIVE" in rule_id:
        return "PHYSICS_INVALID"

    if "WARNING" in rule_id or severity == "WARNING":
        return "MANUAL_REVIEW_REQUIRED"

    if "RESOLVED" in rule_id or "SELECTED" in rule_id:
        return "VALIDATION_INCOMPLETE"

    return "VALIDATION_FAILURE"


def build_regen_candidate_post_resolve_validation_report(
    status,
    post_resolve_valid,
    evidence,
    rules,
    blocking_rules,
    warning_rules,
    global_status_payload=None,
):
    lines = [
        "LEAF PHASE 16T.3K.11 — REGEN CANDIDATE POST-RESOLVE VALIDATION OWNER",
        "======================================================================",
        "",
        f"Status: {status}",
        f"Post-resolve valid: {post_resolve_valid}",
        f"Candidate ID: {evidence.get('candidate_id')}",
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
        "- Candidate acceptance must be checked after resolution, not only before resolution.",
        "- Invalid geometry/physics fails through the global status engine.",
        "- Review/warning states block production sign-off until reviewed.",
        "- Legacy post-resolve validation status remains available.",
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


def _safe_float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_bool_or_none(value):
    if value is None:
        return None
    return bool(value)
