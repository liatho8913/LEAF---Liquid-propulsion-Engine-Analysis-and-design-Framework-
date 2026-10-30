from real_engine_benchmark_source_owner import attach_real_engine_benchmark_source_owner
from real_engine_benchmark_band_owner import attach_real_engine_benchmark_band_owner


def _base_results():
    return {
        "public_benchmark_data_available": True,
        "real_engine_benchmark_source_count": 2,
    }


def test_benchmark_band_owner_passes_default_foundation_case():
    results = _base_results()

    attach_real_engine_benchmark_source_owner(results)
    attach_real_engine_benchmark_band_owner(results)

    assert results["real_engine_benchmark_band_owner_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER"
    )
    assert results["stage_w3_numeric_benchmark_band_ownership_complete"] is True


def test_benchmark_band_owner_passes_in_band_metric():
    results = _base_results()
    results.update({
        "thrust": 100000,
        "benchmark_thrust": 105000,
        "real_engine_benchmark_tolerance_fraction": 0.10,
    })

    attach_real_engine_benchmark_source_owner(results)
    attach_real_engine_benchmark_band_owner(results)

    assert results["real_engine_benchmark_band_owner_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER"
    )
    assert results["real_engine_benchmark_band_owner_rows"][0]["status"] == "IN_BAND"


def test_benchmark_band_owner_blocks_out_of_band_metric():
    results = _base_results()
    results.update({
        "thrust": 100000,
        "benchmark_thrust": 200000,
        "real_engine_benchmark_tolerance_fraction": 0.10,
    })

    attach_real_engine_benchmark_source_owner(results)
    attach_real_engine_benchmark_band_owner(results)

    assert results["real_engine_benchmark_band_owner_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_BAND_OWNER"
    )
    assert results["stage_w3_numeric_benchmark_band_ownership_complete"] is False


def test_benchmark_band_owner_blocks_low_confidence_source():
    results = _base_results()
    results["real_engine_benchmark_source_confidence"] = 0.2

    attach_real_engine_benchmark_source_owner(results)
    attach_real_engine_benchmark_band_owner(results)

    assert results["real_engine_benchmark_band_owner_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_BAND_OWNER"
    )