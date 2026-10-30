"""
PHASE 16M.4 — Final Regen Master Gate

Final software-system sign-off gate for the LEAF regen system.
"""

PASS_STATUS = "PASS_REGEN_FINAL_MASTER_GATE_PHASE_16M4"
FAIL_STATUS = "FAIL_REGEN_FINAL_MASTER_GATE_PHASE_16M4"

REQUIRED_PHASES = (
    "phase_16j8_complete",
    "phase_16k7_complete",
    "phase_16l4_complete",
    "phase_16m1_complete",
    "phase_16m2_complete",
    "phase_16m3_complete",
)

REQUIRED_PAYLOADS = (
    "regen_optimisation_completion_gate_payload",
    "regen_viewer_completion_gate_payload",
    "regen_acceptance_master_gate_payload",
    "regen_final_completion_audit_payload",
    "regen_final_verification_audit_payload",
    "regen_final_signoff_report_payload",
)


def attach_regen_final_master_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for phase in REQUIRED_PHASES:
        if results.get(phase) is not True:
            blockers.append(f"Required final phase incomplete: {phase}")

    for key in REQUIRED_PAYLOADS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required final payload missing: {key}")

    signoff = results.get("regen_final_signoff_report_payload") or {}

    if signoff.get("signoff_report_state") != "FINAL_REGEN_SIGNOFF_REPORT_READY":
        blockers.append("Final sign-off report is not ready.")

    candidate_ids = []
    for key in REQUIRED_PAYLOADS:
        payload = results.get(key)
        if isinstance(payload, dict) and payload.get("candidate_id"):
            candidate_ids.append(payload.get("candidate_id"))

    if candidate_ids and len(set(candidate_ids)) != 1:
        blockers.append(f"Candidate ID mismatch in final master gate: {candidate_ids}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "completion_state": "REGEN_SOFTWARE_SYSTEM_SIGNED_OFF",
            "candidate_id": candidate_ids[0] if candidate_ids else None,
            "visibility": "REPORT_ONLY",
            "source_phase": "16M.4",
            "signed_off_systems": [
                "regen_optimisation_pipeline",
                "regen_viewer_system",
                "regen_acceptance_framework",
                "regen_final_completion_audit",
                "regen_final_verification_audit",
                "regen_final_signoff_report",
            ],
            "important_limit": (
                "This is LEAF software-system regen sign-off. "
                "It is not physical hot-fire certification, flight certification, "
                "or manufacturing release."
            ),
            "next_phase": "Post-Regen Roadmap Selection",
        }

    report = _build_report(status, blockers, payload)

    results["regen_final_master_gate_complete"] = True
    results["phase_16m4_complete"] = status == PASS_STATUS
    results["regen_final_master_gate_status"] = status
    results["phase_16m4_status"] = status
    results["regen_final_master_gate_blockers"] = blockers
    results["regen_final_master_gate_payload"] = payload
    results["regen_final_master_gate_report"] = report

    results["regen_system_signed_off"] = status == PASS_STATUS
    results["regen_software_system_complete"] = status == PASS_STATUS

    results["phase_post_regen_roadmap_selection_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16M.4 FINAL REGEN MASTER GATE",
        "=========================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Final software-system sign-off gate for regen.",
        "- Confirms optimisation, viewer, acceptance, completion audit, verification audit, and sign-off report.",
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
        "Final Gate Result:",
        f"- Regen signed off: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Completion state: {(payload or {}).get('completion_state')}",
        "",
        "Important Limit:",
        f"- {(payload or {}).get('important_limit')}",
        "",
        "Next Required Phase:",
        "- Post-Regen Roadmap Selection.",
    ])

    return "\n".join(lines)
