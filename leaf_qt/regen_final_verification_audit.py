"""
PHASE 16M.2 — Final Regen Verification Audit

Purpose:
- Verify final regen completion audit evidence.
- Confirm final reports, proof, acceptance, viewer, and optimisation payloads exist.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_FINAL_VERIFICATION_AUDIT_PHASE_16M2"
FAIL_STATUS = "FAIL_REGEN_FINAL_VERIFICATION_AUDIT_PHASE_16M2"

REQUIRED_PHASE_FLAGS = (
    "phase_16m1_complete",
    "phase_16l4_complete",
    "phase_16k7_complete",
    "phase_16j8_complete",
)

REQUIRED_EVIDENCE_KEYS = (
    "regen_final_completion_audit_payload",
    "regen_acceptance_master_gate_payload",
    "regen_viewer_completion_gate_payload",
    "regen_optimisation_completion_gate_payload",
    "regen_optimisation_proof_payload",
    "regen_engineering_acceptance_report_payload",
    "regen_viewer_rendered_report",
)


def attach_regen_final_verification_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for flag in REQUIRED_PHASE_FLAGS:
        if results.get(flag) is not True:
            blockers.append(f"Required final verification phase incomplete: {flag}")

    for key in REQUIRED_EVIDENCE_KEYS:
        value = results.get(key)
        if value is None or value == {} or value == []:
            blockers.append(f"Required final verification evidence missing: {key}")

    proof = results.get("regen_optimisation_proof_payload") or {}
    if proof.get("proof_state") != "OPTIMISATION_CHAIN_PROVEN":
        blockers.append("Optimisation proof state is not proven.")

    acceptance = results.get("regen_acceptance_master_gate_payload") or {}
    if acceptance.get("completion_state") != "REGEN_ACCEPTANCE_FRAMEWORK_COMPLETE":
        blockers.append("Acceptance framework is not complete.")

    viewer = results.get("regen_viewer_completion_gate_payload") or {}
    if viewer.get("completion_state") != "REGEN_VIEWER_COMPLETE":
        blockers.append("Viewer system is not complete.")

    completion = results.get("regen_final_completion_audit_payload") or {}
    if completion.get("completion_state") != "FINAL_REGEN_COMPLETION_AUDIT_PASS":
        blockers.append("Final completion audit did not pass.")

    candidate_ids = _candidate_ids(results)
    if candidate_ids and len(set(candidate_ids)) != 1:
        blockers.append(f"Candidate ID mismatch during final verification: {candidate_ids}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16M.2",
            "visibility": "REPORT_ONLY",
            "candidate_id": candidate_ids[0] if candidate_ids else None,
            "verification_state": "FINAL_REGEN_VERIFICATION_AUDIT_PASS",
            "verified_phase_flags": list(REQUIRED_PHASE_FLAGS),
            "verified_evidence_keys": list(REQUIRED_EVIDENCE_KEYS),
            "next_phase": "16M.3 Final Regen Sign-Off Report",
        }

    report = _build_report(status, blockers, payload)

    results["regen_final_verification_audit_complete"] = True
    results["phase_16m2_complete"] = status == PASS_STATUS
    results["regen_final_verification_audit_status"] = status
    results["phase_16m2_status"] = status
    results["regen_final_verification_audit_blockers"] = blockers
    results["regen_final_verification_audit_payload"] = payload
    results["regen_final_verification_audit_report"] = report

    results["phase_16m3_final_regen_signoff_report_allowed"] = status == PASS_STATUS

    return results


def _candidate_ids(results):
    ids = []
    for key in (
        "regen_final_completion_audit_payload",
        "regen_acceptance_master_gate_payload",
        "regen_viewer_completion_gate_payload",
        "regen_optimisation_completion_gate_payload",
        "regen_optimisation_proof_payload",
        "regen_engineering_acceptance_report_payload",
    ):
        payload = results.get(key)
        if isinstance(payload, dict) and payload.get("candidate_id"):
            ids.append(payload.get("candidate_id"))
    return ids


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16M.2 FINAL REGEN VERIFICATION AUDIT",
        "=================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Verifies final completion audit evidence.",
        "- Confirms optimisation, viewer, acceptance, proof, and reports.",
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
        "Verification Result:",
        f"- Verified: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Verification state: {(payload or {}).get('verification_state')}",
        "",
        "Next Required Phase:",
        "- 16M.3 Final Regen Sign-Off Report.",
    ])

    return "\n".join(lines)
