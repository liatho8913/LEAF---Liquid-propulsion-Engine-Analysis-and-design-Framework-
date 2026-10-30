from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_acceptance_criteria_owner.py").write_text(r'''"""
PHASE 16L.1 — Regen Acceptance Criteria Owner

Purpose:
- Define and evaluate regen acceptance criteria.
- Start the Regen Acceptance Framework.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_ACCEPTANCE_CRITERIA_OWNER_PHASE_16L1"
FAIL_STATUS = "FAIL_REGEN_ACCEPTANCE_CRITERIA_OWNER_PHASE_16L1"


def attach_regen_acceptance_criteria_owner(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16k7_complete") is not True:
        blockers.append("Phase 16K.7 viewer completion gate has not passed.")

    criteria = _build_criteria(results)
    evaluations = [_evaluate_criterion(c, results) for c in criteria]

    failed = [e for e in evaluations if e.get("passed") is not True]

    status = PASS_STATUS if not blockers and not failed else FAIL_STATUS

    if failed:
        for item in failed:
            blockers.append(f"Acceptance criterion failed: {item.get('name')}")

    payload = {
        "status": status,
        "source_phase": "16L.1",
        "visibility": "REPORT_ONLY",
        "criteria_count": len(criteria),
        "passed_count": sum(1 for e in evaluations if e.get("passed") is True),
        "failed_count": len(failed),
        "criteria": criteria,
        "evaluations": evaluations,
    }

    report = _build_report(status, blockers, payload)

    results["regen_acceptance_criteria_owner_complete"] = True
    results["phase_16l1_complete"] = status == PASS_STATUS
    results["regen_acceptance_criteria_owner_status"] = status
    results["phase_16l1_status"] = status
    results["regen_acceptance_criteria_owner_blockers"] = blockers
    results["regen_acceptance_criteria_payload"] = payload
    results["regen_acceptance_criteria_report"] = report

    results["phase_16l2_engineering_acceptance_report_allowed"] = status == PASS_STATUS

    return results


def _build_criteria(results):
    return [
        {
            "name": "viewer_system_complete",
            "description": "The regen viewer system must be complete.",
            "required_key": "regen_viewer_system_complete",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "optimisation_pipeline_complete",
            "description": "The optimisation pipeline must be complete.",
            "required_key": "regen_optimisation_pipeline_complete",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "candidate_acceptance_pipeline_complete",
            "description": "The candidate acceptance pipeline must be complete.",
            "required_key": "regen_candidate_acceptance_pipeline_complete",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "solver_regenerated_after_commit",
            "description": "The solver must have regenerated after committed geometry.",
            "required_key": "regen_solver_regenerated_after_commit",
            "required_value": True,
            "severity": "HIGH",
        },
        {
            "name": "viewer_payload_exists",
            "description": "The unified regen viewer payload must exist.",
            "required_key": "regen_viewer_payload",
            "required_type": "dict",
            "severity": "MEDIUM",
        },
        {
            "name": "station_viewer_payload_exists",
            "description": "The station viewer payload must exist.",
            "required_key": "regen_station_viewer_payload",
            "required_type": "dict",
            "severity": "MEDIUM",
        },
        {
            "name": "cross_section_viewer_payload_exists",
            "description": "The cross-section viewer payload must exist.",
            "required_key": "regen_cross_section_viewer_payload",
            "required_type": "dict",
            "severity": "MEDIUM",
        },
    ]


def _evaluate_criterion(criterion, results):
    key = criterion.get("required_key")
    value = results.get(key)

    passed = False

    if "required_value" in criterion:
        passed = value == criterion.get("required_value")
    elif criterion.get("required_type") == "dict":
        passed = isinstance(value, dict) and bool(value)
    elif criterion.get("required_type") == "list":
        passed = isinstance(value, list) and bool(value)

    return {
        "name": criterion.get("name"),
        "key": key,
        "passed": passed,
        "severity": criterion.get("severity"),
        "observed_type": type(value).__name__ if value is not None else None,
        "observed_value": value if isinstance(value, (str, int, float, bool)) else None,
    }


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.1 REGEN ACCEPTANCE CRITERIA OWNER",
        "==================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Defines regen acceptance criteria.",
        "- Evaluates current regen system against those criteria.",
        "- Produces acceptance criteria payload.",
        "- Does not alter geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "Criteria Summary:",
        f"- Criteria count: {payload.get('criteria_count')}",
        f"- Passed: {payload.get('passed_count')}",
        f"- Failed: {payload.get('failed_count')}",
        "",
        "Evaluations:",
    ])

    for item in payload.get("evaluations", []):
        lines.append(
            f"- {item.get('name')}: {'PASS' if item.get('passed') else 'FAIL'}"
        )

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16L.2 Engineering Acceptance Report.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_acceptance_criteria_owner_phase_16l1.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16l1_complete"] is True
    assert results["phase_16l1_status"] == "PASS_REGEN_ACCEPTANCE_CRITERIA_OWNER_PHASE_16L1"

    payload = results["regen_acceptance_criteria_payload"]
    assert payload["failed_count"] == 0
    assert payload["passed_count"] == payload["criteria_count"]

    report = results["regen_acceptance_criteria_report"]
    assert "REGEN ACCEPTANCE CRITERIA OWNER" in report
    assert "Criteria Summary" in report

    assert results["phase_16l2_engineering_acceptance_report_allowed"] is True

    print("PASS_REGEN_ACCEPTANCE_CRITERIA_OWNER_PHASE_16L1")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_acceptance_criteria_owner import attach_regen_acceptance_criteria_owner" not in text:
    anchor = (
        "try:\n"
        "    from regen_viewer_completion_gate import attach_regen_viewer_completion_gate\n"
        "except Exception:\n"
        "    attach_regen_viewer_completion_gate = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_acceptance_criteria_owner import attach_regen_acceptance_criteria_owner\n"
        "except Exception:\n"
        "    attach_regen_acceptance_criteria_owner = None\n"
    )

if "attach_regen_acceptance_criteria_owner=attach_regen_acceptance_criteria_owner" not in text:
    text = text.replace(
        "attach_regen_viewer_completion_gate=attach_regen_viewer_completion_gate,\n",
        "attach_regen_viewer_completion_gate=attach_regen_viewer_completion_gate,\n\n"
        "            attach_regen_acceptance_criteria_owner=attach_regen_acceptance_criteria_owner,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_acceptance_criteria_owner=None" not in text:
    text = text.replace(
        "attach_regen_viewer_completion_gate=None,\n",
        "attach_regen_viewer_completion_gate=None,\n\n"
        "        attach_regen_acceptance_criteria_owner=None,\n",
    )

if '"regen_acceptance_criteria_owner"' not in text:
    text = text.replace(
        '(\n            "regen_viewer_completion_gate",\n            attach_regen_viewer_completion_gate,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_viewer_completion_gate",\n            attach_regen_viewer_completion_gate,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_acceptance_criteria_owner",\n            attach_regen_acceptance_criteria_owner,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16L1_REGEN_ACCEPTANCE_CRITERIA_OWNER_INTEGRATED")
