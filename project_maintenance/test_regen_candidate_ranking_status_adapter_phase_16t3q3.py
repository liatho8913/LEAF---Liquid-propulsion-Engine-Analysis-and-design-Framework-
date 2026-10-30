from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
LEAF_QT = ROOT / "leaf_qt"

if str(LEAF_QT) not in sys.path:
    sys.path.insert(0, str(LEAF_QT))

from regen_candidate_ranking_master_gate import build_regen_candidate_ranking_master_gate


PASS_STATUS = "PASS_REGEN_CANDIDATE_RANKING_MASTER_GATE_PHASE_11B4F"
FAIL_STATUS = "FAIL_REGEN_CANDIDATE_RANKING_MASTER_GATE_PHASE_11B4F"
ADAPTER_STATUS = "PASS_REGEN_CANDIDATE_RANKING_STATUS_ADAPTER_PHASE_16T3Q3"


def valid_results():
    ranked = [
        {
            "candidate_id": "RPOP-G0-0001",
            "rank": 1,
            "score": 99.0,
            "selected": True,
        },
        {
            "candidate_id": "RPOP-G0-0002",
            "rank": 2,
            "score": 91.0,
            "selected": False,
        },
    ]

    return {
        "phase_11b_4a_regen_candidate_ranking_input_audit_complete": True,
        "phase_11b_4b_regen_candidate_ranking_owner_complete": True,
        "phase_11b_4c_regen_candidate_ranking_report_owner_complete": True,
        "phase_11b_4d_regen_candidate_ranking_registration_owner_complete": True,
        "phase_11b_4e_regen_candidate_ranking_completion_audit_complete": True,

        "regen_candidate_ranked_population": ranked,
        "regen_candidate_ranked_population_count": len(ranked),
        "regen_candidate_best_candidate": ranked[0],
        "regen_candidate_ranking_statistics": {
            "candidate_count": len(ranked),
            "best_score": 99.0,
        },
        "regen_candidate_ranking_status": "PASS_REGEN_CANDIDATE_RANKING_OWNER_PHASE_11B4B",

        "regen_candidate_ranking_report_bundle": {
            "ready": True,
            "report_key": "regen_candidate_ranking_report",
        },
        "regen_candidate_ranking_export_bundle": {
            "ready": True,
        },
        "regen_candidate_ranking_registry_entry": {
            "registered": True,
        },
        "regen_candidate_ranking_report_registry": {
            "registered_report_keys": ["regen_candidate_ranking_report"],
        },
        "regen_candidate_ranking_viewer_registry": {
            "viewer_report_keys": ["regen_candidate_ranking_report"],
        },
        "regen_candidate_ranking_export_registry": {
            "export_report_keys": ["regen_candidate_ranking_report"],
        },

        "regen_candidate_ranking_completion_audit_ready": True,
        "regen_candidate_ranking_completion_audit_status": "PASS_REGEN_CANDIDATE_RANKING_COMPLETION_AUDIT_PHASE_11B4E",
        "regen_candidate_ranking_completion_audit_failed_checks": [],
        "regen_candidate_ranking_completion_audit_report": "completion audit ready",

        "regen_candidate_ranking_completion_audit_mutation_executed": False,
        "regen_candidate_ranking_completion_audit_evolution_executed": False,
        "regen_candidate_ranking_completion_audit_solver_executed": False,
        "regen_candidate_ranking_completion_audit_live_commit_executed": False,
        "regen_candidate_ranking_completion_audit_candidate_acceptance_executed": False,
        "regen_candidate_runtime_mutation_allowed": False,
        "regen_candidate_runtime_evolution_allowed": False,
        "regen_candidate_runtime_solver_allowed": False,
        "regen_candidate_runtime_live_commit_allowed": False,
        "regen_candidate_runtime_acceptance_allowed": False,
    }


def assert_adapter_payload(payload):
    assert payload["phase_16t3q3_status_adapter_complete"] is True
    assert payload["phase_16t3q3_regen_candidate_ranking_status_adapter_complete"] is True
    assert payload["regen_candidate_ranking_status_adapter_complete"] is True
    assert payload["regen_candidate_ranking_status_adapter_status"] == ADAPTER_STATUS

    assert isinstance(payload["regen_candidate_ranking_master_gate_structured_findings"], list)
    assert isinstance(payload["regen_candidate_ranking_master_gate_global_status"], str)
    assert isinstance(payload["regen_candidate_ranking_master_gate_global_status_payload"], dict)
    assert isinstance(payload["regen_candidate_ranking_master_gate_adapter_report"], str)

    assert payload["structured_findings"] == payload["regen_candidate_ranking_master_gate_structured_findings"]
    assert payload["global_status"] == payload["regen_candidate_ranking_master_gate_global_status"]
    assert payload["global_status_payload"] == payload["regen_candidate_ranking_master_gate_global_status_payload"]
    assert payload["adapter_report"] == payload["regen_candidate_ranking_master_gate_adapter_report"]

    report = payload["regen_candidate_ranking_master_gate_adapter_report"]
    assert "LEAF PHASE 16T.3Q.3 STATUS ADAPTER" in report
    assert "Compatibility:" in report


