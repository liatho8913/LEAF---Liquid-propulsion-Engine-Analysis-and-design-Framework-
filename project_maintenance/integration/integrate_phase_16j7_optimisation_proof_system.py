from pathlib import Path

ROOT = Path.cwd()
LEAF = ROOT / "leaf_qt"

(LEAF / "regen_optimisation_proof_system.py").write_text(r'''"""
PHASE 16J.7 — Optimisation Proof System

Purpose:
- Prove the optimisation chain has enough evidence to be trusted.
- Verify generation, ranking, recommendation, acceptance, commit, regeneration,
  comparison, explanation, and root-cause systems exist.
- Produce a proof ledger.
- Does not modify geometry.
- Does not rerun solver.
"""

PASS_STATUS = "PASS_REGEN_OPTIMISATION_PROOF_SYSTEM_PHASE_16J7"
FAIL_STATUS = "FAIL_REGEN_OPTIMISATION_PROOF_SYSTEM_PHASE_16J7"

PROOF_CHECKS = (
    ("candidate_population_exists", "regen_candidate_ranking_input_population"),
    ("ranking_best_candidate_exists", "regen_candidate_ranking_best_candidate"),
    ("recommendation_exists", "regen_candidate_recommendation"),
    ("viewer_payload_exists", "regen_recommendation_viewer_payload"),
    ("selection_trace_exists", "regen_end_to_end_candidate_selection_trace"),
    ("acceptance_payload_exists", "regen_candidate_acceptance_pending_application_payload"),
    ("commit_approval_exists", "regen_pending_geometry_commit_approval_payload"),
    ("live_commit_audit_exists", "regen_live_geometry_commit_audit_record"),
    ("solver_regeneration_audit_exists", "regen_solver_regeneration_audit_record"),
    ("comparison_report_exists", "regen_before_after_solver_comparison_report_payload"),
    ("history_event_exists", "regen_design_iteration_history_event"),
    ("completion_gate_exists", "regen_candidate_acceptance_completion_gate_payload"),
    ("recommendation_explanation_exists", "regen_recommendation_explanation_payload"),
    ("failure_root_cause_exists", "regen_failure_root_cause_payload"),
)


def attach_regen_optimisation_proof_system(results):
    if not isinstance(results, dict):
        return results

    blockers = []

    if results.get("phase_16j6_complete") is not True:
        blockers.append("Phase 16J.6 failure root cause system has not passed.")

    proof_ledger = []

    for check_name, key in PROOF_CHECKS:
        payload = results.get(key)
        passed = payload is not None and payload != {} and payload != []
        proof_ledger.append({
            "check": check_name,
            "key": key,
            "passed": passed,
            "evidence_type": type(payload).__name__ if payload is not None else None,
        })
        if not passed:
            blockers.append(f"Proof check failed: {check_name} missing key {key}")

    candidate_id_status = _candidate_id_consistency(results)
    proof_ledger.append(candidate_id_status)

    if not candidate_id_status["passed"]:
        blockers.append(candidate_id_status["message"])

    trust_score = _trust_score(proof_ledger)
    status = PASS_STATUS if not blockers else FAIL_STATUS

    payload = None
    if status == PASS_STATUS:
        payload = {
            "status": status,
            "visibility": "REPORT_ONLY",
            "source_phase": "16J.7",
            "proof_state": "OPTIMISATION_CHAIN_PROVEN",
            "trust_score": trust_score,
            "proof_ledger": proof_ledger,
            "candidate_id": candidate_id_status.get("candidate_id"),
            "next_phase": "16J.8 Optimisation Completion Gate",
        }

    report = _build_report(status, blockers, payload, proof_ledger, trust_score)

    results["regen_optimisation_proof_system_complete"] = True
    results["phase_16j7_complete"] = status == PASS_STATUS
    results["regen_optimisation_proof_system_status"] = status
    results["phase_16j7_status"] = status
    results["regen_optimisation_proof_system_blockers"] = blockers
    results["regen_optimisation_proof_payload"] = payload
    results["regen_optimisation_proof_ledger"] = proof_ledger
    results["regen_optimisation_proof_trust_score"] = trust_score
    results["regen_optimisation_proof_report"] = report
    results["regen_optimisation_proof_visibility"] = "REPORT_ONLY"

    results["phase_16j8_optimisation_completion_gate_allowed"] = status == PASS_STATUS

    return results


def _candidate_id_consistency(results):
    ids = []

    for key in (
        "regen_geometry_active_candidate_id",
        "regen_candidate_pending_application_candidate_id",
    ):
        value = results.get(key)
        if value:
            ids.append(value)

    for key in (
        "regen_recommendation_viewer_payload",
        "regen_candidate_acceptance_history_event",
        "regen_live_geometry_commit_audit_record",
        "regen_solver_regeneration_audit_record",
        "regen_before_after_solver_comparison_report_payload",
        "regen_design_iteration_history_event",
        "regen_candidate_acceptance_completion_gate_payload",
        "regen_recommendation_explanation_payload",
    ):
        payload = results.get(key)
        if isinstance(payload, dict) and payload.get("candidate_id"):
            ids.append(payload.get("candidate_id"))

    unique = sorted(set(ids))

    return {
        "check": "candidate_id_consistency",
        "key": "multiple_candidate_id_sources",
        "passed": len(unique) == 1,
        "candidate_id": unique[0] if len(unique) == 1 else None,
        "message": "Candidate ID is consistent." if len(unique) == 1 else f"Candidate ID mismatch: {unique}",
        "evidence_type": "candidate_id_trace",
    }


def _trust_score(ledger):
    if not ledger:
        return 0.0
    passed = sum(1 for item in ledger if item.get("passed") is True)
    return round(passed / len(ledger), 4)


def _build_report(status, blockers, payload, ledger, trust_score):
    lines = [
        "LEAF PHASE 16J.7 OPTIMISATION PROOF SYSTEM",
        "============================================",
        "",
        f"Status: {status}",
        f"Trust score: {trust_score}",
        "",
        "Scope:",
        "- Verifies evidence across the optimisation chain.",
        "- Produces a proof ledger.",
        "- Checks candidate ID consistency.",
        "- Does not modify geometry.",
        "- Does not rerun solver.",
        "",
        "Blocking Reasons:",
    ]

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- None.")

    lines.extend(["", "Proof Ledger:"])

    for item in ledger:
        lines.append(
            f"- {item.get('check')}: {'PASS' if item.get('passed') else 'FAIL'} "
            f"({item.get('key')})"
        )

    lines.extend([
        "",
        "Proof Result:",
        f"- Proven: {bool(payload)}",
        "- Visibility: REPORT_ONLY",
        "",
        "Next Required Phase:",
        "- 16J.8 Optimisation Completion Gate.",
    ])

    return "\n".join(lines)
''')

