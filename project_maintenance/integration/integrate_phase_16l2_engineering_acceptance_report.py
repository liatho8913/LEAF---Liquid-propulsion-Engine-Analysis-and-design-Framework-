from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_engineering_acceptance_report.py").write_text(r'''"""
PHASE 16L.2 — Engineering Acceptance Report

Purpose:
- Convert acceptance criteria results into an engineering acceptance report.
- Summarise readiness, evidence, limits, and next actions.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_ENGINEERING_ACCEPTANCE_REPORT_PHASE_16L2"
FAIL_STATUS = "FAIL_REGEN_ENGINEERING_ACCEPTANCE_REPORT_PHASE_16L2"


def attach_regen_engineering_acceptance_report(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16l1_complete") is not True:
        blockers.append("Phase 16L.1 acceptance criteria owner has not passed.")

    criteria_payload = results.get("regen_acceptance_criteria_payload")
    viewer_payload = results.get("regen_viewer_completion_gate_payload")
    optimisation_payload = results.get("regen_optimisation_completion_gate_payload")
    proof_payload = results.get("regen_optimisation_proof_payload")

    for name, payload in (
        ("acceptance criteria payload", criteria_payload),
        ("viewer completion payload", viewer_payload),
        ("optimisation completion payload", optimisation_payload),
        ("optimisation proof payload", proof_payload),
    ):
        if not isinstance(payload, dict) or not payload:
            blockers.append(f"Missing {name}.")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    report_payload = None
    if status == PASS_STATUS:
        report_payload = {
            "status": status,
            "source_phase": "16L.2",
            "visibility": "REPORT_ONLY",
            "candidate_id": _candidate_id(
                criteria_payload,
                viewer_payload,
                optimisation_payload,
                proof_payload,
            ),
            "readiness": "ENGINEERING_ACCEPTANCE_READY",
            "acceptance_summary": {
                "criteria_count": criteria_payload.get("criteria_count"),
                "passed_count": criteria_payload.get("passed_count"),
                "failed_count": criteria_payload.get("failed_count"),
                "viewer_complete": True,
                "optimisation_complete": True,
                "proof_state": proof_payload.get("proof_state"),
                "trust_score": proof_payload.get("trust_score"),
            },
            "evidence": {
                "acceptance_criteria": criteria_payload,
                "viewer_completion": viewer_payload,
                "optimisation_completion": optimisation_payload,
                "optimisation_proof": proof_payload,
            },
            "limits": [
                "Engineering acceptance confirms the software pipeline, evidence chain, and report visibility.",
                "This does not replace physical hot-fire validation.",
                "This does not certify manufacturability or flight readiness.",
                "This remains dependent on the quality of upstream solver models and material data.",
            ],
            "next_actions": [
                "Run acceptance audit ownership.",
                "Run acceptance master gate.",
                "Proceed to final regen sign-off only after acceptance gate passes.",
            ],
        }

    report = _build_report(status, blockers, report_payload)

    results["regen_engineering_acceptance_report_complete"] = True
    results["phase_16l2_complete"] = status == PASS_STATUS
    results["regen_engineering_acceptance_report_status"] = status
    results["phase_16l2_status"] = status
    results["regen_engineering_acceptance_report_blockers"] = blockers
    results["regen_engineering_acceptance_report_payload"] = report_payload
    results["regen_engineering_acceptance_report"] = report
    results["regen_engineering_acceptance_visibility"] = "REPORT_ONLY"

    results["phase_16l3_acceptance_audit_allowed"] = status == PASS_STATUS

    return results


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.2 ENGINEERING ACCEPTANCE REPORT",
        "================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Converts acceptance criteria into an engineering report.",
        "- Summarises readiness, evidence, limits, and next actions.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
        return "\n".join(lines)

    summary = payload.get("acceptance_summary") or {}

    lines.extend([
        "- None.",
        "",
        "Acceptance Summary:",
        f"- Candidate ID: {payload.get('candidate_id')}",
        f"- Readiness: {payload.get('readiness')}",
        f"- Criteria count: {summary.get('criteria_count')}",
        f"- Passed: {summary.get('passed_count')}",
        f"- Failed: {summary.get('failed_count')}",
        f"- Proof state: {summary.get('proof_state')}",
        f"- Trust score: {summary.get('trust_score')}",
        "",
        "Limits:",
    ])

    for item in payload.get("limits", []):
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Next Actions:")

    for item in payload.get("next_actions", []):
        lines.append(f"- {item}")

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16L.3 Acceptance Audit.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_engineering_acceptance_report_phase_16l2.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16l2_complete"] is True
    assert results["phase_16l2_status"] == "PASS_REGEN_ENGINEERING_ACCEPTANCE_REPORT_PHASE_16L2"

    payload = results["regen_engineering_acceptance_report_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["readiness"] == "ENGINEERING_ACCEPTANCE_READY"
    assert payload["acceptance_summary"]["failed_count"] == 0
    assert payload["acceptance_summary"]["trust_score"] == 1.0

    report = results["regen_engineering_acceptance_report"]
    assert "ENGINEERING ACCEPTANCE REPORT" in report
    assert "Acceptance Summary" in report

    assert results["phase_16l3_acceptance_audit_allowed"] is True

    print("PASS_REGEN_ENGINEERING_ACCEPTANCE_REPORT_PHASE_16L2")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_engineering_acceptance_report import attach_regen_engineering_acceptance_report" not in text:
    anchor = (
        "try:\n"
        "    from regen_acceptance_criteria_owner import attach_regen_acceptance_criteria_owner\n"
        "except Exception:\n"
        "    attach_regen_acceptance_criteria_owner = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_engineering_acceptance_report import attach_regen_engineering_acceptance_report\n"
        "except Exception:\n"
        "    attach_regen_engineering_acceptance_report = None\n"
    )

if "attach_regen_engineering_acceptance_report=attach_regen_engineering_acceptance_report" not in text:
    text = text.replace(
        "attach_regen_acceptance_criteria_owner=attach_regen_acceptance_criteria_owner,\n",
        "attach_regen_acceptance_criteria_owner=attach_regen_acceptance_criteria_owner,\n\n"
        "            attach_regen_engineering_acceptance_report=attach_regen_engineering_acceptance_report,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_engineering_acceptance_report=None" not in text:
    text = text.replace(
        "attach_regen_acceptance_criteria_owner=None,\n",
        "attach_regen_acceptance_criteria_owner=None,\n\n"
        "        attach_regen_engineering_acceptance_report=None,\n",
    )

if '"regen_engineering_acceptance_report"' not in text:
    text = text.replace(
        '(\n            "regen_acceptance_criteria_owner",\n            attach_regen_acceptance_criteria_owner,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_acceptance_criteria_owner",\n            attach_regen_acceptance_criteria_owner,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_engineering_acceptance_report",\n            attach_regen_engineering_acceptance_report,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16L2_ENGINEERING_ACCEPTANCE_REPORT_INTEGRATED")
