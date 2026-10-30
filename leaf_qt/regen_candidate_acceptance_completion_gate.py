"""
PHASE 16J.4G — Candidate Acceptance Completion Gate

Purpose:
- Audit the full candidate acceptance pipeline.
- Confirm recommendation, acceptance, commit, regeneration, comparison, and history link exist.
- Produce final completion gate status.
- Does not modify geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_CANDIDATE_ACCEPTANCE_COMPLETION_GATE_PHASE_16J4G"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_ACCEPTANCE_COMPLETION_GATE_PHASE_16J4G"

REQUIRED_PHASE_FLAGS = (
    "phase_16j3f_complete",
    "phase_16j3g_complete",
    "phase_16j3h_complete",
    "phase_16j4_complete",
    "phase_16j4b_complete",
    "phase_16j4c_complete",
    "phase_16j4d_complete",
    "phase_16j4e_complete",
    "phase_16j4f_complete",
)

REQUIRED_PAYLOAD_KEYS = (
    "regen_candidate_recommendation",
    "regen_recommendation_viewer_payload",
    "regen_end_to_end_candidate_selection_trace",
    "regen_candidate_acceptance_pending_application_payload",
    "regen_pending_geometry_commit_approval_payload",
    "regen_live_geometry_commit_audit_record",
    "regen_solver_regeneration_audit_record",
    "regen_before_after_solver_comparison_report_payload",
    "regen_design_iteration_history_event",
)


def attach_regen_candidate_acceptance_completion_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for flag in REQUIRED_PHASE_FLAGS:
        if results.get(flag) is not True:
            blockers.append(f"Required phase flag not complete: {flag}")

    for key in REQUIRED_PAYLOAD_KEYS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required payload missing: {key}")

    candidate_ids = _collect_candidate_ids(results)
    resolved_candidate_id = _resolve_candidate_id(candidate_ids)

    if not resolved_candidate_id:
        blockers.append("Could not resolve a candidate ID across the acceptance pipeline.")

    if resolved_candidate_id and len(set(v for v in candidate_ids.values() if v)) != 1:
        blockers.append("Candidate ID mismatch across acceptance pipeline payloads.")

    if results.get("regen_candidate_live_geometry_commit_executed") is not True:
        blockers.append("Live geometry commit was not executed.")

    if results.get("regen_solver_regenerated_after_commit") is not True:
        blockers.append("Solver regeneration after commit was not completed.")

    history = results.get("regen_design_iteration_history")
    if not isinstance(history, list) or len(history) == 0:
        blockers.append("Design iteration history list is missing or empty.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    gate_payload = None
    if status == PASS_STATUS:
        gate_payload = {
            "status": status,
            "candidate_id": resolved_candidate_id,
            "completion_state": "CANDIDATE_ACCEPTANCE_PIPELINE_COMPLETE",
            "verified_chain": list(REQUIRED_PHASE_FLAGS),
            "verified_payloads": list(REQUIRED_PAYLOAD_KEYS),
            "candidate_ids": candidate_ids,
            "visibility": "REPORT_ONLY",
            "next_phase": "16J.5 Recommendation Explanation Engine",
        }

    report = _build_report(status, blockers, gate_payload, candidate_ids)

    results["regen_candidate_acceptance_completion_gate_complete"] = True
    results["phase_16j4g_complete"] = status == PASS_STATUS
    results["regen_candidate_acceptance_completion_gate_status"] = status
    results["phase_16j4g_status"] = status
    results["regen_candidate_acceptance_completion_gate_blockers"] = blockers
    results["regen_candidate_acceptance_completion_gate_payload"] = gate_payload
    results["regen_candidate_acceptance_completion_gate_report"] = report
    results["regen_candidate_acceptance_pipeline_complete"] = status == PASS_STATUS

    results["phase_16j5_recommendation_explanation_engine_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _collect_candidate_ids(results):
    ids = {}

    trace = results.get("regen_end_to_end_candidate_selection_trace")
    if isinstance(trace, dict):
        ids["trace_best"] = trace.get("best_candidate_id")
        ids["trace_selected"] = trace.get("selected_candidate_id")
        ids["trace_recommendation"] = trace.get("recommendation_candidate_id")
        ids["trace_viewer"] = trace.get("viewer_candidate_id")

    for label, key in (
        ("active_geometry", "regen_geometry_active_candidate_id"),
        ("pending_application", "regen_candidate_pending_application_candidate_id"),
    ):
        ids[label] = results.get(key)

    for label, key in (
        ("viewer", "regen_recommendation_viewer_payload"),
        ("acceptance", "regen_candidate_acceptance_history_event"),
        ("commit", "regen_live_geometry_commit_audit_record"),
        ("regeneration", "regen_solver_regeneration_audit_record"),
        ("comparison", "regen_before_after_solver_comparison_report_payload"),
        ("history", "regen_design_iteration_history_event"),
    ):
        payload = results.get(key)
        if isinstance(payload, dict):
            ids[label] = payload.get("candidate_id")

    return ids


def _resolve_candidate_id(candidate_ids):
    for value in candidate_ids.values():
        if value:
            return value
    return None


def _build_report(status, blockers, gate_payload, candidate_ids):
    lines = [
        "LEAF PHASE 16J.4G CANDIDATE ACCEPTANCE COMPLETION GATE",
        "=========================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Audits the full candidate acceptance pipeline.",
        "- Confirms recommendation, viewer, selection, acceptance, commit, regeneration, comparison, and history link.",
        "- Produces final completion gate status.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Candidate ID Trace:",
    ]

    for key, value in candidate_ids.items():
        lines.append(f"- {key}: {value}")

    lines.extend(["", "Blocking Reasons:"])

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Gate Result:",
        f"- Pipeline complete: {bool(gate_payload)}",
        "- Visibility: REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.5 Recommendation Explanation Engine.",
    ])

    return "\n".join(lines)