(ROOT / "project_maintenance/relocated_production_tests/programme_46g_residual_reference_rewrite/leaf_qt/test_regen_optimisation_proof_system_phase_16j7.py").write_text(r'''from regen_ranking_owner_source_repair import attach_regen_ranking_owner_source_repair
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
    ):
        results = fn(results)

    assert results["phase_16j7_complete"] is True
    assert results["phase_16j7_status"] == "PASS_REGEN_OPTIMISATION_PROOF_SYSTEM_PHASE_16J7"

    payload = results["regen_optimisation_proof_payload"]
    assert payload["proof_state"] == "OPTIMISATION_CHAIN_PROVEN"
    assert payload["candidate_id"] == "CANDIDATE_A"
    assert payload["trust_score"] == 1.0

    ledger = results["regen_optimisation_proof_ledger"]
    assert all(item["passed"] is True for item in ledger)

    report = results["regen_optimisation_proof_report"]
    assert "OPTIMISATION PROOF SYSTEM" in report
    assert "Proof Ledger" in report

    assert results["phase_16j8_optimisation_completion_gate_allowed"] is True

    print("PASS_REGEN_OPTIMISATION_PROOF_SYSTEM_PHASE_16J7")


if __name__ == "__main__":
    main()
''')

controller = LEAF / "foundation_layer_controller.py"
text = controller.read_text()

if "from regen_optimisation_proof_system import attach_regen_optimisation_proof_system" not in text:
    anchor = (
        "try:\n"
        "    from regen_failure_root_cause_system import attach_regen_failure_root_cause_system\n"
        "except Exception:\n"
        "    attach_regen_failure_root_cause_system = None\n"
    )
    text = text.replace(
        anchor,
        anchor + "\n"
        "try:\n"
        "    from regen_optimisation_proof_system import attach_regen_optimisation_proof_system\n"
        "except Exception:\n"
        "    attach_regen_optimisation_proof_system = None\n"
    )

if "attach_regen_optimisation_proof_system=attach_regen_optimisation_proof_system" not in text:
    text = text.replace(
        "attach_regen_failure_root_cause_system=attach_regen_failure_root_cause_system,\n",
        "attach_regen_failure_root_cause_system=attach_regen_failure_root_cause_system,\n\n"
        "            attach_regen_optimisation_proof_system=attach_regen_optimisation_proof_system,\n",
    )

controller.write_text(text)

pipeline = LEAF / "foundation_attachment_pipeline.py"
text = pipeline.read_text()

if "attach_regen_optimisation_proof_system=None" not in text:
    text = text.replace(
        "attach_regen_failure_root_cause_system=None,\n",
        "attach_regen_failure_root_cause_system=None,\n\n"
        "        attach_regen_optimisation_proof_system=None,\n",
    )

if '"regen_optimisation_proof_system"' not in text:
    text = text.replace(
        '(\n            "regen_failure_root_cause_system",\n            attach_regen_failure_root_cause_system,\n            (),\n            {},\n        ),\n',
        '(\n            "regen_failure_root_cause_system",\n            attach_regen_failure_root_cause_system,\n            (),\n            {},\n        ),\n\n'
        '        (\n            "regen_optimisation_proof_system",\n            attach_regen_optimisation_proof_system,\n            (),\n            {},\n        ),\n',
    )

pipeline.write_text(text)

print("PHASE_16J7_OPTIMISATION_PROOF_SYSTEM_INTEGRATED")
