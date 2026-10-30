"""
PHASE 16K.7 — Viewer Completion Gate

Final gate for regen viewer completion.
"""

PASS_STATUS = "PASS_REGEN_VIEWER_COMPLETION_GATE_PHASE_16K7"
FAIL_STATUS = "FAIL_REGEN_VIEWER_COMPLETION_GATE_PHASE_16K7"

REQUIRED_PHASES = (
    "phase_16k1_complete",
    "phase_16k2_complete",
    "phase_16k3_complete",
    "phase_16k4_complete",
    "phase_16k5_complete",
    "phase_16k6_complete",
)

REQUIRED_PAYLOADS = (
    "regen_viewer_payload",
    "regen_viewer_rendered_report",
    "regen_viewer_navigation_payload",
    "regen_viewer_master_gate_payload",
    "regen_cross_section_viewer_payload",
    "regen_station_viewer_payload",
)


def attach_regen_viewer_completion_gate(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for phase in REQUIRED_PHASES:
        if results.get(phase) is not True:
            blockers.append(f"Required viewer phase incomplete: {phase}")

    for key in REQUIRED_PAYLOADS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required viewer payload missing: {key}")

    viewer_payload = results.get("regen_viewer_payload") or {}
    cross_payload = results.get("regen_cross_section_viewer_payload") or {}
    station_payload = results.get("regen_station_viewer_payload") or {}

    candidate_ids = [
        viewer_payload.get("candidate_id"),
        cross_payload.get("candidate_id"),
        station_payload.get("candidate_id"),
    ]
    candidate_ids = [c for c in candidate_ids if c]

    if len(set(candidate_ids)) != 1:
        blockers.append(f"Viewer candidate ID mismatch: {candidate_ids}")

    if viewer_payload.get("visibility") != "UI_REPORT_VIEW":
        blockers.append("Main viewer payload visibility is not UI_REPORT_VIEW.")

    if cross_payload.get("visibility") != "UI_REPORT_VIEW":
        blockers.append("Cross-section viewer payload visibility is not UI_REPORT_VIEW.")

    if station_payload.get("visibility") != "UI_REPORT_VIEW":
        blockers.append("Station viewer payload visibility is not UI_REPORT_VIEW.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    completion_payload = None
    if status == PASS_STATUS:
        completion_payload = {
            "status": status,
            "completion_state": "REGEN_VIEWER_COMPLETE",
            "candidate_id": candidate_ids[0],
            "visibility": "UI_REPORT_VIEW",
            "completed_phases": list(REQUIRED_PHASES),
            "verified_payloads": list(REQUIRED_PAYLOADS),
            "viewer_capabilities": [
                "summary_report",
                "recommendation_report",
                "comparison_report",
                "explanation_report",
                "root_cause_report",
                "proof_report",
                "history_report",
                "cross_section_geometry_feed",
                "station_inspection_feed",
            ],
            "next_phase": "16L Regen Acceptance Framework",
        }

    report = _build_report(status, blockers, completion_payload)

    results["regen_viewer_completion_gate_complete"] = True
    results["phase_16k7_complete"] = status == PASS_STATUS
    results["regen_viewer_completion_gate_status"] = status
    results["phase_16k7_status"] = status
    results["regen_viewer_completion_gate_blockers"] = blockers
    results["regen_viewer_completion_gate_payload"] = completion_payload
    results["regen_viewer_completion_gate_report"] = report
    results["regen_viewer_system_complete"] = status == PASS_STATUS

    results["phase_16l_regen_acceptance_framework_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16K.7 VIEWER COMPLETION GATE",
        "========================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Final audit for regen viewer completion.",
        "- Confirms viewer data adapter, renderer, navigation, ownership, cross-section feed, and station feed.",
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
        f"- Viewer complete: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16L Regen Acceptance Framework.",
    ])

    return "\n".join(lines)
