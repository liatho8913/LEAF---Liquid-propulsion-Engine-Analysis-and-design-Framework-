from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_cross_section_viewer_integration.py").write_text(r'''"""
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
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_cross_section_viewer_integration_phase_16k5.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner
from regen_design_iteration_history_link import attach_regen_design_iteration_history_link
from regen_candidate_acceptance_completion_gate import attach_regen_candidate_acceptance_completion_gate
from regen_recommendation_explanation_engine import attach_regen_recommendation_explanation_engine
from regen_failure_root_cause_system import attach_regen_failure_root_cause_system
from regen_optimisation_proof_system import attach_regen_optimisation_proof_system
from regen_optimisation_completion_gate import attach_regen_optimisation_completion_gate
from regen_viewer_data_adapter import attach_regen_viewer_data_adapter
from regen_viewer_report_renderer import attach_regen_viewer_report_renderer
from regen_viewer_navigation_system import attach_regen_viewer_navigation_system
from regen_viewer_ownership_architecture import attach_regen_viewer_ownership_architecture
from regen_cross_section_viewer_integration import attach_regen_cross_section_viewer_integration


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["coolant_pressure_drop"] = 900.0
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
        "coolant_pressure_drop": 1200.0,
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

    for fn in (
        attach_regen_ranking_owner_source_repair,
        attach_regen_recommendation_feed_repair,
        attach_regen_recommendation_viewer_repair,
        attach_regen_end_to_end_candidate_selection_validation,
        attach_regen_candidate_acceptance_integration,
        attach_regen_pending_geometry_commit_validation,
        attach_regen_live_geometry_commit_execution,
        attach_regen_solver_regeneration_after_commit,
        attach_regen_before_after_solver_comparison_report_owner,
        attach_regen_design_iteration_history_link,
        attach_regen_candidate_acceptance_completion_gate,
        attach_regen_recommendation_explanation_engine,
        attach_regen_failure_root_cause_system,
        attach_regen_optimisation_proof_system,
        attach_regen_optimisation_completion_gate,
        attach_regen_viewer_data_adapter,
        attach_regen_viewer_report_renderer,
        attach_regen_viewer_navigation_system,
        attach_regen_viewer_ownership_architecture,
        attach_regen_cross_section_viewer_integration,
    ):
        results = fn(results)

    assert results["phase_16k5_complete"] is True
    assert results["phase_16k5_status"] == "PASS_REGEN_CROSS_SECTION_VIEWER_INTEGRATION_PHASE_16K5"

    payload = results["regen_cross_section_viewer_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["viewer_mode"] == "CROSS_SECTION_GEOMETRY_COMPARISON"
    assert payload["visibility"] == "UI_REPORT_VIEW"
    assert payload["display_layers"]["read_only"] is True
    assert payload["active_geometry"]["number_of_coolant_channels"] == 80
    assert payload["comparison"]["change_count"] >= 1

    report = results["regen_cross_section_viewer_integration_report"]
    assert "CROSS SECTION VIEWER INTEGRATION" in report
    assert "Viewer mode" in report

    assert results["phase_16k6_station_viewer_integration_allowed"] is True

    print("PASS_REGEN_CROSS_SECTION_VIEWER_INTEGRATION_PHASE_16K5")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_cross_section_viewer_integration import attach_regen_cross_section_viewer_integration" not in text:
    anchor = (
        "try:\n"
        "    from regen_viewer_ownership_architecture import attach_regen_viewer_ownership_architecture\n"
        "except Exception:\n"
        "    attach_regen_viewer_ownership_architecture = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_cross_section_viewer_integration import attach_regen_cross_section_viewer_integration\n"
        "except Exception:\n"
        "    attach_regen_cross_section_viewer_integration = None\n"
    )

if "attach_regen_cross_section_viewer_integration=attach_regen_cross_section_viewer_integration" not in text:
    text = text.replace(
        "attach_regen_viewer_ownership_architecture=attach_regen_viewer_ownership_architecture,\n",
        "attach_regen_viewer_ownership_architecture=attach_regen_viewer_ownership_architecture,\n\n"
        "            attach_regen_cross_section_viewer_integration=attach_regen_cross_section_viewer_integration,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_cross_section_viewer_integration=None" not in text:
    text = text.replace(
        "attach_regen_viewer_ownership_architecture=None,\n",
        "attach_regen_viewer_ownership_architecture=None,\n\n"
        "        attach_regen_cross_section_viewer_integration=None,\n",
    )

if '"regen_cross_section_viewer_integration"' not in text:
    text = text.replace(
        '(\n            "regen_viewer_ownership_architecture",\n            attach_regen_viewer_ownership_architecture,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_viewer_ownership_architecture",\n            attach_regen_viewer_ownership_architecture,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_cross_section_viewer_integration",\n            attach_regen_cross_section_viewer_integration,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16K5_CROSS_SECTION_VIEWER_INTEGRATION_INTEGRATED")
