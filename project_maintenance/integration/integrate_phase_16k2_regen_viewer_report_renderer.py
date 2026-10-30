from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_viewer_report_renderer.py").write_text(r'''"""
PHASE 16K.2 — Regen Viewer Report Renderer

Purpose:
- Render the unified regen viewer payload from 16K.1.
- Produce UI-ready section text.
- Preserve read-only/report-only behaviour.
- Does not modify geometry.
- Does not rerun solver.
- Does not alter Qt layout yet.
"""

PASS_STATUS = "PASS_REGEN_VIEWER_REPORT_RENDERER_PHASE_16K2"
FAIL_STATUS = "FAIL_REGEN_VIEWER_REPORT_RENDERER_PHASE_16K2"


SECTION_ORDER = (
    "summary",
    "recommendation",
    "comparison",
    "explanation",
    "root_cause",
    "proof",
    "history",
)


def attach_regen_viewer_report_renderer(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k1_complete") is not True:
        blockers.append("Phase 16K.1 viewer data adapter has not passed.")

    payload = results.get("regen_viewer_payload")

    if not isinstance(payload, dict) or not payload:
        blockers.append("Unified regen viewer payload is missing.")

    rendered_sections = {}
    full_report = None

    if isinstance(payload, dict):
        sections = payload.get("sections") or {}
        for section_name in SECTION_ORDER:
            section = sections.get(section_name)
            if not isinstance(section, dict) or not section:
                blockers.append(f"Viewer section missing or invalid: {section_name}")
            else:
                rendered_sections[section_name] = _render_section(section_name, section)

    status = PASS_STATUS if not blockers else FAIL_STATUS

    if status == PASS_STATUS:
        full_report = _build_full_report(payload, rendered_sections)

    results["regen_viewer_report_renderer_complete"] = True
    results["phase_16k2_complete"] = status == PASS_STATUS
    results["regen_viewer_report_renderer_status"] = status
    results["phase_16k2_status"] = status
    results["regen_viewer_report_renderer_blockers"] = blockers
    results["regen_viewer_rendered_sections"] = rendered_sections
    results["regen_viewer_rendered_report"] = full_report
    results["regen_viewer_report_renderer_visibility"] = "UI_REPORT_VIEW"

    results["phase_16k3_viewer_navigation_system_allowed"] = status == PASS_STATUS

    return results


def _render_section(section_name, section):
    heading = section.get("heading", section_name.replace("_", " ").title())
    lines = [heading, "=" * len(heading), ""]

    if section_name == "summary":
        lines.extend([
            f"Candidate ID: {section.get('candidate_id')}",
            f"Completion State: {section.get('completion_state')}",
            f"Trust Score: {section.get('trust_score')}",
            f"Status: {section.get('status')}",
        ])

    elif section_name == "recommendation":
        lines.extend([
            f"Candidate ID: {section.get('candidate_id')}",
            f"Rank: {section.get('rank')}",
            f"Score: {section.get('score')}",
            "",
            "Reasoning:",
            str(section.get("reasoning")),
            "",
            "Advantages:",
        ])
        lines.extend(_bullet_list(section.get("advantages")))
        lines.append("")
        lines.append("Penalties:")
        lines.extend(_bullet_list(section.get("penalties")))

    elif section_name == "comparison":
        summary = section.get("summary") or {}
        lines.extend([
            f"Compared Outputs: {summary.get('total_compared')}",
            f"Changed Outputs: {summary.get('changed')}",
            f"Improved: {summary.get('improved')}",
            f"Regressed: {summary.get('regressed')}",
            f"Neutral Changed: {summary.get('neutral_changed')}",
            "",
            "Classified Changes:",
        ])
        changes = section.get("classified_changes") or []
        if changes:
            for change in changes:
                lines.append(
                    f"- {change.get('key')}: {change.get('before')} -> "
                    f"{change.get('after')} [{change.get('classification')}]"
                )
        else:
            lines.append("- None.")

    elif section_name == "explanation":
        lines.extend([
            "Headline:",
            str(section.get("headline")),
            "",
            "Why Chosen:",
        ])
        lines.extend(_bullet_list(section.get("why_chosen")))
        trust = section.get("trust_assessment") or {}
        lines.extend([
            "",
            "Trust Assessment:",
            f"- Level: {trust.get('level')}",
            f"- Reason: {trust.get('reason')}",
            "",
            "Remaining Risks:",
        ])
        lines.extend(_bullet_list(section.get("remaining_risks")))
        lines.append("")
        lines.append("Next Actions:")
        lines.extend(_bullet_list(section.get("next_actions")))

    elif section_name == "root_cause":
        summary = section.get("summary") or {}
        lines.extend([
            f"Total Root Causes: {summary.get('total')}",
            f"High Severity: {summary.get('high')}",
            f"Medium Severity: {summary.get('medium')}",
            f"Low Severity: {summary.get('low')}",
            "",
            "Root Causes:",
        ])
        causes = section.get("root_causes") or []
        if causes:
            for cause in causes:
                lines.append(
                    f"- [{cause.get('severity')}] {cause.get('category')}: "
                    f"{cause.get('message')}"
                )
        else:
            lines.append("- None detected.")
        lines.append("")
        lines.append("Next Actions:")
        lines.extend(_bullet_list(section.get("next_actions")))

    elif section_name == "proof":
        lines.extend([
            f"Proof State: {section.get('proof_state')}",
            f"Trust Score: {section.get('trust_score')}",
            "",
            "Proof Ledger:",
        ])
        ledger = section.get("proof_ledger") or []
        if ledger:
            for item in ledger:
                lines.append(
                    f"- {item.get('check')}: "
                    f"{'PASS' if item.get('passed') else 'FAIL'}"
                )
        else:
            lines.append("- None.")

    elif section_name == "history":
        lines.extend([
            f"Event Type: {section.get('event_type')}",
            f"Phase: {section.get('phase')}",
            f"Timestamp UTC: {section.get('timestamp_utc')}",
            "",
            "Chain:",
        ])
        lines.extend(_bullet_list(section.get("chain")))
        lines.append("")
        lines.append("Comparison Summary:")
        summary = section.get("comparison_summary") or {}
        for key, value in summary.items():
            lines.append(f"- {key}: {value}")

    return "\n".join(lines)


def _bullet_list(values):
    if not values:
        return ["- None."]
    if not isinstance(values, list):
        return [f"- {values}"]
    return [f"- {value}" for value in values]


def _build_full_report(payload, rendered_sections):
    lines = [
        "LEAF REGEN VIEWER REPORT",
        "========================",
        "",
        f"Title: {payload.get('title')}",
        f"Candidate ID: {payload.get('candidate_id')}",
        f"Visibility: {payload.get('visibility')}",
        "",
    ]

    ui_state = payload.get("ui_state") or {}
    lines.extend([
        "UI State:",
        f"- Geometry Applied: {ui_state.get('geometry_applied')}",
        f"- Solver Regenerated: {ui_state.get('solver_regenerated')}",
        f"- Report Only: {ui_state.get('report_only')}",
        f"- Editable: {ui_state.get('editable')}",
        "",
    ])

    for section_name in SECTION_ORDER:
        lines.append(rendered_sections[section_name])
        lines.append("")
        lines.append("-" * 72)
        lines.append("")

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_viewer_report_renderer_phase_16k2.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16k2_complete"] is True
    assert results["phase_16k2_status"] == "PASS_REGEN_VIEWER_REPORT_RENDERER_PHASE_16K2"

    sections = results["regen_viewer_rendered_sections"]
    assert "summary" in sections
    assert "recommendation" in sections
    assert "comparison" in sections
    assert "proof" in sections

    report = results["regen_viewer_rendered_report"]
    assert "LEAF REGEN VIEWER REPORT" in report
    assert "Candidate ID: CANDIDATE_A" in report
    assert "Optimisation Summary" in report
    assert "Before / After Solver Comparison" in report

    assert results["phase_16k3_viewer_navigation_system_allowed"] is True

    print("PASS_REGEN_VIEWER_REPORT_RENDERER_PHASE_16K2")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_viewer_report_renderer import attach_regen_viewer_report_renderer" not in text:
    anchor = (
        "try:\n"
        "    from regen_viewer_data_adapter import attach_regen_viewer_data_adapter\n"
        "except Exception:\n"
        "    attach_regen_viewer_data_adapter = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_viewer_report_renderer import attach_regen_viewer_report_renderer\n"
        "except Exception:\n"
        "    attach_regen_viewer_report_renderer = None\n"
    )

if "attach_regen_viewer_report_renderer=attach_regen_viewer_report_renderer" not in text:
    text = text.replace(
        "attach_regen_viewer_data_adapter=attach_regen_viewer_data_adapter,\n",
        "attach_regen_viewer_data_adapter=attach_regen_viewer_data_adapter,\n\n"
        "            attach_regen_viewer_report_renderer=attach_regen_viewer_report_renderer,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_viewer_report_renderer=None" not in text:
    text = text.replace(
        "attach_regen_viewer_data_adapter=None,\n",
        "attach_regen_viewer_data_adapter=None,\n\n"
        "        attach_regen_viewer_report_renderer=None,\n",
    )

if '"regen_viewer_report_renderer"' not in text:
    text = text.replace(
        '(\n            "regen_viewer_data_adapter",\n            attach_regen_viewer_data_adapter,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_viewer_data_adapter",\n            attach_regen_viewer_data_adapter,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_viewer_report_renderer",\n            attach_regen_viewer_report_renderer,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16K2_REGEN_VIEWER_REPORT_RENDERER_INTEGRATED")
