from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_viewer_ownership_architecture.py").write_text(r'''"""
PHASE 16K.4 — Viewer Ownership Architecture

Purpose:
- Add ownership around the regen viewer system.
- Validate viewer payload, rendered report, and navigation payload.
- Produce viewer ownership/visibility/validation/audit/master-gate payloads.
- Does not alter geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_VIEWER_OWNERSHIP_ARCHITECTURE_PHASE_16K4"
FAIL_STATUS = "FAIL_REGEN_VIEWER_OWNERSHIP_ARCHITECTURE_PHASE_16K4"

REQUIRED_VIEWER_KEYS = (
    "regen_viewer_payload",
    "regen_viewer_rendered_sections",
    "regen_viewer_rendered_report",
    "regen_viewer_navigation_payload",
    "regen_viewer_selected_section",
)


def attach_regen_viewer_ownership_architecture(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k3_complete") is not True:
        blockers.append("Phase 16K.3 viewer navigation system has not passed.")

    for key in REQUIRED_VIEWER_KEYS:
        payload = results.get(key)
        if payload is None or payload == {} or payload == []:
            blockers.append(f"Required viewer payload missing: {key}")

    viewer_payload = results.get("regen_viewer_payload")
    navigation_payload = results.get("regen_viewer_navigation_payload")
    rendered_sections = results.get("regen_viewer_rendered_sections")

    if isinstance(viewer_payload, dict):
        if viewer_payload.get("visibility") != "UI_REPORT_VIEW":
            blockers.append("Viewer payload visibility is not UI_REPORT_VIEW.")
        ui_state = viewer_payload.get("ui_state") or {}
        if ui_state.get("editable") is not False:
            blockers.append("Viewer payload is not read-only.")
    else:
        blockers.append("Viewer payload is not a dictionary.")

    if isinstance(navigation_payload, dict):
        if navigation_payload.get("read_only") is not True:
            blockers.append("Navigation payload is not read-only.")
        if navigation_payload.get("section_count") != 7:
            blockers.append("Navigation section count is not 7.")
    else:
        blockers.append("Navigation payload is not a dictionary.")

    if isinstance(rendered_sections, dict):
        expected_sections = {
            "summary",
            "recommendation",
            "comparison",
            "explanation",
            "root_cause",
            "proof",
            "history",
        }
        missing = expected_sections - set(rendered_sections.keys())
        for section in sorted(missing):
            blockers.append(f"Rendered section missing: {section}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    owner_payload = None
    visibility_payload = None
    validation_payload = None
    audit_payload = None
    gate_payload = None

    if status == PASS_STATUS:
        candidate_id = viewer_payload.get("candidate_id")

        owner_payload = {
            "owner": "regen_viewer_owner",
            "status": "OWNED",
            "candidate_id": candidate_id,
            "owned_payloads": list(REQUIRED_VIEWER_KEYS),
            "source_phase": "16K.4",
        }

        visibility_payload = {
            "owner": "regen_viewer_visibility_owner",
            "visibility": "UI_REPORT_VIEW",
            "scalar_output_allowed": False,
            "report_view_allowed": True,
            "editable": False,
            "source_phase": "16K.4",
        }

        validation_payload = {
            "owner": "regen_viewer_validation_owner",
            "status": "VALID",
            "section_count": navigation_payload.get("section_count"),
            "default_section": navigation_payload.get("default_section_key"),
            "required_sections_present": True,
            "source_phase": "16K.4",
        }

        audit_payload = {
            "owner": "regen_viewer_completion_audit",
            "status": "PASS",
            "checked_keys": list(REQUIRED_VIEWER_KEYS),
            "blockers": [],
            "source_phase": "16K.4",
        }

        gate_payload = {
            "owner": "regen_viewer_master_gate",
            "status": PASS_STATUS,
            "completion_state": "VIEWER_OWNERSHIP_ARCHITECTURE_COMPLETE",
            "candidate_id": candidate_id,
            "visibility": "UI_REPORT_VIEW",
            "next_phase": "16K.5 Cross Section Viewer Integration",
        }

    report = _build_report(
        status=status,
        blockers=blockers,
        owner_payload=owner_payload,
        visibility_payload=visibility_payload,
        validation_payload=validation_payload,
        audit_payload=audit_payload,
        gate_payload=gate_payload,
    )

    results["regen_viewer_ownership_architecture_complete"] = True
    results["phase_16k4_complete"] = status == PASS_STATUS
    results["regen_viewer_ownership_architecture_status"] = status
    results["phase_16k4_status"] = status
    results["regen_viewer_ownership_architecture_blockers"] = blockers

    results["regen_viewer_owner_payload"] = owner_payload
    results["regen_viewer_visibility_owner_payload"] = visibility_payload
    results["regen_viewer_validation_owner_payload"] = validation_payload
    results["regen_viewer_completion_audit_payload"] = audit_payload
    results["regen_viewer_master_gate_payload"] = gate_payload
    results["regen_viewer_ownership_architecture_report"] = report

    results["phase_16k5_cross_section_viewer_integration_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _build_report(
    status,
    blockers,
    owner_payload,
    visibility_payload,
    validation_payload,
    audit_payload,
    gate_payload,
):
    lines = [
        "LEAF PHASE 16K.4 VIEWER OWNERSHIP ARCHITECTURE",
        "================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Adds viewer owner.",
        "- Adds viewer visibility owner.",
        "- Adds viewer validation owner.",
        "- Adds viewer completion audit.",
        "- Adds viewer master gate.",
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
        "Ownership Payloads:",
        f"- Viewer owner: {bool(owner_payload)}",
        f"- Visibility owner: {bool(visibility_payload)}",
        f"- Validation owner: {bool(validation_payload)}",
        f"- Completion audit: {bool(audit_payload)}",
        f"- Master gate: {bool(gate_payload)}",
        "",
        "Gate Result:",
        f"- Complete: {bool(gate_payload)}",
        f"- Candidate ID: {(gate_payload or {}).get('candidate_id')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16K.5 Cross Section Viewer Integration.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_viewer_ownership_architecture_phase_16k4.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16k4_complete"] is True
    assert results["phase_16k4_status"] == "PASS_REGEN_VIEWER_OWNERSHIP_ARCHITECTURE_PHASE_16K4"

    assert results["regen_viewer_owner_payload"]["status"] == "OWNED"
    assert results["regen_viewer_visibility_owner_payload"]["visibility"] == "UI_REPORT_VIEW"
    assert results["regen_viewer_visibility_owner_payload"]["editable"] is False
    assert results["regen_viewer_validation_owner_payload"]["status"] == "VALID"
    assert results["regen_viewer_completion_audit_payload"]["status"] == "PASS"

    gate = results["regen_viewer_master_gate_payload"]
    assert gate["completion_state"] == "VIEWER_OWNERSHIP_ARCHITECTURE_COMPLETE"
    assert gate["candidate_id"] == "CANDIDATE_A"

    report = results["regen_viewer_ownership_architecture_report"]
    assert "VIEWER OWNERSHIP ARCHITECTURE" in report
    assert "Master gate: True" in report

    assert results["phase_16k5_cross_section_viewer_integration_allowed"] is True

    print("PASS_REGEN_VIEWER_OWNERSHIP_ARCHITECTURE_PHASE_16K4")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_viewer_ownership_architecture import attach_regen_viewer_ownership_architecture" not in text:
    anchor = (
        "try:\n"
        "    from regen_viewer_navigation_system import attach_regen_viewer_navigation_system\n"
        "except Exception:\n"
        "    attach_regen_viewer_navigation_system = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_viewer_ownership_architecture import attach_regen_viewer_ownership_architecture\n"
        "except Exception:\n"
        "    attach_regen_viewer_ownership_architecture = None\n"
    )

if "attach_regen_viewer_ownership_architecture=attach_regen_viewer_ownership_architecture" not in text:
    text = text.replace(
        "attach_regen_viewer_navigation_system=attach_regen_viewer_navigation_system,\n",
        "attach_regen_viewer_navigation_system=attach_regen_viewer_navigation_system,\n\n"
        "            attach_regen_viewer_ownership_architecture=attach_regen_viewer_ownership_architecture,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_viewer_ownership_architecture=None" not in text:
    text = text.replace(
        "attach_regen_viewer_navigation_system=None,\n",
        "attach_regen_viewer_navigation_system=None,\n\n"
        "        attach_regen_viewer_ownership_architecture=None,\n",
    )

if '"regen_viewer_ownership_architecture"' not in text:
    text = text.replace(
        '(\n            "regen_viewer_navigation_system",\n            attach_regen_viewer_navigation_system,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_viewer_navigation_system",\n            attach_regen_viewer_navigation_system,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_viewer_ownership_architecture",\n            attach_regen_viewer_ownership_architecture,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16K4_VIEWER_OWNERSHIP_ARCHITECTURE_INTEGRATED")
