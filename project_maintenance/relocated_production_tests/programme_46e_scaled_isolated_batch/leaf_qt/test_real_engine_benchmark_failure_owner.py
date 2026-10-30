from real_engine_benchmark_failure_owner import (
    attach_real_engine_benchmark_failure_owner,
)


def test_failure_owner_reports_no_failure_for_clean_stage_w_inputs():
    results = {
        "stage_v_scalability_complete": True,
        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": True,
        "stage_w3_numeric_benchmark_band_ownership_complete": True,
        "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
        "real_engine_benchmark_source_owner_status": "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
        "real_engine_benchmark_band_owner_status": "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER",
        "real_engine_benchmark_reference_engine": "Merlin_1D",
    }

    attach_real_engine_benchmark_failure_owner(results)

    assert results["real_engine_benchmark_failure_owner_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_FAILURE_OWNERSHIP"
    )
    assert results["stage_w4_real_engine_benchmark_failure_ownership_complete"] is True
    assert results["real_engine_benchmark_failure_root_causes"] == [
        "No Stage W benchmark failure causes detected."
    ]


def test_failure_owner_separates_source_confidence_failure():
    results = {
        "stage_v_scalability_complete": True,
        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": False,
        "stage_w3_numeric_benchmark_band_ownership_complete": True,
        "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
        "real_engine_benchmark_source_owner_status": "FAIL_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
        "real_engine_benchmark_source_owner_blocking_reasons": [
            "Public benchmark source confidence is below the minimum threshold for Stage W benchmarking."
        ],
        "real_engine_benchmark_source_owner_confidence": 0.3,
        "real_engine_benchmark_band_owner_status": "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER",
    }

    attach_real_engine_benchmark_failure_owner(results)

    categories = results["real_engine_benchmark_failure_categories"]
    root_causes = "\n".join(results["real_engine_benchmark_failure_root_causes"])

    assert "SOURCE_CONFIDENCE" in categories
    assert "below the minimum threshold" in root_causes
    assert results["stage_w4_real_engine_benchmark_failure_ownership_complete"] is True


def test_failure_owner_separates_numeric_band_failure():
    results = {
        "stage_v_scalability_complete": True,
        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": True,
        "stage_w3_numeric_benchmark_band_ownership_complete": False,
        "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
        "real_engine_benchmark_source_owner_status": "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
        "real_engine_benchmark_band_owner_status": "FAIL_REAL_ENGINE_BENCHMARK_BAND_OWNER",
        "real_engine_benchmark_band_owner_blocking_reasons": [
            "One or more real-engine benchmark metrics are outside the accepted public-data band."
        ],
        "real_engine_benchmark_band_owner_rows": [
            {
                "metric": "thrust",
                "predicted": 100000.0,
                "reference": 200000.0,
                "status": "OUT_OF_BAND",
            }
        ],
    }

    attach_real_engine_benchmark_failure_owner(results)

    categories = results["real_engine_benchmark_failure_categories"]
    root_causes = "\n".join(results["real_engine_benchmark_failure_root_causes"])

    assert "NUMERIC_BAND" in categories
    assert "outside the accepted public-data band" in root_causes
    assert "Out-of-band rows: 1" in results["real_engine_benchmark_failure_evidence"]