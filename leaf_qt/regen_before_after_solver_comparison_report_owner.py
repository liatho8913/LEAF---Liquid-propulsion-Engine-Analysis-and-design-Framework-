"""
PHASE 16J.4E — Before/After Solver Comparison Report Ownership

Purpose:
- Own the before/after solver comparison produced by 16J.4D.
- Classify changed solver outputs.
- Produce a report-only payload for UI/report viewers.
- Preserve traceability from candidate acceptance to regeneration.
"""

PASS_STATUS = "PASS_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E"
FAIL_STATUS = "FAIL_REGEN_BEFORE_AFTER_SOLVER_COMPARISON_REPORT_PHASE_16J4E"

HIGHER_IS_BETTER = {
    "thrust",
    "corrected_thrust",
    "specific_impulse",
    "isp",
    "isp_vac",
}

LOWER_IS_BETTER = {
    "coolant_pressure_drop",
    "regen_max_hot_wall_temperature",
    "regen_max_coolant_wall_temperature",
}


def attach_regen_before_after_solver_comparison_report_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j4d_complete") is not True:
        blockers.append("Phase 16J.4D solver regeneration has not passed.")

    comparison = results.get("regen_solver_regeneration_before_after_comparison")
    audit = results.get("regen_solver_regeneration_audit_record")
    payload = results.get("regen_solver_regeneration_result_payload")

    if not isinstance(comparison, dict) or not comparison:
        blockers.append("Solver before/after comparison payload is missing.")

    if not isinstance(audit, dict) or not audit:
        blockers.append("Solver regeneration audit record is missing.")

    if not isinstance(payload, dict) or not payload:
        blockers.append("Post-commit solver result payload is missing.")

    owned_changes = []

    if isinstance(comparison, dict):
        for change in comparison.get("changes", []):
            if isinstance(change, dict):
                owned_changes.append(_classify_change(change))

    summary = _summarise_changes(owned_changes)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report_payload = None
    if status == PASS_STATUS:
        report_payload = {
            "status": status,
            "candidate_id": _candidate_id_from_results(results, audit),
            "source_phase": "16J.4E",
            "upstream_phase": "16J.4D",
            "visibility": "REPORT_ONLY",
            "summary": summary,
            "classified_changes": owned_changes,
            "solver_callback_key": results.get("regen_solver_regeneration_callback_key"),
            "geometry_snapshot": results.get("regen_solver_regeneration_committed_geometry_snapshot"),
            "audit_record": audit,
        }

    report = _build_report(status, blockers, report_payload, owned_changes, summary)

    results["regen_before_after_solver_comparison_report_owner_complete"] = True
    results["phase_16j4e_complete"] = status == PASS_STATUS
    results["regen_before_after_solver_comparison_report_status"] = status
    results["phase_16j4e_status"] = status
    results["regen_before_after_solver_comparison_report_blockers"] = blockers
    results["regen_before_after_solver_comparison_report_payload"] = report_payload
    results["regen_before_after_solver_comparison_classified_changes"] = owned_changes
    results["regen_before_after_solver_comparison_summary"] = summary
    results["regen_before_after_solver_comparison_report"] = report

    results["regen_before_after_solver_comparison_visibility"] = "REPORT_ONLY"
    results["phase_16j4f_design_iteration_history_link_allowed"] = status == PASS_STATUS

    return results



def _candidate_id_from_results(results, audit):
    if isinstance(audit, dict):
        candidate_id = audit.get("candidate_id")
        if candidate_id:
            return candidate_id

    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        candidate_id = results.get(key)
        if candidate_id:
            return candidate_id

    approval = results.get("regen_pending_geometry_commit_approval_payload")
    if isinstance(approval, dict):
        candidate_id = approval.get("candidate_id")
        if candidate_id:
            return candidate_id

    accepted = results.get("regen_candidate_acceptance_pending_application_payload")
    if isinstance(accepted, dict):
        candidate_id = accepted.get("candidate_id")
        if candidate_id:
            return candidate_id

    viewer = results.get("regen_recommendation_viewer_payload")
    if isinstance(viewer, dict):
        candidate_id = viewer.get("candidate_id")
        if candidate_id:
            return candidate_id

    return None


def _classify_change(change):
    key = change.get("key")
    before = change.get("before")
    after = change.get("after")
    changed = bool(change.get("changed"))

    classification = "UNCHANGED"
    delta = None

    if changed:
        try:
            delta = float(after) - float(before)
        except Exception:
            delta = None

        if delta is None:
            classification = "CHANGED_NON_NUMERIC"
        elif key in HIGHER_IS_BETTER:
            classification = "IMPROVED" if delta > 0 else "REGRESSED"
        elif key in LOWER_IS_BETTER:
            classification = "IMPROVED" if delta < 0 else "REGRESSED"
        else:
            classification = "CHANGED_NEUTRAL"

    return {
        "key": key,
        "before": before,
        "after": after,
        "changed": changed,
        "delta": delta,
        "classification": classification,
    }


def _summarise_changes(changes):
    return {
        "total_compared": len(changes),
        "changed": sum(1 for c in changes if c.get("changed")),
        "improved": sum(1 for c in changes if c.get("classification") == "IMPROVED"),
        "regressed": sum(1 for c in changes if c.get("classification") == "REGRESSED"),
        "neutral_changed": sum(1 for c in changes if c.get("classification") in {"CHANGED_NEUTRAL", "CHANGED_NON_NUMERIC"}),
        "unchanged": sum(1 for c in changes if c.get("classification") == "UNCHANGED"),
    }


def _build_report(status, blockers, report_payload, changes, summary):
    lines = [
        "LEAF PHASE 16J.4E BEFORE/AFTER SOLVER COMPARISON REPORT OWNERSHIP",
        "====================================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Owns the before/after solver comparison from Phase 16J.4D.",
        "- Classifies changed outputs as improved, regressed, neutral, or unchanged.",
        "- Publishes report-only payload for viewer/report systems.",
        "- Does not rerun the solver.",
        "- Does not alter committed geometry.",
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
        "Summary:",
        f"- Compared outputs: {summary.get('total_compared')}",
        f"- Changed outputs: {summary.get('changed')}",
        f"- Improved: {summary.get('improved')}",
        f"- Regressed: {summary.get('regressed')}",
        f"- Neutral changed: {summary.get('neutral_changed')}",
        f"- Unchanged: {summary.get('unchanged')}",
        "",
        "Classified Changes:",
    ])

    if changes:
        for change in changes:
            lines.append(
                f"- {change.get('key')}: {change.get('before')} -> {change.get('after')} "
                f"[{change.get('classification')}]"
            )
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Visibility:",
        "- REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.4F Design Iteration History Link.",
    ])

    return "\n".join(lines)
