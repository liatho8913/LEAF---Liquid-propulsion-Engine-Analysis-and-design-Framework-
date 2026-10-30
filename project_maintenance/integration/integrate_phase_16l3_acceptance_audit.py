from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_acceptance_audit.py").write_text(r'''"""
PHASE 16L.3 — Acceptance Audit

Purpose:
- Audit acceptance criteria and engineering acceptance report.
- Confirm acceptance evidence is complete and internally consistent.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_ACCEPTANCE_AUDIT_PHASE_16L3"
FAIL_STATUS = "FAIL_REGEN_ACCEPTANCE_AUDIT_PHASE_16L3"


def attach_regen_acceptance_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16l2_complete") is not True:
        blockers.append("Phase 16L.2 engineering acceptance report has not passed.")

    criteria = results.get("regen_acceptance_criteria_payload")
    report_payload = results.get("regen_engineering_acceptance_report_payload")

    if not isinstance(criteria, dict) or not criteria:
        blockers.append("Acceptance criteria payload is missing.")

    if not isinstance(report_payload, dict) or not report_payload:
        blockers.append("Engineering acceptance report payload is missing.")

    audit_items = []

    if isinstance(criteria, dict):
        audit_items.append(_audit_item(
            "criteria_all_passed",
            criteria.get("failed_count") == 0,
            f"failed_count={criteria.get('failed_count')}",
        ))
        audit_items.append(_audit_item(
            "criteria_counts_consistent",
            criteria.get("criteria_count") == criteria.get("passed_count") + criteria.get("failed_count"),
            "criteria_count should equal passed_count + failed_count",
        ))

    if isinstance(report_payload, dict):
        summary = report_payload.get("acceptance_summary") or {}
        audit_items.append(_audit_item(
            "readiness_statement_present",
            report_payload.get("readiness") == "ENGINEERING_ACCEPTANCE_READY",
            f"readiness={report_payload.get('readiness')}",
        ))
        audit_items.append(_audit_item(
            "report_failed_count_zero",
            summary.get("failed_count") == 0,
            f"failed_count={summary.get('failed_count')}",
        ))
        audit_items.append(_audit_item(
            "trust_score_one",
            summary.get("trust_score") == 1.0,
            f"trust_score={summary.get('trust_score')}",
        ))
        audit_items.append(_audit_item(
            "limits_present",
            isinstance(report_payload.get("limits"), list) and len(report_payload.get("limits")) > 0,
            "engineering limits must be stated",
        ))

    failed_items = [item for item in audit_items if item.get("passed") is not True]

    for item in failed_items:
        blockers.append(f"Acceptance audit item failed: {item.get('name')}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = {
        "status": status,
        "source_phase": "16L.3",
        "visibility": "REPORT_ONLY",
        "candidate_id": _candidate_id(criteria, report_payload),
        "audit_item_count": len(audit_items),
        "passed_count": sum(1 for item in audit_items if item.get("passed") is True),
        "failed_count": len(failed_items),
        "audit_items": audit_items,
    }

    report = _build_report(status, blockers, payload)

    results["regen_acceptance_audit_complete"] = True
    results["phase_16l3_complete"] = status == PASS_STATUS
    results["regen_acceptance_audit_status"] = status
    results["phase_16l3_status"] = status
    results["regen_acceptance_audit_blockers"] = blockers
    results["regen_acceptance_audit_payload"] = payload
    results["regen_acceptance_audit_report"] = report

    results["phase_16l4_acceptance_master_gate_allowed"] = status == PASS_STATUS

    return results


def _audit_item(name, passed, detail):
    return {
        "name": name,
        "passed": bool(passed),
        "detail": detail,
    }


def _candidate_id(*payloads):
    for payload in payloads:
        if isinstance(payload, dict) and payload.get("candidate_id"):
            return payload.get("candidate_id")
    return None


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16L.3 ACCEPTANCE AUDIT",
        "===================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Audits acceptance criteria.",
        "- Audits engineering acceptance report.",
        "- Confirms acceptance evidence consistency.",
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
        "Audit Summary:",
        f"- Candidate ID: {payload.get('candidate_id')}",
        f"- Audit items: {payload.get('audit_item_count')}",
        f"- Passed: {payload.get('passed_count')}",
        f"- Failed: {payload.get('failed_count')}",
        "",
        "Audit Items:",
    ])

    for item in payload.get("audit_items", []):
        lines.append(
            f"- {item.get('name')}: {'PASS' if item.get('passed') else 'FAIL'}"
        )

    lines.extend([
        "",
        "Next Required Phase:",
        "- 16L.4 Acceptance Master Gate.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_acceptance_audit_phase_16l3.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16l3_complete"] is True
    assert results["phase_16l3_status"] == "PASS_REGEN_ACCEPTANCE_AUDIT_PHASE_16L3"

    payload = results["regen_acceptance_audit_payload"]
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["failed_count"] == 0
    assert payload["passed_count"] == payload["audit_item_count"]

    report = results["regen_acceptance_audit_report"]
    assert "ACCEPTANCE AUDIT" in report
    assert "Audit Summary" in report

    assert results["phase_16l4_acceptance_master_gate_allowed"] is True

    print("PASS_REGEN_ACCEPTANCE_AUDIT_PHASE_16L3")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_acceptance_audit import attach_regen_acceptance_audit" not in text:
    anchor = (
        "try:\n"
        "    from regen_engineering_acceptance_report import attach_regen_engineering_acceptance_report\n"
        "except Exception:\n"
        "    attach_regen_engineering_acceptance_report = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_acceptance_audit import attach_regen_acceptance_audit\n"
        "except Exception:\n"
        "    attach_regen_acceptance_audit = None\n"
    )

if "attach_regen_acceptance_audit=attach_regen_acceptance_audit" not in text:
    text = text.replace(
        "attach_regen_engineering_acceptance_report=attach_regen_engineering_acceptance_report,\n",
        "attach_regen_engineering_acceptance_report=attach_regen_engineering_acceptance_report,\n\n"
        "            attach_regen_acceptance_audit=attach_regen_acceptance_audit,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_acceptance_audit=None" not in text:
    text = text.replace(
        "attach_regen_engineering_acceptance_report=None,\n",
        "attach_regen_engineering_acceptance_report=None,\n\n"
        "        attach_regen_acceptance_audit=None,\n",
    )

if '"regen_acceptance_audit"' not in text:
    text = text.replace(
        '(\n            "regen_engineering_acceptance_report",\n            attach_regen_engineering_acceptance_report,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_engineering_acceptance_report",\n            attach_regen_engineering_acceptance_report,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_acceptance_audit",\n            attach_regen_acceptance_audit,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16L3_ACCEPTANCE_AUDIT_INTEGRATED")
