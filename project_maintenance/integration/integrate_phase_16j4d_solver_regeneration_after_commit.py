from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_solver_regeneration_after_commit.py").write_text(r'''"""
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
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_solver_regeneration_after_commit_phase_16j4d.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["regen_geometry_valid"] = True
    out["regen_validation_status"] = "PASS_REGENERATED_SOLVER_PAYLOAD"
    return out


def main():
    results = {
        "number_of_coolant_channels": 60,
        "coolant_channel_width": 0.0010,
        "coolant_channel_height": 0.0015,
        "rib_width": 0.0010,
        "hot_gas_wall_thickness": 0.0008,
        "corrected_thrust": 3300.0,
        "isp_vac": 300.0,
        "regen_solver_regeneration_callable": fake_solver,
        "regen_candidate_ranking_input_population": [
            {
                "candidate_id": "CANDIDATE_A",
                "candidate_geometry": {
                    "number_of_coolant_channels": 80,
                    "coolant_channel_width": 0.0015,
                    "coolant_channel_height": 0.0020,
                    "rib_width": 0.0010,
                    "hot_gas_wall_thickness": 0.0010,
                },
            }
        ],
    }

    results = attach_regen_ranking_owner_source_repair(results)
    results = attach_regen_recommendation_feed_repair(results)
    results = attach_regen_recommendation_viewer_repair(results)
    results = attach_regen_end_to_end_candidate_selection_validation(results)
    results = attach_regen_candidate_acceptance_integration(results)
    results = attach_regen_pending_geometry_commit_validation(results)
    results = attach_regen_live_geometry_commit_execution(results)
    results = attach_regen_solver_regeneration_after_commit(results)

    assert results["phase_16j4d_complete"] is True
    assert results["phase_16j4d_status"] == "PASS_REGEN_SOLVER_REGENERATION_AFTER_COMMIT_PHASE_16J4D"

    payload = results["regen_solver_regeneration_result_payload"]
    assert payload["corrected_thrust"] == 3500.0
    assert payload["isp_vac"] == 315.0
    assert payload["regen_validation_status"] == "PASS_REGENERATED_SOLVER_PAYLOAD"

    comparison = results["regen_solver_regeneration_before_after_comparison"]
    assert comparison["change_count"] >= 2

    assert results["regen_solver_regenerated_after_commit"] is True
    assert results["phase_16j4e_before_after_solver_comparison_allowed"] is True

    report = results["regen_solver_regeneration_report"]
    assert "SOLVER REGENERATION AFTER COMMIT" in report
    assert "Refuses to fake regenerated solver outputs" in report

    print("PASS_REGEN_SOLVER_REGENERATION_AFTER_COMMIT_PHASE_16J4D")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit" not in text:
    anchor = (
        "try:\n"
        "    from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution\n"
        "except Exception:\n"
        "    attach_regen_live_geometry_commit_execution = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit\n"
        "except Exception:\n"
        "    attach_regen_solver_regeneration_after_commit = None\n"
    )

if "attach_regen_solver_regeneration_after_commit=attach_regen_solver_regeneration_after_commit" not in text:
    text = text.replace(
        "attach_regen_live_geometry_commit_execution=attach_regen_live_geometry_commit_execution,\n",
        "attach_regen_live_geometry_commit_execution=attach_regen_live_geometry_commit_execution,\n\n"
        "            attach_regen_solver_regeneration_after_commit=attach_regen_solver_regeneration_after_commit,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_solver_regeneration_after_commit=None" not in text:
    text = text.replace(
        "attach_regen_live_geometry_commit_execution=None,\n",
        "attach_regen_live_geometry_commit_execution=None,\n\n"
        "        attach_regen_solver_regeneration_after_commit=None,\n",
    )

if '"regen_solver_regeneration_after_commit"' not in text:
    text = text.replace(
        '(\n            "regen_live_geometry_commit_execution",\n            attach_regen_live_geometry_commit_execution,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_live_geometry_commit_execution",\n            attach_regen_live_geometry_commit_execution,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_solver_regeneration_after_commit",\n            attach_regen_solver_regeneration_after_commit,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J4D_SOLVER_REGENERATION_AFTER_COMMIT_INTEGRATED")
