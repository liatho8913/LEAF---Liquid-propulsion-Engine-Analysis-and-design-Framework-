from real_engine_benchmark_source_owner import (
    evaluate_real_engine_benchmark_source_owner,
)


def test_real_engine_benchmark_source_owner_passes_default_public_case():
    results = {
        "public_benchmark_data_available": True,
        "real_engine_benchmark_source_count": 2,
    }

    audit = evaluate_real_engine_benchmark_source_owner(results)

    assert audit["real_engine_benchmark_source_owner_status"] == (
        "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER"
    )
    assert audit["stage_w1_real_engine_benchmark_source_owner_complete"] is True
    assert audit["real_engine_benchmark_source_owner_quality"] in {
        "ACCEPTABLE_PUBLIC_SOURCE",
        "HIGH_CONFIDENCE_PUBLIC_SOURCE",
    }


def test_real_engine_benchmark_source_owner_blocks_low_confidence():
    results = {
        "public_benchmark_data_available": True,
        "real_engine_benchmark_source_confidence": 0.3,
        "real_engine_benchmark_source_count": 1,
    }

    audit = evaluate_real_engine_benchmark_source_owner(results)

    assert audit["real_engine_benchmark_source_owner_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_SOURCE_OWNER"
    )
    assert audit["stage_w1_real_engine_benchmark_source_owner_complete"] is False
    assert "below the minimum threshold" in audit[
        "real_engine_benchmark_source_owner_blocking_reasons"
    ][0]


def test_real_engine_benchmark_source_owner_blocks_confidential_data():
    results = {
        "real_engine_benchmark_confidential_data_used": True,
        "real_engine_benchmark_source_confidence": 0.9,
        "real_engine_benchmark_source_count": 3,
    }

    audit = evaluate_real_engine_benchmark_source_owner(results)

    assert audit["real_engine_benchmark_source_owner_status"] == (
        "FAIL_REAL_ENGINE_BENCHMARK_SOURCE_OWNER"
    )
    assert audit["stage_w1_real_engine_benchmark_source_owner_complete"] is False
    assert "Confidential" in audit[
        "real_engine_benchmark_source_owner_blocking_reasons"
    ][0]