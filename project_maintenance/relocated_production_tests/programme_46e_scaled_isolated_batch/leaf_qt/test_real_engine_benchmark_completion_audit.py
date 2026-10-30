from real_engine_benchmark_completion_audit import (
    attach_real_engine_benchmark_completion_audit,
)


def _clean_results():
    return {
        "stage_v_scalability_complete": True,

        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": True,
        "stage_w3_numeric_benchmark_band_ownership_complete": True,
        "stage_w4_real_engine_benchmark_failure_ownership_complete": True,
        "stage_w5_real_engine_benchmark_master_gate_complete": True,

        "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
        "real_engine_benchmark_source_owner_status": "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
        "real_engine_benchmark_band_owner_status": "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER",
        "real_engine_benchmark_failure_owner_status": "PASS_REAL_ENGINE_BENCHMARK_FAILURE_OWNERSHIP",
        "real_engine_benchmark_master_gate_status": "PASS_REAL_ENGINE_BENCHMARK_MASTER_GATE",

        "real_engine_benchmarking_framework_text": "framework report",
        "real_engine_benchmark_source_owner_text": "source owner report",
        "real_engine_benchmark_band_owner_text": "band owner report",
        "real_engine_benchmark_failure_owner_text": "failure owner report",
        "real_engine_benchmark_master_gate_text": "master gate report",

        "real_engine_benchmark_master_gate_pass_allowed": True,
        "real_engine_benchmark_reference_engine": "Merlin_1D",
    }


def test_completion_audit_passes_clean_stage_w_chain():
    results = _clean_results()

    attach_real_engine_benchmark_completion_audit(results)

    assert results["real_engine_benchmark_completion_audit_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    )
    assert results["stage_w_real_engine_benchmarking_complete"] is True
    assert results["stage_w_complete"] is True
    assert results["stage_w6_real_engine_benchmark_completion_audit_complete"] is True


def test_completion_audit_blocks_missing_master_gate():
    results = _clean_results()
    results["stage_w5_real_engine_benchmark_master_gate_complete"] = False

    attach_real_engine_benchmark_completion_audit(results)

    assert results["real_engine_benchmark_completion_audit_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    )
    assert results["stage_w_real_engine_benchmarking_complete"] is False


def test_completion_audit_blocks_failed_band_status():
    results = _clean_results()
    results["stage_w3_numeric_benchmark_band_ownership_complete"] = False
    results["real_engine_benchmark_band_owner_status"] = (
        "FAIL_REAL_ENGINE_BENCHMARK_BAND_OWNER"
    )

    attach_real_engine_benchmark_completion_audit(results)

    assert results["real_engine_benchmark_completion_audit_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    )

    text = "\n".join(results["real_engine_benchmark_completion_audit_blocking_reasons"])
    assert "W.3 numeric band owner status" in text


def test_completion_audit_blocks_missing_report_text():
    results = _clean_results()
    results.pop("real_engine_benchmark_source_owner_text")

    attach_real_engine_benchmark_completion_audit(results)

    assert results["real_engine_benchmark_completion_audit_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    )

    text = "\n".join(results["real_engine_benchmark_completion_audit_blocking_reasons"])
    assert "W.2 source owner report is missing" in text


def test_completion_audit_blocks_review_status():
    results = _clean_results()
    results["real_engine_benchmark_band_owner_status"] = (
        "WARN_REAL_ENGINE_BENCHMARK_BAND_OWNER_REVIEW_REQUIRED"
    )

    attach_real_engine_benchmark_completion_audit(results)

    assert results["real_engine_benchmark_completion_audit_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT"
    )
    assert results["stage_w_real_engine_benchmarking_complete"] is False