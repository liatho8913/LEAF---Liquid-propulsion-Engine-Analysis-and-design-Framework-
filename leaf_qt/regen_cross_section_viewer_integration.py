"""
PHASE 16K.5 — Cross Section Viewer Integration

Purpose:
- Link committed/accepted/recommended geometry to the regen viewer system.
- Produce a cross-section viewer payload for the existing drawing/UI layer.
- Compare previous geometry against accepted active geometry.
- Does not redraw Qt widgets yet.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_CROSS_SECTION_VIEWER_INTEGRATION_PHASE_16K5"
FAIL_STATUS = "FAIL_REGEN_CROSS_SECTION_VIEWER_INTEGRATION_PHASE_16K5"

GEOMETRY_KEYS = (
    "number_of_coolant_channels",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
    "outer_wall_thickness",
    "coating_thickness",
    "bond_coat_thickness",
    "coolant_channel_aspect_ratio",
)


def attach_regen_cross_section_viewer_integration(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k4_complete") is not True:
        blockers.append("Phase 16K.4 viewer ownership architecture has not passed.")

    active_geometry = _extract_active_geometry(results)
    pending_payload = results.get("regen_candidate_acceptance_pending_application_payload")
    recommendation = results.get("regen_recommendation_viewer_payload")
    commit_audit = results.get("regen_live_geometry_commit_audit_record")

    if not active_geometry:
        blockers.append("Active geometry could not be extracted for cross-section viewer.")

    if not isinstance(pending_payload, dict) or not pending_payload:
        blockers.append("Pending/accepted geometry payload is missing.")

    if not isinstance(recommendation, dict) or not recommendation:
        blockers.append("Recommendation viewer payload is missing.")

    if not isinstance(commit_audit, dict) or not commit_audit:
        blockers.append("Live geometry commit audit record is missing.")

    previous_geometry = {}
    accepted_geometry = {}
    recommended_geometry = {}

    if isinstance(pending_payload, dict):
        previous_geometry = pending_payload.get("previous_geometry") or {}
        accepted_geometry = pending_payload.get("accepted_geometry") or {}

    if isinstance(recommendation, dict):
        recommended_geometry = recommendation.get("geometry") or {}

    comparison = _compare_geometries(previous_geometry, active_geometry)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16K.5",
            "visibility": "UI_REPORT_VIEW",
            "candidate_id": _candidate_id(results, recommendation, commit_audit),
            "viewer_mode": "CROSS_SECTION_GEOMETRY_COMPARISON",
            "active_geometry": active_geometry,
            "previous_geometry": previous_geometry,
            "accepted_geometry": accepted_geometry,
            "recommended_geometry": recommended_geometry,
            "comparison": comparison,
            "display_layers": {
                "show_previous": True,
                "show_recommended": True,
                "show_accepted": True,
                "show_active": True,
                "show_dimension_callouts": True,
                "read_only": True,
            },
        }

    report = _build_report(status, blockers, payload)

    results["regen_cross_section_viewer_integration_complete"] = True
    results["phase_16k5_complete"] = status == PASS_STATUS
    results["regen_cross_section_viewer_integration_status"] = status
    results["phase_16k5_status"] = status
    results["regen_cross_section_viewer_integration_blockers"] = blockers
    results["regen_cross_section_viewer_payload"] = payload
    results["regen_cross_section_viewer_integration_report"] = report
    results["regen_cross_section_viewer_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k6_station_viewer_integration_allowed"] = status == PASS_STATUS

    return results


def _extract_active_geometry(results):
    geometry = {}
    for key in GEOMETRY_KEYS:
        if key in results:
            geometry[key] = results[key]
    return geometry


def _compare_geometries(previous, active):
    keys = sorted(set(previous.keys()) | set(active.keys()))
    changes = []

    for key in keys:
        before = previous.get(key)
        after = active.get(key)
        changes.append({
            "key": key,
            "before": before,
            "after": after,
            "changed": before != after,
        })

    return {
        "change_count": sum(1 for item in changes if item["changed"]),
        "compared_key_count": len(changes),
        "changes": changes,
    }


def _candidate_id(results, *payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")

    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        value = results.get(key)
        if value:
            return value

    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16K.5 CROSS SECTION VIEWER INTEGRATION",
        "===================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Links active, previous, accepted, and recommended geometry to the viewer.",
        "- Produces a cross-section viewer payload.",
        "- Produces geometry comparison metadata.",
        "- Does not redraw Qt widgets yet.",
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
        "Cross Section Payload:",
        f"- Created: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Viewer mode: {(payload or {}).get('viewer_mode')}",
        f"- Change count: {((payload or {}).get('comparison') or {}).get('change_count')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16K.6 Station Viewer Integration.",
    ])

    return "\n".join(lines)
