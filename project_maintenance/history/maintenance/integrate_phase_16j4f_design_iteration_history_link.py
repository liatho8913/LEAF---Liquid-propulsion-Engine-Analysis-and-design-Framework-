from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_design_iteration_history_link.py").write_text(r'''"""
PHASE 16J.4F — Design Iteration History Link

Purpose:
- Link recommendation, acceptance, commit, regeneration, and comparison reports
  into one design iteration event.
- Preserve explainability:
  what changed, why it changed, whether it improved/regressed, and what phase did it.
- Does not modify geometry.
- Does not rerun solver.
"""

from datetime import datetime, timezone

PASS_STATUS = "PASS_REGEN_DESIGN_ITERATION_HISTORY_LINK_PHASE_16J4F"
FAIL_STATUS = "FAIL_REGEN_DESIGN_ITERATION_HISTORY_LINK_PHASE_16J4F"


def attach_regen_design_iteration_history_link(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j4e_complete") is not True:
        blockers.append("Phase 16J.4E before/after report ownership has not passed.")

    recommendation = results.get("regen_recommendation_viewer_payload")
    acceptance = results.get("regen_candidate_acceptance_history_event")
    commit = results.get("regen_live_geometry_commit_audit_record")
    regen = results.get("regen_solver_regeneration_audit_record")
    comparison = results.get("regen_before_after_solver_comparison_report_payload")
    summary = results.get("regen_before_after_solver_comparison_summary")

    required = {
        "recommendation viewer payload": recommendation,
        "acceptance history event": acceptance,
        "live geometry commit audit": commit,
        "solver regeneration audit": regen,
        "before/after comparison report payload": comparison,
        "before/after comparison summary": summary,
    }

    for name, payload in required.items():
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name}.")

    candidate_id = _candidate_id(results, recommendation, acceptance, commit, regen, comparison)

    if not candidate_id:
        blockers.append("Candidate ID could not be resolved for design iteration history.")

    event = None

    if not blockers:
        event = {
            "event_type": "REGEN_DESIGN_ITERATION_COMPLETED",
            "phase": "16J.4F",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_id": candidate_id,
            "iteration_title": f"Accepted regen candidate {candidate_id}",
            "chain": [
                "16J.3F Recommendation Feed Repair",
                "16J.3G Recommendation Viewer Repair",
                "16J.3H End-to-End Selection Validation",
                "16J.4 Candidate Acceptance Integration",
                "16J.4B Pending Geometry Commit Validation",
                "16J.4C Live Geometry Commit Execution",
                "16J.4D Solver Regeneration After Commit",
                "16J.4E Before/After Solver Comparison Report Ownership",
            ],
            "recommendation_reasoning": recommendation.get("reasoning"),
            "acceptance_summary": acceptance.get("summary"),
            "commit_summary": {
                "committed_keys": commit.get("committed_keys"),
                "before_after": commit.get("before_after"),
            },
            "solver_regeneration_status": regen.get("status"),
            "comparison_summary": summary,
            "classified_changes": comparison.get("classified_changes"),
            "visibility": "REPORT_ONLY",
            "geometry_application_state": "COMMITTED_AND_REGENERATED",
        }

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report = _build_report(status, blockers, event)

    existing_history = results.get("regen_design_iteration_history")
    if not isinstance(existing_history, list):
        existing_history = []

    if event:
        existing_history = existing_history + [event]

    results["regen_design_iteration_history_link_complete"] = True
    results["phase_16j4f_complete"] = status == PASS_STATUS
    results["regen_design_iteration_history_link_status"] = status
    results["phase_16j4f_status"] = status
    results["regen_design_iteration_history_link_blockers"] = blockers
    results["regen_design_iteration_history_event"] = event
    results["regen_design_iteration_history"] = existing_history
    results["regen_design_iteration_history_report"] = report
    results["regen_design_iteration_history_visibility"] = "REPORT_ONLY"

    results["phase_16j4g_candidate_acceptance_completion_gate_allowed"] = (
        status == PASS_STATUS
    )

    return results


def _candidate_id(results, *payloads):
    for payload in payloads:
        if isinstance(payload, dict):
            value = payload.get("candidate_id")
            if value:
                return value

    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        value = results.get(key)
        if value:
            return value

    return None


def _build_report(status, blockers, event):
    lines = [
        "LEAF PHASE 16J.4F DESIGN ITERATION HISTORY LINK",
        "==================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Links recommendation, acceptance, commit, regeneration, and comparison into one history event.",
        "- Records what changed and why.",
        "- Records whether solver outputs improved or regressed.",
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

    if event:
        lines.extend([
            "",
            "Design Iteration Event:",
            f"- Candidate ID: {event.get('candidate_id')}",
            f"- Event type: {event.get('event_type')}",
            f"- Geometry state: {event.get('geometry_application_state')}",
            "",
            "Comparison Summary:",
        ])

        summary = event.get("comparison_summary") or {}
        for key in ("changed", "improved", "regressed", "neutral_changed", "unchanged"):
            lines.append(f"- {key}: {summary.get(key)}")

    lines.extend([
        "",
        "Visibility:",
        "- REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.4G Candidate Acceptance Completion Gate.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46i_nested_test_relocation/leaf_qt/history/test/test_regen_design_iteration_history_link_phase_16j4f.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
from regen_recommendation_feed_repair import attach_regen_recommendation_feed_repair
from regen_recommendation_viewer_repair import attach_regen_recommendation_viewer_repair
from regen_end_to_end_candidate_selection_validation import attach_regen_end_to_end_candidate_selection_validation
from regen_candidate_acceptance_integration import attach_regen_candidate_acceptance_integration
from regen_pending_geometry_commit_validation import attach_regen_pending_geometry_commit_validation
from regen_live_geometry_commit_execution import attach_regen_live_geometry_commit_execution
from regen_solver_regeneration_after_commit import attach_regen_solver_regeneration_after_commit
from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner
from regen_design_iteration_history_link import attach_regen_design_iteration_history_link


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
    ):
        results = fn(results)

    assert results["phase_16j4f_complete"] is True
    assert results["phase_16j4f_status"] == "PASS_REGEN_DESIGN_ITERATION_HISTORY_LINK_PHASE_16J4F"

    event = results["regen_design_iteration_history_event"]
    assert event["candidate_id"] == "CANDIDATE_A"
    assert event["event_type"] == "REGEN_DESIGN_ITERATION_COMPLETED"
    assert event["geometry_application_state"] == "COMMITTED_AND_REGENERATED"
    assert len(event["chain"]) >= 8

    history = results["regen_design_iteration_history"]
    assert len(history) == 1
    assert history[0]["candidate_id"] == "CANDIDATE_A"

    report = results["regen_design_iteration_history_report"]
    assert "DESIGN ITERATION HISTORY LINK" in report
    assert "REPORT_ONLY" in report

    assert results["phase_16j4g_candidate_acceptance_completion_gate_allowed"] is True

    print("PASS_REGEN_DESIGN_ITERATION_HISTORY_LINK_PHASE_16J4F")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_design_iteration_history_link import attach_regen_design_iteration_history_link" not in text:
    anchor = (
        "try:\n"
        "    from regen_before_after_solver_comparison_report_owner import attach_regen_before_after_solver_comparison_report_owner\n"
        "except Exception:\n"
        "    attach_regen_before_after_solver_comparison_report_owner = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_design_iteration_history_link import attach_regen_design_iteration_history_link\n"
        "except Exception:\n"
        "    attach_regen_design_iteration_history_link = None\n"
    )

if "attach_regen_design_iteration_history_link=attach_regen_design_iteration_history_link" not in text:
    text = text.replace(
        "attach_regen_before_after_solver_comparison_report_owner=attach_regen_before_after_solver_comparison_report_owner,\n",
        "attach_regen_before_after_solver_comparison_report_owner=attach_regen_before_after_solver_comparison_report_owner,\n\n"
        "            attach_regen_design_iteration_history_link=attach_regen_design_iteration_history_link,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_design_iteration_history_link=None" not in text:
    text = text.replace(
        "attach_regen_before_after_solver_comparison_report_owner=None,\n",
        "attach_regen_before_after_solver_comparison_report_owner=None,\n\n"
        "        attach_regen_design_iteration_history_link=None,\n",
    )

if '"regen_design_iteration_history_link"' not in text:
    text = text.replace(
        '(\n            "regen_before_after_solver_comparison_report_owner",\n            attach_regen_before_after_solver_comparison_report_owner,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_before_after_solver_comparison_report_owner",\n            attach_regen_before_after_solver_comparison_report_owner,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_design_iteration_history_link",\n            attach_regen_design_iteration_history_link,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J4F_DESIGN_ITERATION_HISTORY_LINK_INTEGRATED")
