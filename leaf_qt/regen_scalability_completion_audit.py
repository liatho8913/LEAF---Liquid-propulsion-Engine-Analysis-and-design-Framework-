"""
LEAF Regen Scalability Completion Audit
=======================================

Stage V.5 architectural completion audit for regen scalability.

This module signs off the Stage V architecture only when:

- Stage V.0 profile owner is complete
- Stage V.1 constraint owner/framework is complete
- Stage V.2 report owner is complete
- Stage V.3 failure owner is complete
- Stage V.4 master gate is complete

This is not real-engine benchmarking.
That belongs to Stage W.
"""


def attach_regen_scalability_completion_audit(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_regen_scalability_completion_audit(results)
    results.update(audit)
    return results


def evaluate_regen_scalability_completion_audit(results):
    results = results if isinstance(results, dict) else {}

    checks = {
        "stage_v0_regen_scalability_profile_complete": bool(
            results.get("stage_v0_regen_scalability_profile_complete", False)
        ),
        "stage_v1_regen_scalability_constraint_owner_complete": bool(
            results.get("stage_v1_regen_scalability_constraint_owner_complete")
            or results.get("stage_v1_regen_scalability_framework_complete")
            or False
        ),
        "stage_v2_regen_scalability_report_owner_complete": bool(
            results.get("stage_v2_regen_scalability_report_owner_complete")
            or results.get("stage_v2_regen_scalability_report_ownership_complete")
            or False
        ),
        "stage_v3_regen_scalability_failure_owner_complete": bool(
            results.get("stage_v3_regen_scalability_failure_owner_complete", False)
        ),
        "stage_v4_regen_scalability_master_gate_complete": bool(
            results.get("stage_v4_regen_scalability_master_gate_complete", False)
        ),
    }

    missing = [
        key for key, passed in checks.items()
        if not passed
    ]

    master_gate_status = str(
        results.get("regen_scalability_master_gate_status", "UNKNOWN")
    ).upper()

    blocking_reasons = []

    for key in missing:
        blocking_reasons.append(f"Required Stage V completion key is false: {key}")

    if master_gate_status != "PASS_REGEN_SCALABILITY_MASTER_GATE":
        blocking_reasons.append(
            f"Scalability master gate did not pass: {master_gate_status}"
        )

    if blocking_reasons:
        status = "FAIL_REGEN_SCALABILITY_COMPLETION_AUDIT"
        complete = False
    else:
        status = "PASS_REGEN_SCALABILITY_COMPLETION_AUDIT"
        complete = True

    text = build_regen_scalability_completion_audit_text(
        status=status,
        complete=complete,
        checks=checks,
        missing=missing,
        master_gate_status=master_gate_status,
        blocking_reasons=blocking_reasons,
        results=results,
    )

    return {
        "regen_scalability_completion_audit_status": status,
        "regen_scalability_completion_audit_complete": complete,
        "regen_scalability_completion_audit_checks": checks,
        "regen_scalability_completion_audit_missing": missing,
        "regen_scalability_completion_audit_blocking_reasons": blocking_reasons,
        "regen_scalability_completion_audit_text": text,

        # Stage V.5 owned key.
        "stage_v5_regen_scalability_completion_audit_complete": complete,

        # Backward-compatible / harness-facing keys.
        "stage_v_regen_scalability_complete": complete,
        "stage_v_regen_scalability_completion_audit_complete": complete,
        "stage_v_regen_scalability_completion_complete": complete,
        "stage_v_regen_scalability_architecture_complete": complete,
        "stage_v_scalability_complete": complete,
        "stage_v_complete": complete,
    }


def build_regen_scalability_completion_audit_text(
    status,
    complete,
    checks,
    missing,
    master_gate_status,
    blocking_reasons,
    results,
):
    lines = [
        "LEAF STAGE V.5 REGEN SCALABILITY COMPLETION AUDIT",
        "==================================================",
        "",
        f"Status: {status}",
        f"Complete: {complete}",
        "",
        "Owned By:",
        "- regen_scalability_completion_audit.py",
        "",
        "Scope:",
        "- Owns architectural Stage V completion signoff.",
        "- Does not benchmark real engines.",
        "- Does not optimise geometry.",
        "",
        "Stage V Completion Checks:",
    ]

    for key, passed in checks.items():
        lines.append(f"- {key}: {passed}")

    lines.append("")
    lines.append("Master Gate:")
    lines.append(f"- {master_gate_status}")

    lines.append("")
    lines.append("Missing / False Completion Keys:")
    lines.extend([f"- {item}" for item in missing] or ["- None."])

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Upstream Status Evidence:")
    lines.append(
        f"- Stage V.0 profile: {results.get('regen_scalability_profile_status', 'N/A')}"
    )
    lines.append(
        f"- Stage V.1 constraint: {results.get('regen_scalability_constraint_owner_status', results.get('regen_scalability_framework_status', 'N/A'))}"
    )
    lines.append(
        f"- Stage V.2 report: {results.get('regen_scalability_report_owner_status', 'N/A')}"
    )
    lines.append(
        f"- Stage V.3 failure owner: {results.get('regen_scalability_failure_owner_status', 'N/A')}"
    )
    lines.append(
        f"- Stage V.4 master gate: {results.get('regen_scalability_master_gate_status', 'N/A')}"
    )

    lines.append("")
    lines.append("Rule:")
    lines.append("- Stage V is complete only when the full V.0–V.5 chain passes.")
    lines.append("- Stage W benchmarking remains separate and downstream.")
    lines.append("- Warning or blocked scalability cases must fail this audit.")

    return "\n".join(lines)