from __future__ import annotations

from leaf_qt.real_engine_benchmark_master_gate import (
    attach_real_engine_benchmark_master_gate,
    evaluate_real_engine_benchmark_master_gate,
)


VALID_RESULTS = {
    "stage_v_scalability_complete": True,

    "stage_w1_real_engine_benchmarking_framework_complete": True,
    "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
    "real_engine_benchmarking_framework_text": "W.1 report",

    "stage_w2_public_benchmark_source_ownership_complete": True,
    "real_engine_benchmark_source_owner_status": "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
    "real_engine_benchmark_source_owner_text": "W.2 report",

    "stage_w3_numeric_benchmark_band_ownership_complete": True,
    "real_engine_benchmark_band_owner_status": "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER",
    "real_engine_benchmark_band_owner_text": "W.3 report",

    "stage_w4_real_engine_benchmark_failure_ownership_complete": True,
    "real_engine_benchmark_failure_owner_status": "PASS_REAL_ENGINE_BENCHMARK_FAILURE_OWNER",
    "real_engine_benchmark_failure_owner_text": "W.4 report",

    "real_engine_benchmark_reference_engine": "RL10",
    "real_engine_benchmark_source_owner_confidence": "PUBLIC_ORDER_OF_MAGNITUDE",
    "real_engine_benchmark_band_owner_rows": [{"name": "RL10"}],
}


def test_phase_16t3k2_preserves_legacy_pass_contract() -> None:
    payload = evaluate_real_engine_benchmark_master_gate(dict(VALID_RESULTS))

    assert payload["real_engine_benchmark_master_gate_status"] == "PASS_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    assert payload["real_engine_benchmark_master_gate_pass_allowed"] is True
    assert payload["stage_w5_real_engine_benchmark_master_gate_complete"] is True


def test_phase_16t3k2_adds_structured_findings_and_global_pass() -> None:
    payload = evaluate_real_engine_benchmark_master_gate(dict(VALID_RESULTS))

    assert payload["real_engine_benchmark_master_gate_structured_findings"]
    assert payload["real_engine_benchmark_master_gate_global_status"] == "PASS"
    assert payload["real_engine_benchmark_master_gate_global_status_payload"]["passed"] is True
    assert "Global Status Engine" in payload["real_engine_benchmark_master_gate_text"]


def test_phase_16t3k2_warning_review_escalates_to_blocked_in_production_gate() -> None:
    data = dict(VALID_RESULTS)
    data["real_engine_benchmark_band_owner_status"] = "WARN_REAL_ENGINE_BENCHMARK_BAND_OWNER_LIMITED_PUBLIC_DATA"

    payload = evaluate_real_engine_benchmark_master_gate(data)

    assert payload["real_engine_benchmark_master_gate_status"] == "WARN_REAL_ENGINE_BENCHMARK_MASTER_GATE_REVIEW_REQUIRED"
    assert payload["real_engine_benchmark_master_gate_pass_allowed"] is False
    assert payload["real_engine_benchmark_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k2_blocking_failure_maps_to_fail() -> None:
    data = dict(VALID_RESULTS)
    data["real_engine_benchmark_failure_owner_status"] = "FAIL_REAL_ENGINE_BENCHMARK_FAILURE_OWNER"

    payload = evaluate_real_engine_benchmark_master_gate(data)

    assert payload["real_engine_benchmark_master_gate_status"] == "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    assert payload["real_engine_benchmark_master_gate_pass_allowed"] is False
    assert payload["real_engine_benchmark_master_gate_global_status"] == "FAIL"


def test_phase_16t3k2_missing_dependency_maps_to_blocked() -> None:
    data = dict(VALID_RESULTS)
    data["stage_v_scalability_complete"] = False

    payload = evaluate_real_engine_benchmark_master_gate(data)

    assert payload["real_engine_benchmark_master_gate_status"] == "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    assert payload["real_engine_benchmark_master_gate_pass_allowed"] is False
    assert payload["real_engine_benchmark_master_gate_global_status"] == "BLOCKED"


def test_phase_16t3k2_attach_preserves_mutating_contract() -> None:
    data = dict(VALID_RESULTS)
    returned = attach_real_engine_benchmark_master_gate(data)

    assert returned is data
    assert data["real_engine_benchmark_master_gate_status"] == "PASS_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    assert data["real_engine_benchmark_master_gate_global_status"] == "PASS"
