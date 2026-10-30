"""
PHASE 16L.4 — Acceptance Master Gate

Final gate for the Regen Acceptance Framework.
"""

PASS_STATUS = "PASS_REGEN_ACCEPTANCE_MASTER_GATE_PHASE_16L4"
FAIL_STATUS = "FAIL_REGEN_ACCEPTANCE_MASTER_GATE_PHASE_16L4"

REQUIRED_PHASES = (
    "phase_16l1_complete",
    "phase_16l2_complete",
    "phase_16l3_complete",
)

REQUIRED_PAYLOADS = (
    "regen_acceptance_criteria_payload",
    "regen_engineering_acceptance_report_payload",
    "regen_acceptance_audit_payload",
)


def attach_regen_acceptance_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for phase in REQUIRED_PHASES:
        if results.get(phase) is not True:
            blockers.append(f"Required acceptance phase incomplete: {phase}")

    for key in REQUIRED_PAYLOADS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required acceptance payload missing: {key}")

    criteria = results.get("regen_acceptance_criteria_payload") or {}
    report_payload = results.get("regen_engineering_acceptance_report_payload") or {}
    audit = results.get("regen_acceptance_audit_payload") or {}

    if criteria.get("failed_count") != 0:
        blockers.append("Acceptance criteria contain failures.")

    if report_payload.get("readiness") != "ENGINEERING_ACCEPTANCE_READY":
        blockers.append("Engineering acceptance readiness is not ready.")

    if audit.get("failed_count") != 0:
        blockers.append("Acceptance audit contains failures.")

    candidate_ids = [
        criteria.get("candidate_id"),
        report_payload.get("candidate_id"),
        audit.get("candidate_id"),
    ]
    candidate_ids = [c for c in candidate_ids if c]

    if candidate_ids and len(set(candidate_ids)) != 1:
        blockers.append(f"Acceptance candidate ID mismatch: {candidate_ids}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "completion_state": "REGEN_ACCEPTANCE_FRAMEWORK_COMPLETE",
            "candidate_id": candidate_ids[0] if candidate_ids else report_payload.get("candidate_id"),
            "visibility": "REPORT_ONLY",
            "source_phase": "16L.4",
            "completed_phases": list(REQUIRED_PHASES),
            "verified_payloads": list(REQUIRED_PAYLOADS),
            "next_phase": "16M Final Regen Sign-Off Framework",
        }

    report = _build_report(status, blockers, payload)

    results["regen_acceptance_master_gate_complete"] = True
    results["phase_16l4_complete"] = status == PASS_STATUS
    results["regen_acceptance_master_gate_status"] = status
    results["phase_16l4_status"] = status
    results["regen_acceptance_master_gate_blockers"] = blockers
    results["regen_acceptance_master_gate_payload"] = payload
    results["regen_acceptance_master_gate_report"] = report
    results["regen_acceptance_framework_complete"] = status == PASS_STATUS

    results["phase_16m_final_regen_signoff_framework_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.4 ACCEPTANCE MASTER GATE",
        "========================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Final gate for regen acceptance framework.",
        "- Confirms acceptance criteria, engineering report, and audit.",
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
        "Gate Result:",
        f"- Acceptance framework complete: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        "- Visibility: REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16M Final Regen Sign-Off Framework.",
    ])

    return "\n".join(lines)