def test_successful_ranking_passes_with_adapter():
    payload = build_regen_candidate_ranking_master_gate(valid_results())

    assert payload["regen_candidate_ranking_master_gate_status"] == PASS_STATUS
    assert payload["regen_candidate_ranking_master_gate_ready"] is True
    assert payload["regen_candidate_ranking_master_gate_global_status"] == "PASS"
    assert payload["regen_candidate_ranking_master_gate_legacy_status"] == PASS_STATUS
    assert_adapter_payload(payload)


def test_empty_ranking_fails_with_structured_finding():
    results = valid_results()
    results["regen_candidate_ranked_population"] = []
    results["regen_candidate_ranked_population_count"] = 0

    payload = build_regen_candidate_ranking_master_gate(results)

    assert payload["regen_candidate_ranking_master_gate_status"] == FAIL_STATUS
    assert payload["regen_candidate_ranking_master_gate_global_status"] == "FAIL"

    codes = {f["code"] for f in payload["regen_candidate_ranking_master_gate_structured_findings"]}
    assert "RANKED_POPULATION_EMPTY" in codes
    assert_adapter_payload(payload)


def test_missing_best_candidate_fails():
    results = valid_results()
    results["regen_candidate_best_candidate"] = {}

    payload = build_regen_candidate_ranking_master_gate(results)

    assert payload["regen_candidate_ranking_master_gate_status"] == FAIL_STATUS
    assert payload["regen_candidate_ranking_master_gate_global_status"] == "FAIL"

    codes = {f["code"] for f in payload["regen_candidate_ranking_master_gate_structured_findings"]}
    assert "BEST_CANDIDATE_MISSING" in codes


def test_duplicate_winner_fails():
    results = valid_results()
    results["regen_candidate_ranked_population"][1]["selected"] = True

    payload = build_regen_candidate_ranking_master_gate(results)

    assert payload["regen_candidate_ranking_master_gate_global_status"] == "FAIL"

    codes = {f["code"] for f in payload["regen_candidate_ranking_master_gate_structured_findings"]}
    assert "DUPLICATE_WINNER_CANDIDATES" in codes


def test_invalid_score_fails():
    results = valid_results()
    results["regen_candidate_ranked_population"][0]["score"] = -1.0

    payload = build_regen_candidate_ranking_master_gate(results)

    assert payload["regen_candidate_ranking_master_gate_global_status"] == "FAIL"

    codes = {f["code"] for f in payload["regen_candidate_ranking_master_gate_structured_findings"]}
    assert "INVALID_RANKING_SCORE" in codes


def test_missing_statistics_requires_review_or_failure():
    results = valid_results()
    results["regen_candidate_ranking_statistics"] = {}

    payload = build_regen_candidate_ranking_master_gate(results)

    assert payload["regen_candidate_ranking_master_gate_global_status"] in {
        "REVIEW_REQUIRED",
        "FAIL",
    }

    codes = {f["code"] for f in payload["regen_candidate_ranking_master_gate_structured_findings"]}
    assert "RANKING_STATISTICS_MISSING" in codes


def test_missing_report_bundle_fails():
    results = valid_results()
    results["regen_candidate_ranking_report_bundle"] = {}

    payload = build_regen_candidate_ranking_master_gate(results)

    assert payload["regen_candidate_ranking_master_gate_global_status"] == "FAIL"

    codes = {f["code"] for f in payload["regen_candidate_ranking_master_gate_structured_findings"]}
    assert "RANKING_REPORT_BUNDLE_NOT_READY" in codes


def test_backwards_compatibility_fields_preserved():
    payload = build_regen_candidate_ranking_master_gate(valid_results())

    legacy_fields = [
        "regen_candidate_ranking_master_gate_complete",
        "phase_11b_4f_regen_candidate_ranking_master_gate_complete",
        "regen_candidate_ranking_master_gate_ready",
        "regen_candidate_ranking_master_gate_status",
        "regen_candidate_ranking_master_gate_checks",
        "regen_candidate_ranking_master_gate_failed_checks",
        "regen_candidate_ranking_master_gate_report",
        "regen_candidate_ranking_architecture_complete",
        "phase_11b_4_candidate_ranking_architecture_complete",
        "regen_ranking_master_gate_complete",
        "regen_ranking_master_gate_ready",
        "regen_ranking_master_gate_status",
        "regen_ranking_master_gate_report",
        "regen_candidate_mutation_architecture_allowed",
        "phase_11b_5_candidate_mutation_architecture_allowed",
        "regen_candidate_runtime_mutation_allowed",
        "regen_candidate_runtime_evolution_allowed",
        "regen_candidate_runtime_solver_allowed",
        "regen_candidate_runtime_live_commit_allowed",
        "regen_candidate_runtime_acceptance_allowed",
    ]

    for field in legacy_fields:
        assert field in payload, field

    assert payload["regen_candidate_ranking_master_gate_status"] == PASS_STATUS
    assert payload["regen_ranking_master_gate_status"] == PASS_STATUS


def run_all():
    test_successful_ranking_passes_with_adapter()
    test_empty_ranking_fails_with_structured_finding()
    test_missing_best_candidate_fails()
    test_duplicate_winner_fails()
    test_invalid_score_fails()
    test_missing_statistics_requires_review_or_failure()
    test_missing_report_bundle_fails()
    test_backwards_compatibility_fields_preserved()

    print("PASS_REGEN_CANDIDATE_RANKING_STATUS_ADAPTER_PHASE_16T3Q3")
    return True


if __name__ == "__main__":
    run_all()
