"""
PHASE 16J.8 — Optimisation Completion Gate

Final gate for the current regen optimisation/recommendation/acceptance pipeline.
Does not modify geometry.
Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_OPTIMISATION_COMPLETION_GATE_PHASE_16J8"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_COMPLETION_GATE_PHASE_16J8"

REQUIRED_PHASES = (
    "phase_16j3f_complete",
    "phase_16j3g_complete",
    "phase_16j3h_complete",
    "phase_16j4_complete",
    "phase_16j4b_complete",
    "phase_16j4c_complete",
    "phase_16j4d_complete",
    "phase_16j4e_complete",
    "phase_16j4f_complete",
    "phase_16j4g_complete",
    "phase_16j5_complete",
    "phase_16j6_complete",
    "phase_16j7_complete",
)

REQUIRED_FINAL_PAYLOADS = (
    "regen_candidate_acceptance_completion_gate_payload",
    "regen_recommendation_explanation_payload",
    "regen_failure_root_cause_payload",
    "regen_optimisation_proof_payload",
)


def attach_regen_optimisation_completion_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for phase in REQUIRED_PHASES:
        if results.get(phase) is not True:
            blockers.append(f"Required phase incomplete: {phase}")

    for key in REQUIRED_FINAL_PAYLOADS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required final payload missing: {key}")

    proof = results.get("regen_optimisation_proof_payload")
    trust_score = results.get("regen_optimisation_proof_trust_score")

    if not isinstance(proof, dict):
        blockers.append("Optimisation proof payload is not available.")
    elif proof.get("proof_state") != "OPTIMISATION_CHAIN_PROVEN":
        blockers.append("Optimisation proof state is not OPTIMISATION_CHAIN_PROVEN.")

    if trust_score != 1.0:
        blockers.append(f"Optimisation trust score is not 1.0: {trust_score}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "completion_state": "REGEN_OPTIMISATION_PIPELINE_COMPLETE",
            "visibility": "REPORT_ONLY",
            "source_phase": "16J.8",
            "candidate_id": proof.get("candidate_id"),
            "trust_score": trust_score,
            "completed_phases": list(REQUIRED_PHASES),
            "final_payloads": list(REQUIRED_FINAL_PAYLOADS),
            "next_phase": "16K Regen Viewer Completion / UI Integration",
        }

    report = _build_report(status, blockers, payload)

    results["regen_optimisation_completion_gate_complete"] = True
    results["phase_16j8_complete"] = status == PASS_STATUS
    results["regen_optimisation_completion_gate_status"] = status
    results["phase_16j8_status"] = status
    results["regen_optimisation_completion_gate_blockers"] = blockers
    results["regen_optimisation_completion_gate_payload"] = payload
    results["regen_optimisation_completion_gate_report"] = report
    results["regen_optimisation_pipeline_complete"] = status == PASS_STATUS

    results["phase_16k_regen_viewer_completion_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16J.8 OPTIMISATION COMPLETION GATE",
        "================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Final audit for the optimisation/recommendation/acceptance pipeline.",
        "- Confirms proof, explanation, root-cause, acceptance, commit, and regeneration ownership.",
        "- Produces final completion payload.",
        "- Does not modify geometry.",
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
        f"- Pipeline complete: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Trust score: {(payload or {}).get('trust_score')}",
        "- Visibility: REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16K Regen Viewer Completion / UI Integration.",
    ])

    return "\n".join(lines)
