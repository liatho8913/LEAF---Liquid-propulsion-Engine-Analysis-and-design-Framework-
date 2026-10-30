"""
PHASE 16M.1 — Final Regen Completion Audit

Purpose:
- Audit completed regen optimisation, viewer, and acceptance frameworks.
- Start final regen sign-off framework.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_FINAL_COMPLETION_AUDIT_PHASE_16M1"
FAIL_STATUS = "FAIL_REGEN_FINAL_COMPLETION_AUDIT_PHASE_16M1"

REQUIRED_COMPLETION_FLAGS = (
    "regen_optimisation_pipeline_complete",
    "regen_viewer_system_complete",
    "regen_acceptance_framework_complete",
)

REQUIRED_MASTER_PAYLOADS = (
    "regen_optimisation_completion_gate_payload",
    "regen_viewer_completion_gate_payload",
    "regen_acceptance_master_gate_payload",
)


def attach_regen_final_completion_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16l4_complete") is not True:
        blockers.append("Phase 16L.4 acceptance master gate has not passed.")

    for flag in REQUIRED_COMPLETION_FLAGS:
        if results.get(flag) is not True:
            blockers.append(f"Required completion flag missing or false: {flag}")

    for key in REQUIRED_MASTER_PAYLOADS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required master payload missing: {key}")

    candidate_ids = _candidate_ids(results)

    if candidate_ids and len(set(candidate_ids)) != 1:
        blockers.append(f"Candidate ID mismatch across final regen completion audit: {candidate_ids}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16M.1",
            "visibility": "REPORT_ONLY",
            "candidate_id": candidate_ids[0] if candidate_ids else None,
            "completion_state": "FINAL_REGEN_COMPLETION_AUDIT_PASS",
            "verified_completion_flags": list(REQUIRED_COMPLETION_FLAGS),
            "verified_master_payloads": list(REQUIRED_MASTER_PAYLOADS),
            "next_phase": "16M.2 Final Regen Verification Audit",
        }

    report = _build_report(status, blockers, payload)

    results["regen_final_completion_audit_complete"] = True
    results["phase_16m1_complete"] = status == PASS_STATUS
    results["regen_final_completion_audit_status"] = status
    results["phase_16m1_status"] = status
    results["regen_final_completion_audit_blockers"] = blockers
    results["regen_final_completion_audit_payload"] = payload
    results["regen_final_completion_audit_report"] = report

    results["phase_16m2_final_regen_verification_audit_allowed"] = status == PASS_STATUS

    return results


def _candidate_ids(results):
    ids = []

    for key in REQUIRED_MASTER_PAYLOADS:
        payload = results.get(key)
        if isinstance(payload, dict) and payload.get("candidate_id"):
            ids.append(payload.get("candidate_id"))

    return ids


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16M.1 FINAL REGEN COMPLETION AUDIT",
        "==============================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Audits optimisation completion.",
        "- Audits viewer completion.",
        "- Audits acceptance framework completion.",
        "- Starts final regen sign-off framework.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Audit Result:",
        f"- Complete: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Completion state: {(payload or {}).get('completion_state')}",
        "",
        "Next Required Phase:",
        "- 16M.2 Final Regen Verification Audit.",
    ])

    return "\n".join(lines)
