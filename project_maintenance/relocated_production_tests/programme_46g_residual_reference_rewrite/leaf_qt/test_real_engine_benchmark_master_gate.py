from real_engine_benchmark_master_gate import (
    attach_real_engine_benchmark_master_gate,
)


def _clean_results():
    return {
        "stage_v_scalability_complete": True,

        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": True,
        "stage_w3_numeric_benchmark_band_ownership_complete": True,
        "stage_w4_real_engine_benchmark_failure_ownership_complete": True,

        "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
        "real_engine_benchmark_source_owner_status": "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
        "real_engine_benchmark_band_owner_status": "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER",
        "real_engine_benchmark_failure_owner_status": "PASS_REAL_ENGINE_BENCHMARK_FAILURE_OWNERSHIP",

        "real_engine_benchmarking_framework_text": "framework report",
        "real_engine_benchmark_source_owner_text": "source report",
        "real_engine_benchmark_band_owner_text": "band report",
        "real_engine_benchmark_failure_owner_text": "failure report",

        "real_engine_benchmark_reference_engine": "Merlin_1D",
    }


def test_master_gate_passes_clean_stage_w_chain():
    results = _clean_results()

    attach_real_engine_benchmark_master_gate(results)

    assert results["real_engine_benchmark_master_gate_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    )
    assert results["real_engine_benchmark_master_gate_pass_allowed"] is True
    assert results["stage_w5_real_engine_benchmark_master_gate_complete"] is True


def test_master_gate_blocks_incomplete_stage_v():
    results = _clean_results()
    results["stage_v_scalability_complete"] = False

    attach_real_engine_benchmark_master_gate(results)

    assert results["real_engine_benchmark_master_gate_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    )
    assert results["stage_w5_real_engine_benchmark_master_gate_complete"] is False


def test_master_gate_blocks_source_failure():
    results = _clean_results()
    results["stage_w2_public_benchmark_source_ownership_complete"] = False
    results["real_engine_benchmark_source_owner_status"] = (
        "FAIL_REAL_ENGINE_BENCHMARK_SOURCE_OWNER"
    )

    attach_real_engine_benchmark_master_gate(results)

    assert results["real_engine_benchmark_master_gate_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    )

    text = "\n".join(results["real_engine_benchmark_master_gate_blocking_reasons"])
    assert "W.2 public source ownership" in text


def test_master_gate_blocks_numeric_band_failure():
    results = _clean_results()
    results["stage_w3_numeric_benchmark_band_ownership_complete"] = False
    results["real_engine_benchmark_band_owner_status"] = (
        "FAIL_REAL_ENGINE_BENCHMARK_BAND_OWNER"
    )

    attach_real_engine_benchmark_master_gate(results)

    assert results["real_engine_benchmark_master_gate_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    )

    text = "\n".join(results["real_engine_benchmark_master_gate_blocking_reasons"])
    assert "W.3 numeric benchmark band ownership" in text


def test_master_gate_blocks_missing_report_text():
    results = _clean_results()
    results.pop("real_engine_benchmark_band_owner_text")

    attach_real_engine_benchmark_master_gate(results)

    assert results["real_engine_benchmark_master_gate_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_MASTER_GATE"
    )

    text = "\n".join(results["real_engine_benchmark_master_gate_blocking_reasons"])
    assert "report is missing" in text