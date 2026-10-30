from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_station_viewer_integration.py").write_text(r'''"""
PHASE 16K.6 — Station Viewer Integration

Purpose:
- Link station/axial regen data into the completed viewer system.
- Produce a station viewer payload for inspection of geometry, thermal, and coolant fields.
- Does not alter geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6"
FAIL_STATUS = "FAIL_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6"


STATION_KEYS = (
    "x",
    "station_index",
    "radius",
    "mach",
    "hot_gas_wall_temperature",
    "coolant_wall_temperature",
    "coolant_bulk_temperature",
    "heat_flux",
    "coolant_pressure",
    "coolant_pressure_drop",
    "coolant_reynolds",
    "coolant_channel_width",
    "coolant_channel_height",
    "rib_width",
    "hot_gas_wall_thickness",
)


def attach_regen_station_viewer_integration(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k5_complete") is not True:
        blockers.append("Phase 16K.5 cross section viewer integration has not passed.")

    stations = _find_station_data(results)

    if not isinstance(stations, list) or not stations:
        stations = _build_fallback_station_data(results)

    if not isinstance(stations, list) or not stations:
        blockers.append("No station or fallback geometry station data could be produced.")

    station_rows = []
    if isinstance(stations, list):
        for idx, station in enumerate(stations):
            if isinstance(station, dict):
                station_rows.append(_normalise_station(idx, station))

    if not station_rows:
        blockers.append("Station rows are empty after normalisation.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16K.6",
            "visibility": "UI_REPORT_VIEW",
            "candidate_id": _candidate_id(results),
            "viewer_mode": "STATION_REGEN_INSPECTION",
            "station_count": len(station_rows),
            "columns": list(STATION_KEYS),
            "station_rows": station_rows,
            "presets": {
                "thermal": [
                    "x",
                    "hot_gas_wall_temperature",
                    "coolant_wall_temperature",
                    "coolant_bulk_temperature",
                    "heat_flux",
                ],
                "coolant": [
                    "x",
                    "coolant_pressure",
                    "coolant_pressure_drop",
                    "coolant_reynolds",
                ],
                "geometry": [
                    "x",
                    "radius",
                    "coolant_channel_width",
                    "coolant_channel_height",
                    "rib_width",
                    "hot_gas_wall_thickness",
                ],
                "flow": [
                    "x",
                    "mach",
                    "radius",
                ],
            },
            "read_only": True,
        }

    report = _build_report(status, blockers, payload)

    results["regen_station_viewer_integration_complete"] = True
    results["phase_16k6_complete"] = status == PASS_STATUS
    results["regen_station_viewer_integration_status"] = status
    results["phase_16k6_status"] = status
    results["regen_station_viewer_integration_blockers"] = blockers
    results["regen_station_viewer_payload"] = payload
    results["regen_station_viewer_integration_report"] = report
    results["regen_station_viewer_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k7_viewer_completion_gate_allowed"] = status == PASS_STATUS

    return results


def _find_station_data(results):
    for key in (
        "regen_station_rows",
        "regen_axial_station_rows",
        "regen_station_table",
        "station_rows",
        "axial_station_rows",
        "regen_axial_results",
    ):
        value = results.get(key)
        if isinstance(value, list) and value:
            return value
    return []


def _build_fallback_station_data(results):
    geometry = {}
    for key in (
        "number_of_coolant_channels",
        "coolant_channel_width",
        "coolant_channel_height",
        "rib_width",
        "hot_gas_wall_thickness",
    ):
        if key in results:
            geometry[key] = results[key]

    if not geometry:
        return []

    return [
        {
            "station_index": 0,
            "x": 0.0,
            **geometry,
        }
    ]


def _normalise_station(index, station):
    row = {}

    for key in STATION_KEYS:
        row[key] = station.get(key)

    if row.get("station_index") is None:
        row["station_index"] = index

    if row.get("x") is None:
        row["x"] = station.get("axial_position") or station.get("x_m") or index

    return row


def _candidate_id(results):
    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        value = results.get(key)
        if value:
            return value

    payload = results.get("regen_viewer_payload")
    if isinstance(payload, dict):
        return payload.get("candidate_id")

    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16K.6 STATION VIEWER INTEGRATION",
        "=============================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Links station/axial regen data into the viewer system.",
        "- Produces thermal, coolant, geometry, and flow presets.",
        "- Produces read-only station inspection payload.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "- Does not alter Qt layout yet.",
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
        "Station Viewer Payload:",
        f"- Created: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Station count: {(payload or {}).get('station_count')}",
        f"- Viewer mode: {(payload or {}).get('viewer_mode')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16K.7 Viewer Completion Gate.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_station_viewer_integration_phase_16k6.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
from regen_station_viewer_integration import attach_regen_station_viewer_integration


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["coolant_pressure_drop"] = 900.0
    out["regen_validation_status"] = "PASS_REGENERATED_SOLVER_PAYLOAD"
    out["regen_station_rows"] = [
        {
            "station_index": 0,
            "x": 0.0,
            "radius": 0.02,
            "mach": 1.0,
            "hot_gas_wall_temperature": 850.0,
            "coolant_wall_temperature": 420.0,
            "coolant_bulk_temperature": 300.0,
            "heat_flux": 5.0e6,
            "coolant_pressure": 5.0e6,
            "coolant_pressure_drop": 0.0,
            "coolant_reynolds": 2500.0,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
            "hot_gas_wall_thickness": 0.001,
        },
        {
            "station_index": 1,
            "x": 0.05,
            "radius": 0.03,
            "mach": 2.0,
            "hot_gas_wall_temperature": 780.0,
            "coolant_wall_temperature": 410.0,
            "coolant_bulk_temperature": 305.0,
            "heat_flux": 4.0e6,
            "coolant_pressure": 4.999e6,
            "coolant_pressure_drop": 1000.0,
            "coolant_reynolds": 2600.0,
            "coolant_channel_width": 0.0015,
            "coolant_channel_height": 0.002,
            "rib_width": 0.001,
            "hot_gas_wall_thickness": 0.001,
        },
    ]
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
        attach_regen_station_viewer_integration,
    ):
        results = fn(results)

    assert results["phase_16k6_complete"] is True
    assert results["phase_16k6_status"] == "PASS_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6"

    payload = results["regen_station_viewer_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["viewer_mode"] == "STATION_REGEN_INSPECTION"
    assert payload["visibility"] == "UI_REPORT_VIEW"
    assert payload["read_only"] is True
    assert payload["station_count"] >= 1
    assert "thermal" in payload["presets"]
    assert "coolant" in payload["presets"]
    assert "geometry" in payload["presets"]

    report = results["regen_station_viewer_integration_report"]
    assert "STATION VIEWER INTEGRATION" in report
    assert "Station count" in report

    assert results["phase_16k7_viewer_completion_gate_allowed"] is True

    print("PASS_REGEN_STATION_VIEWER_INTEGRATION_PHASE_16K6")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_station_viewer_integration import attach_regen_station_viewer_integration" not in text:
    anchor = (
        "try:\n"
        "    from regen_cross_section_viewer_integration import attach_regen_cross_section_viewer_integration\n"
        "except Exception:\n"
        "    attach_regen_cross_section_viewer_integration = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_station_viewer_integration import attach_regen_station_viewer_integration\n"
        "except Exception:\n"
        "    attach_regen_station_viewer_integration = None\n"
    )

if "attach_regen_station_viewer_integration=attach_regen_station_viewer_integration" not in text:
    text = text.replace(
        "attach_regen_cross_section_viewer_integration=attach_regen_cross_section_viewer_integration,\n",
        "attach_regen_cross_section_viewer_integration=attach_regen_cross_section_viewer_integration,\n\n"
        "            attach_regen_station_viewer_integration=attach_regen_station_viewer_integration,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_station_viewer_integration=None" not in text:
    text = text.replace(
        "attach_regen_cross_section_viewer_integration=None,\n",
        "attach_regen_cross_section_viewer_integration=None,\n\n"
        "        attach_regen_station_viewer_integration=None,\n",
    )

if '"regen_station_viewer_integration"' not in text:
    text = text.replace(
        '(\n            "regen_cross_section_viewer_integration",\n            attach_regen_cross_section_viewer_integration,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_cross_section_viewer_integration",\n            attach_regen_cross_section_viewer_integration,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_station_viewer_integration",\n            attach_regen_station_viewer_integration,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16K6_STATION_VIEWER_INTEGRATION_INTEGRATED")
