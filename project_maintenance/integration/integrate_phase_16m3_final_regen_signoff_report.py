from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_final_signoff_report.py").write_text(r'''"""
PHASE 16M.3 — Final Regen Sign-Off Report

Purpose:
- Produce the final regen sign-off report.
- Summarise completion, verification, acceptance, viewer, optimisation, evidence, limits, and next actions.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_FINAL_SIGNOFF_REPORT_PHASE_16M3"
FAIL_STATUS = "FAIL_REGEN_FINAL_SIGNOFF_REPORT_PHASE_16M3"


def attach_regen_final_signoff_report(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16m2_complete") is not True:
        blockers.append("Phase 16M.2 final regen verification audit has not passed.")

    completion = results.get("regen_final_completion_audit_payload")
    verification = results.get("regen_final_verification_audit_payload")
    acceptance = results.get("regen_acceptance_master_gate_payload")
    viewer = results.get("regen_viewer_completion_gate_payload")
    optimisation = results.get("regen_optimisation_completion_gate_payload")
    engineering = results.get("regen_engineering_acceptance_report_payload")

    required = {
        "completion audit": completion,
        "verification audit": verification,
        "acceptance gate": acceptance,
        "viewer gate": viewer,
        "optimisation gate": optimisation,
        "engineering acceptance report": engineering,
    }

    for name, payload in required.items():
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name} payload.")

    candidate_id = _candidate_id(*required.values())

    if not candidate_id:
        blockers.append("Could not resolve candidate ID for final sign-off report.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16M.3",
            "visibility": "REPORT_ONLY",
            "candidate_id": candidate_id,
            "signoff_report_state": "FINAL_REGEN_SIGNOFF_REPORT_READY",
            "completion_summary": {
                "optimisation_complete": True,
                "viewer_complete": True,
                "acceptance_complete": True,
                "completion_audit_passed": True,
                "verification_audit_passed": True,
            },
            "evidence": required,
            "engineering_limits": engineering.get("limits", []),
            "final_statement": (
                "The LEAF regenerative cooling software pipeline has completed "
                "optimisation, viewer integration, acceptance, completion audit, "
                "and verification audit. This is software-system sign-off evidence, "
                "not physical hot-fire certification."
            ),
            "next_actions": [
                "Run final regen master sign-off gate.",
                "Preserve all report-only payloads for UI/export.",
                "Do not start new physics until final master gate passes.",
            ],
        }

    report = _build_report(status, blockers, payload)

    results["regen_final_signoff_report_complete"] = True
    results["phase_16m3_complete"] = status == PASS_STATUS
    results["regen_final_signoff_report_status"] = status
    results["phase_16m3_status"] = status
    results["regen_final_signoff_report_blockers"] = blockers
    results["regen_final_signoff_report_payload"] = payload
    results["regen_final_signoff_report_text"] = report

    results["phase_16m4_final_regen_master_gate_allowed"] = status == PASS_STATUS

    return results


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16M.3 FINAL REGEN SIGN-OFF REPORT",
        "==============================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Produces final regen sign-off report.",
        "- Summarises completion, verification, acceptance, viewer, optimisation, and limits.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    lines.extend([
        "- None.",
        "",
        "Final Sign-Off Report:",
        f"- Candidate ID: {payload.get('candidate_id')}",
        f"- Report state: {payload.get('signoff_report_state')}",
        "",
        "Completion Summary:",
    ])

    for key, value in payload.get("completion_summary", {}).items():
        lines.append(f"- {key}: {value}")

    lines.extend([
        "",
        "Final Statement:",
        payload.get("final_statement"),
        "",
        "Engineering Limits:",
    ])

    for item in payload.get("engineering_limits", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Next Actions:")

    for item in payload.get("next_actions", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16M.4 Final Regen Master Gate.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_final_signoff_report_phase_16m3.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
from regen_viewer_completion_gate import attach_regen_viewer_completion_gate
from regen_acceptance_criteria_owner import attach_regen_acceptance_criteria_owner
from regen_engineering_acceptance_report import attach_regen_engineering_acceptance_report
from regen_acceptance_audit import attach_regen_acceptance_audit
from regen_acceptance_master_gate import attach_regen_acceptance_master_gate
from regen_final_completion_audit import attach_regen_final_completion_audit
from regen_final_verification_audit import attach_regen_final_verification_audit
from regen_final_signoff_report import attach_regen_final_signoff_report


def fake_solver(payload):
    out = dict(payload)
    out["corrected_thrust"] = 3500.0
    out["isp_vac"] = 315.0
    out["coolant_pressure_drop"] = 900.0
    out["regen_validation_status"] = "PASS_REGENERATED_SOLVER_PAYLOAD"
    out["regen_station_rows"] = [{"station_index": 0, "x": 0.0}]
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
        attach_regen_viewer_completion_gate,
        attach_regen_acceptance_criteria_owner,
        attach_regen_engineering_acceptance_report,
        attach_regen_acceptance_audit,
        attach_regen_acceptance_master_gate,
        attach_regen_final_completion_audit,
        attach_regen_final_verification_audit,
        attach_regen_final_signoff_report,
    ):
        results = fn(results)

    assert results["phase_16m3_complete"] is True
    assert results["phase_16m3_status"] == "PASS_REGEN_FINAL_SIGNOFF_REPORT_PHASE_16M3"

    payload = results["regen_final_signoff_report_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["signoff_report_state"] == "FINAL_REGEN_SIGNOFF_REPORT_READY"
    assert payload["completion_summary"]["optimisation_complete"] is True
    assert payload["completion_summary"]["viewer_complete"] is True
    assert payload["completion_summary"]["acceptance_complete"] is True

    report = results["regen_final_signoff_report_text"]
    assert "FINAL REGEN SIGN-OFF REPORT" in report
    assert "software-system sign-off evidence" in report

    assert results["phase_16m4_final_regen_master_gate_allowed"] is True

    print("PASS_REGEN_FINAL_SIGNOFF_REPORT_PHASE_16M3")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_final_signoff_report import attach_regen_final_signoff_report" not in text:
    anchor = (
        "try:\n"
        "    from regen_final_verification_audit import attach_regen_final_verification_audit\n"
        "except Exception:\n"
        "    attach_regen_final_verification_audit = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_final_signoff_report import attach_regen_final_signoff_report\n"
        "except Exception:\n"
        "    attach_regen_final_signoff_report = None\n"
    )

if "attach_regen_final_signoff_report=attach_regen_final_signoff_report" not in text:
    text = text.replace(
        "attach_regen_final_verification_audit=attach_regen_final_verification_audit,\n",
        "attach_regen_final_verification_audit=attach_regen_final_verification_audit,\n\n"
        "            attach_regen_final_signoff_report=attach_regen_final_signoff_report,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_final_signoff_report=None" not in text:
    text = text.replace(
        "attach_regen_final_verification_audit=None,\n",
        "attach_regen_final_verification_audit=None,\n\n"
        "        attach_regen_final_signoff_report=None,\n",
    )

if '"regen_final_signoff_report"' not in text:
    text = text.replace(
        '(\n            "regen_final_verification_audit",\n            attach_regen_final_verification_audit,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_final_verification_audit",\n            attach_regen_final_verification_audit,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_final_signoff_report",\n            attach_regen_final_signoff_report,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16M3_FINAL_REGEN_SIGNOFF_REPORT_INTEGRATED")
