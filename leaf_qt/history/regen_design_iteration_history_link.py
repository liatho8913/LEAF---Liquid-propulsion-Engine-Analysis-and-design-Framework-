"""
PHASE 16J.4F — Design Iteration History Link

Purpose:
- Link recommendation, acceptance, commit, regeneration, and comparison reports
  into one design iteration event.
- Preserve explainability:
  what changed, why it changed, whether it improved/regressed, and what phase did it.
- Does not modify geometry.
- Does not rerun solver.
"""

from datetime import datetime, timezone

PASS_STATUS = "PASS_REGEN_DESIGN_ITERATION_HISTORY_LINK_PHASE_16J4F"
FAIL_STATUS = "FAIL_REGEN_DESIGN_ITERATION_HISTORY_LINK_PHASE_16J4F"


def attach_regen_design_iteration_history_link(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j4e_complete") is not True:
        blockers.append("Phase 16J.4E before/after report ownership has not passed.")

    recommendation = results.get("regen_recommendation_viewer_payload")
    acceptance = results.get("regen_candidate_acceptance_history_event")
    commit = results.get("regen_live_geometry_commit_audit_record")
    regen = results.get("regen_solver_regeneration_audit_record")
    comparison = results.get("regen_before_after_solver_comparison_report_payload")
    summary = results.get("regen_before_after_solver_comparison_summary")

    required = {
        "recommendation viewer payload": recommendation,
        "acceptance history event": acceptance,
        "live geometry commit audit": commit,
        "solver regeneration audit": regen,
        "before/after comparison report payload": comparison,
        "before/after comparison summary": summary,
    }

    for name, payload in required.items():
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name}.")

    candidate_id = _candidate_id(results, recommendation, acceptance, commit, regen, comparison)

    if not candidate_id:
        blockers.append("Candidate ID could not be resolved for design iteration history.")

    event = None

    if not blockers:
        event = {
            "event_type": "REGEN_DESIGN_ITERATION_COMPLETED",
            "phase": "16J.4F",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_id": candidate_id,
            "iteration_title": f"Accepted regen candidate {candidate_id}",
            "chain": [
                "16J.3F Recommendation Feed Repair",
                "16J.3G Recommendation Viewer Repair",
                "16J.3H End-to-End Selection Validation",
                "16J.4 Candidate Acceptance Integration",
                "16J.4B Pending Geometry Commit Validation",
                "16J.4C Live Geometry Commit Execution",
                "16J.4D Solver Regeneration After Commit",
                "16J.4E Before/After Solver Comparison Report Ownership",
            ],
            "recommendation_reasoning": recommendation.get("reasoning"),
            "acceptance_summary": acceptance.get("summary"),
            "commit_summary": {
                "committed_keys": commit.get("committed_keys"),
                "before_after": commit.get("before_after"),
            },
            "solver_regeneration_status": regen.get("status"),
            "comparison_summary": summary,
            "classified_changes": comparison.get("classified_changes"),
            "visibility": "REPORT_ONLY",
            "geometry_application_state": "COMMITTED_AND_REGENERATED",
        }

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report = _build_report(status, blockers, event)

    existing_history = results.get("regen_design_iteration_history")
    if not isinstance(existing_history, list):
        existing_history = []

    if event:
        existing_history = existing_history + [event]

    results["regen_design_iteration_history_link_complete"] = True
    results["phase_16j4f_complete"] = status == PASS_STATUS
    results["regen_design_iteration_history_link_status"] = status
    results["phase_16j4f_status"] = status
    results["regen_design_iteration_history_link_blockers"] = blockers
    results["regen_design_iteration_history_event"] = event
    results["regen_design_iteration_history"] = existing_history
    results["regen_design_iteration_history_report"] = report
    results["regen_design_iteration_history_visibility"] = "REPORT_ONLY"

    results["phase_16j4g_candidate_acceptance_completion_gate_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _candidate_id(results, *payloads):
    for payload in payloads:
        if isinstance(payload, dict):
            value = payload.get("candidate_id")
            if value:
                return value

    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        value = results.get(key)
        if value:
            return value

    return None


def _build_report(status, blockers, event):
    lines = [
        "LEAF PHASE 16J.4F DESIGN ITERATION HISTORY LINK",
        "==================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Links recommendation, acceptance, commit, regeneration, and comparison into one history event.",
        "- Records what changed and why.",
        "- Records whether solver outputs improved or regressed.",
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

    if event:
        lines.extend([
            "",
            "Design Iteration Event:",
            f"- Candidate ID: {event.get('candidate_id')}",
            f"- Event type: {event.get('event_type')}",
            f"- Geometry state: {event.get('geometry_application_state')}",
            "",
            "Comparison Summary:",
        ])

        summary = event.get("comparison_summary") or {}
        for key in ("changed", "improved", "regressed", "neutral_changed", "unchanged"):
            lines.append(f"- {key}: {summary.get(key)}")

    lines.extend([
        "",
        "Visibility:",
        "- REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.4G Candidate Acceptance Completion Gate.",
    ])

    return "\n".join(lines)
