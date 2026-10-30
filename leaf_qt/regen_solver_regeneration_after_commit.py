"""
PHASE 16J.4D — Solver Regeneration After Commit

Purpose:
- Consume the committed geometry from Phase 16J.4C.
- Execute a controlled solver-regeneration call when a solver callback is available.
- Produce a post-commit solver payload.
- Produce before/after comparison data.
- Refuse to fake a solver PASS when no solver callable is available.
"""

import copy
from datetime import datetime, timezone

PASS_STATUS = "PASS_REGEN_SOLVER_REGENERATION_AFTER_COMMIT_PHASE_16J4D"
FAIL_STATUS = "FAIL_REGEN_SOLVER_REGENERATION_AFTER_COMMIT_PHASE_16J4D"

SOLVER_CALLBACK_KEYS = (
    "regen_solver_regeneration_callable",
    "engine_solver_callable",
    "solver_callable",
)

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


def attach_regen_solver_regeneration_after_commit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j4c_complete") is not True:
        blockers.append("Phase 16J.4C live geometry commit has not passed.")

    if results.get("regen_candidate_live_geometry_commit_executed") is not True:
        blockers.append("Live geometry commit flag is not true.")

    committed_geometry = _extract_geometry(results)

    if not committed_geometry:
        blockers.append("Committed geometry snapshot is missing.")

    callback_key, callback = _find_solver_callback(results)

    if callback is None:
        blockers.append(
            "No solver regeneration callable is available. "
            "This phase refuses to fake regenerated solver outputs."
        )

    pre_solver_snapshot = _extract_solver_snapshot(results)
    regenerated_payload = None
    callback_error = None

    if not blockers:
        try:
            regenerated_payload = callback(copy.deepcopy(results))
        except Exception as exc:
            callback_error = repr(exc)
            blockers.append(f"Solver regeneration callable failed: {callback_error}")

    if regenerated_payload is not None and not isinstance(regenerated_payload, dict):
        blockers.append("Solver regeneration callable did not return a dictionary payload.")

    post_solver_snapshot = (
        _extract_solver_snapshot(regenerated_payload)
        if isinstance(regenerated_payload, dict)
        else {}
    )

    comparison = _build_solver_comparison(pre_solver_snapshot, post_solver_snapshot)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    audit_record = {
        "event_type": "REGEN_SOLVER_REGENERATION_AFTER_COMMIT",
        "phase": "16J.4D",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "solver_callback_key": callback_key,
        "committed_geometry": committed_geometry,
        "callback_error": callback_error,
        "comparison": comparison,
    }

    report = _build_report(
        status=status,
        blockers=blockers,
        callback_key=callback_key,
        committed_geometry=committed_geometry,
        comparison=comparison,
        callback_error=callback_error,
    )

    results["regen_solver_regeneration_after_commit_complete"] = True
    results["phase_16j4d_complete"] = status == PASS_STATUS
    results["regen_solver_regeneration_after_commit_status"] = status
    results["phase_16j4d_status"] = status
    results["regen_solver_regeneration_after_commit_blockers"] = blockers
    results["regen_solver_regeneration_callback_key"] = callback_key
    results["regen_solver_regeneration_committed_geometry_snapshot"] = committed_geometry
    results["regen_solver_regeneration_pre_solver_snapshot"] = pre_solver_snapshot
    results["regen_solver_regeneration_post_solver_snapshot"] = post_solver_snapshot
    results["regen_solver_regeneration_result_payload"] = regenerated_payload
    results["regen_solver_regeneration_before_after_comparison"] = comparison
    results["regen_solver_regeneration_audit_record"] = audit_record
    results["regen_solver_regeneration_report"] = report

    results["regen_solver_regenerated_after_commit"] = status == PASS_STATUS
    results["phase_16j4e_before_after_solver_comparison_allowed"] = status == PASS_STATUS

    return results


def _find_solver_callback(results):
    for key in SOLVER_CALLBACK_KEYS:
        callback = results.get(key)
        if callable(callback):
            return key, callback
    return None, None


def _candidate_id_from_approval_or_results(approval, results):
    if isinstance(approval, dict):
        candidate_id = approval.get("candidate_id")
        if candidate_id:
            return candidate_id

    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        candidate_id = results.get(key)
        if candidate_id:
            return candidate_id

    audit = results.get("regen_live_geometry_commit_audit_record")
    if isinstance(audit, dict):
        candidate_id = audit.get("candidate_id")
        if candidate_id:
            return candidate_id

    return None




def _extract_geometry(results):
    geometry = {}
    for key in GEOMETRY_KEYS:
        if key in results:
            geometry[key] = copy.deepcopy(results[key])
    return geometry


def _extract_solver_snapshot(payload):
    if not isinstance(payload, dict):
        return {}

    keys = (
        "thrust",
        "corrected_thrust",
        "specific_impulse",
        "isp",
        "isp_vac",
        "chamber_pressure",
        "mass_flow_rate",
        "coolant_pressure_drop",
        "regen_max_hot_wall_temperature",
        "regen_max_coolant_wall_temperature",
        "regen_geometry_valid",
        "regen_validation_status",
    )

    return {key: copy.deepcopy(payload[key]) for key in keys if key in payload}


def _build_solver_comparison(before, after):
    keys = sorted(set(before.keys()) | set(after.keys()))
    changes = []

    for key in keys:
        old = before.get(key)
        new = after.get(key)
        changes.append({
            "key": key,
            "before": old,
            "after": new,
            "changed": old != new,
        })

    return {
        "change_count": sum(1 for item in changes if item["changed"]),
        "compared_key_count": len(changes),
        "changes": changes,
    }


def _build_report(status, blockers, callback_key, committed_geometry, comparison, callback_error):
    lines = [
        "LEAF PHASE 16J.4D SOLVER REGENERATION AFTER COMMIT",
        "=====================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Consumes committed geometry from Phase 16J.4C.",
        "- Calls a real solver regeneration callable when available.",
        "- Produces post-commit solver payload.",
        "- Produces before/after solver comparison.",
        "- Refuses to fake regenerated solver outputs.",
        "",
        f"Solver callback key: {callback_key}",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    if callback_error:
        lines.extend(["", f"Callback error: {callback_error}"])

    lines.extend(["", "Committed Geometry:"])

    if committed_geometry:
        for key in sorted(committed_geometry.keys()):
            lines.append(f"- {key}: {committed_geometry[key]}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Before/After Solver Comparison:",
        f"- Compared keys: {comparison.get('compared_key_count')}",
        f"- Changed keys: {comparison.get('change_count')}",
    ])

    for change in comparison.get("changes", [])[:20]:
        lines.append(
            f"- {change['key']}: {change['before']} -> {change['after']}"
        )

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16J.4E Before/After Solver Comparison Report Ownership.",
    ])

    return "\n".join(lines)
