from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_viewer_navigation_system.py").write_text(r'''"""
PHASE 16K.3 — Viewer Navigation System

Purpose:
- Build a navigation model for rendered regen viewer sections.
- Allow UI to select summary/recommendation/comparison/explanation/root-cause/proof/history.
- Produce default selected section.
- Does not alter geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3"
FAIL_STATUS = "FAIL_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3"

SECTION_ORDER = (
    "summary",
    "recommendation",
    "comparison",
    "explanation",
    "root_cause",
    "proof",
    "history",
)

SECTION_LABELS = {
    "summary": "Summary",
    "recommendation": "Recommendation",
    "comparison": "Before / After",
    "explanation": "Explanation",
    "root_cause": "Root Cause",
    "proof": "Proof",
    "history": "History",
}


def attach_regen_viewer_navigation_system(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k2_complete") is not True:
        blockers.append("Phase 16K.2 viewer report renderer has not passed.")

    rendered_sections = results.get("regen_viewer_rendered_sections")
    viewer_payload = results.get("regen_viewer_payload")

    if not isinstance(rendered_sections, dict) or not rendered_sections:
        blockers.append("Rendered viewer sections are missing.")

    if not isinstance(viewer_payload, dict) or not viewer_payload:
        blockers.append("Viewer payload is missing.")

    navigation_items = []
    selected_section = None

    if isinstance(rendered_sections, dict):
        for index, section_key in enumerate(SECTION_ORDER):
            section_text = rendered_sections.get(section_key)
            if not isinstance(section_text, str) or not section_text.strip():
                blockers.append(f"Rendered section missing or empty: {section_key}")
            else:
                navigation_items.append({
                    "index": index,
                    "key": section_key,
                    "label": SECTION_LABELS.get(section_key, section_key),
                    "enabled": True,
                    "has_content": True,
                })

    status = PASS_STATUS if not blockers else FAIL_STATUS

    navigation_payload = None

    if status == PASS_STATUS:
        default_key = "summary"
        selected_section = {
            "key": default_key,
            "label": SECTION_LABELS[default_key],
            "content": rendered_sections[default_key],
            "index": 0,
        }

        navigation_payload = {
            "status": status,
            "source_phase": "16K.3",
            "visibility": "UI_REPORT_VIEW",
            "candidate_id": viewer_payload.get("candidate_id"),
            "navigation_items": navigation_items,
            "default_section_key": default_key,
            "selected_section": selected_section,
            "section_count": len(navigation_items),
            "read_only": True,
        }

    report = _build_report(status, blockers, navigation_payload)

    results["regen_viewer_navigation_system_complete"] = True
    results["phase_16k3_complete"] = status == PASS_STATUS
    results["regen_viewer_navigation_system_status"] = status
    results["phase_16k3_status"] = status
    results["regen_viewer_navigation_system_blockers"] = blockers
    results["regen_viewer_navigation_payload"] = navigation_payload
    results["regen_viewer_selected_section"] = selected_section
    results["regen_viewer_navigation_report"] = report
    results["regen_viewer_navigation_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k4_viewer_ownership_architecture_allowed"] = status == PASS_STATUS

    return results


def _build_report(status, blockers, navigation_payload):
    lines = [
        "LEAF PHASE 16K.3 VIEWER NAVIGATION SYSTEM",
        "==========================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Builds navigation model for regen viewer sections.",
        "- Produces default selected section.",
        "- Keeps viewer read-only.",
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
        "Navigation:",
        f"- Created: {bool(navigation_payload)}",
        f"- Section count: {(navigation_payload or {}).get('section_count')}",
        f"- Default section: {(navigation_payload or {}).get('default_section_key')}",
        "- Visibility: UI_REPORT_VIEW",
        "",
        "Next Required Phase:",
        "- 16K.4 Viewer Ownership Architecture.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_viewer_navigation_system_phase_16k3.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16k3_complete"] is True
    assert results["phase_16k3_status"] == "PASS_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3"

    payload = results["regen_viewer_navigation_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["section_count"] == 7
    assert payload["default_section_key"] == "summary"
    assert payload["read_only"] is True

    selected = results["regen_viewer_selected_section"]
    assert selected["key"] == "summary"
    assert "Optimisation Summary" in selected["content"]

    assert results["phase_16k4_viewer_ownership_architecture_allowed"] is True

    print("PASS_REGEN_VIEWER_NAVIGATION_SYSTEM_PHASE_16K3")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_viewer_navigation_system import attach_regen_viewer_navigation_system" not in text:
    anchor = (
        "try:\n"
        "    from regen_viewer_report_renderer import attach_regen_viewer_report_renderer\n"
        "except Exception:\n"
        "    attach_regen_viewer_report_renderer = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_viewer_navigation_system import attach_regen_viewer_navigation_system\n"
        "except Exception:\n"
        "    attach_regen_viewer_navigation_system = None\n"
    )

if "attach_regen_viewer_navigation_system=attach_regen_viewer_navigation_system" not in text:
    text = text.replace(
        "attach_regen_viewer_report_renderer=attach_regen_viewer_report_renderer,\n",
        "attach_regen_viewer_report_renderer=attach_regen_viewer_report_renderer,\n\n"
        "            attach_regen_viewer_navigation_system=attach_regen_viewer_navigation_system,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_viewer_navigation_system=None" not in text:
    text = text.replace(
        "attach_regen_viewer_report_renderer=None,\n",
        "attach_regen_viewer_report_renderer=None,\n\n"
        "        attach_regen_viewer_navigation_system=None,\n",
    )

if '"regen_viewer_navigation_system"' not in text:
    text = text.replace(
        '(\n            "regen_viewer_report_renderer",\n            attach_regen_viewer_report_renderer,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_viewer_report_renderer",\n            attach_regen_viewer_report_renderer,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_viewer_navigation_system",\n            attach_regen_viewer_navigation_system,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16K3_VIEWER_NAVIGATION_SYSTEM_INTEGRATED")
