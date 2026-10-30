from project_maintenance.production_historical_artifacts.leaf_qt.real_engine_benchmark_final_regression import (
    attach_real_engine_benchmark_final_regression,
)


def _clean_results():
    return {
        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": True,
        "stage_w3_numeric_benchmark_band_ownership_complete": True,
        "stage_w4_real_engine_benchmark_failure_ownership_complete": True,
        "stage_w5_real_engine_benchmark_master_gate_complete": True,
        "stage_w6_real_engine_benchmark_completion_audit_complete": True,
        "stage_w_real_engine_benchmarking_complete": True,

        "real_engine_benchmarking_framework_text": "W1",
        "real_engine_benchmark_source_owner_text": "W2",
        "real_engine_benchmark_band_owner_text": "W3",
        "real_engine_benchmark_failure_owner_text": "W4",
        "real_engine_benchmark_master_gate_text": "W5",
        "real_engine_benchmark_completion_audit_text": "W6",

        "real_engine_benchmark_completion_audit_status": (
            "PASS_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
        ),
        "real_engine_benchmark_reference_engine": "Merlin_1D",
    }


def test_final_regression_passes_clean_stage_w_chain():
    results = _clean_results()

    attach_real_engine_benchmark_final_regression(results)

    assert results["real_engine_benchmark_final_regression_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_FINAL_REGRESSION"
    )
    assert results["stage_w7_real_engine_benchmark_final_regression_complete"] is True


def test_final_regression_blocks_missing_report():
    results = _clean_results()
    results.pop("real_engine_benchmark_band_owner_text")

    attach_real_engine_benchmark_final_regression(results)

    assert results["real_engine_benchmark_final_regression_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_FINAL_REGRESSION"
    )
    assert results["stage_w7_real_engine_benchmark_final_regression_complete"] is False


def test_final_regression_blocks_failed_completion_audit():
    results = _clean_results()
    results["real_engine_benchmark_completion_audit_status"] = (
        "FAIL_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    )

    attach_real_engine_benchmark_final_regression(results)

    assert results["real_engine_benchmark_final_regression_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_FINAL_REGRESSION"
    )