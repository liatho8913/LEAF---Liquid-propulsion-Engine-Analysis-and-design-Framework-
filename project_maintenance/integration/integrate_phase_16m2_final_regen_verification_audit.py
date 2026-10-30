from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_final_verification_audit.py").write_text(r'''"""
PHASE 16M.2 — Final Regen Verification Audit

Purpose:
- Verify final regen completion audit evidence.
- Confirm final reports, proof, acceptance, viewer, and optimisation payloads exist.
- Does not alter geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_FINAL_VERIFICATION_AUDIT_PHASE_16M2"
FAIL_STATUS = "FAIL_REGEN_FINAL_VERIFICATION_AUDIT_PHASE_16M2"

REQUIRED_PHASE_FLAGS = (
    "phase_16m1_complete",
    "phase_16l4_complete",
    "phase_16k7_complete",
    "phase_16j8_complete",
)

REQUIRED_EVIDENCE_KEYS = (
    "regen_final_completion_audit_payload",
    "regen_acceptance_master_gate_payload",
    "regen_viewer_completion_gate_payload",
    "regen_optimisation_completion_gate_payload",
    "regen_optimisation_proof_payload",
    "regen_engineering_acceptance_report_payload",
    "regen_viewer_rendered_report",
)


def attach_regen_final_verification_audit(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    for flag in REQUIRED_PHASE_FLAGS:
        if results.get(flag) is not True:
            blockers.append(f"Required final verification phase incomplete: {flag}")

    for key in REQUIRED_EVIDENCE_KEYS:
        value = results.get(key)
        if value is None or value == {} or value == []:
            blockers.append(f"Required final verification evidence missing: {key}")

    proof = results.get("regen_optimisation_proof_payload") or {}
    if proof.get("proof_state") != "OPTIMISATION_CHAIN_PROVEN":
        blockers.append("Optimisation proof state is not proven.")

    acceptance = results.get("regen_acceptance_master_gate_payload") or {}
    if acceptance.get("completion_state") != "REGEN_ACCEPTANCE_FRAMEWORK_COMPLETE":
        blockers.append("Acceptance framework is not complete.")

    viewer = results.get("regen_viewer_completion_gate_payload") or {}
    if viewer.get("completion_state") != "REGEN_VIEWER_COMPLETE":
        blockers.append("Viewer system is not complete.")

    completion = results.get("regen_final_completion_audit_payload") or {}
    if completion.get("completion_state") != "FINAL_REGEN_COMPLETION_AUDIT_PASS":
        blockers.append("Final completion audit did not pass.")

    candidate_ids = _candidate_ids(results)
    if candidate_ids and len(set(candidate_ids)) != 1:
        blockers.append(f"Candidate ID mismatch during final verification: {candidate_ids}")

    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "source_phase": "16M.2",
            "visibility": "REPORT_ONLY",
            "candidate_id": candidate_ids[0] if candidate_ids else None,
            "verification_state": "FINAL_REGEN_VERIFICATION_AUDIT_PASS",
            "verified_phase_flags": list(REQUIRED_PHASE_FLAGS),
            "verified_evidence_keys": list(REQUIRED_EVIDENCE_KEYS),
            "next_phase": "16M.3 Final Regen Sign-Off Report",
        }

    report = _build_report(status, blockers, payload)

    results["regen_final_verification_audit_complete"] = True
    results["phase_16m2_complete"] = status == PASS_STATUS
    results["regen_final_verification_audit_status"] = status
    results["phase_16m2_status"] = status
    results["regen_final_verification_audit_blockers"] = blockers
    results["regen_final_verification_audit_payload"] = payload
    results["regen_final_verification_audit_report"] = report

    results["phase_16m3_final_regen_signoff_report_allowed"] = status == PASS_STATUS

    return results


def _candidate_ids(results):
    ids = []
    for key in (
        "regen_final_completion_audit_payload",
        "regen_acceptance_master_gate_payload",
        "regen_viewer_completion_gate_payload",
        "regen_optimisation_completion_gate_payload",
        "regen_optimisation_proof_payload",
        "regen_engineering_acceptance_report_payload",
    ):
        payload = results.get(key)
        if isinstance(payload, dict) and payload.get("candidate_id"):
            ids.append(payload.get("candidate_id"))
    return ids


def _build_report(status, blockers, payload):
    lines = [
        "LEAF PHASE 16M.2 FINAL REGEN VERIFICATION AUDIT",
        "=================================================",
        "",
        f"Status: {status}",
        "",
        "Scope:",
        "- Verifies final completion audit evidence.",
        "- Confirms optimisation, viewer, acceptance, proof, and reports.",
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
        "Verification Result:",
        f"- Verified: {bool(payload)}",
        f"- Candidate ID: {(payload or {}).get('candidate_id')}",
        f"- Verification state: {(payload or {}).get('verification_state')}",
        "",
        "Next Required Phase:",
        "- 16M.3 Final Regen Sign-Off Report.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_final_verification_audit_phase_16m2.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16m2_complete"] is True
    assert results["phase_16m2_status"] == "PASS_REGEN_FINAL_VERIFICATION_AUDIT_PHASE_16M2"

    payload = results["regen_final_verification_audit_payload"]
    assert payload["verification_state"] == "FINAL_REGEN_VERIFICATION_AUDIT_PASS"
    assert payload["candidate_id"] == "CANDIDATE_A"

    report = results["regen_final_verification_audit_report"]
    assert "FINAL REGEN VERIFICATION AUDIT" in report
    assert "Verified: True" in report

    assert results["phase_16m3_final_regen_signoff_report_allowed"] is True

    print("PASS_REGEN_FINAL_VERIFICATION_AUDIT_PHASE_16M2")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_final_verification_audit import attach_regen_final_verification_audit" not in text:
    anchor = (
        "try:\n"
        "    from regen_final_completion_audit import attach_regen_final_completion_audit\n"
        "except Exception:\n"
        "    attach_regen_final_completion_audit = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_final_verification_audit import attach_regen_final_verification_audit\n"
        "except Exception:\n"
        "    attach_regen_final_verification_audit = None\n"
    )

if "attach_regen_final_verification_audit=attach_regen_final_verification_audit" not in text:
    text = text.replace(
        "attach_regen_final_completion_audit=attach_regen_final_completion_audit,\n",
        "attach_regen_final_completion_audit=attach_regen_final_completion_audit,\n\n"
        "            attach_regen_final_verification_audit=attach_regen_final_verification_audit,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_final_verification_audit=None" not in text:
    text = text.replace(
        "attach_regen_final_completion_audit=None,\n",
        "attach_regen_final_completion_audit=None,\n\n"
        "        attach_regen_final_verification_audit=None,\n",
    )

if '"regen_final_verification_audit"' not in text:
    text = text.replace(
        '(\n            "regen_final_completion_audit",\n            attach_regen_final_completion_audit,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_final_completion_audit",\n            attach_regen_final_completion_audit,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_final_verification_audit",\n            attach_regen_final_verification_audit,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16M2_FINAL_REGEN_VERIFICATION_AUDIT_INTEGRATED")
