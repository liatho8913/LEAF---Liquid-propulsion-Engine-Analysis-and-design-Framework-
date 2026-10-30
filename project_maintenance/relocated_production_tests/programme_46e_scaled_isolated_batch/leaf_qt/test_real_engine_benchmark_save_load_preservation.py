from foundation_save_load_verification import (
    verify_foundation_save_load_roundtrip,
)


def test_stage_w_save_load_preserves_benchmark_evidence():
    results = {
        "stage_u_regen_validation_complete": True,
        "stage_v_scalability_complete": True,
        "stage_w_real_engine_benchmarking_complete": True,
        "stage_w_real_engine_benchmark_complete": True,
        "stage_w_complete": True,

        "regen_completion_audit_status": "PASS_REGEN_COMPLETION_AUDIT",
        "regen_scalability_completion_audit_status": "PASS_REGEN_SCALABILITY_COMPLETION_AUDIT",
        "real_engine_benchmark_completion_audit_status": "PASS_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT",

        "foundation_attachment_pipeline_status": "PASS",
        "foundation_result_key_audit_status": "PASS",

        "regen_completion_audit_text": "Stage U report",
        "regen_scalability_completion_audit_text": "Stage V report",
        "real_engine_benchmark_completion_audit_text": "Stage W report",

        "regen_scalability_completion_audit_blocking_reasons": [],
        "real_engine_benchmark_completion_audit_blocking_reasons": [],

        "regen_scalability_completion_audit_warning_reasons": [],
        "real_engine_benchmark_completion_audit_warning_reasons": [],

        "stage_w1_real_engine_benchmarking_framework_complete": True,
        "stage_w2_public_benchmark_source_ownership_complete": True,
        "stage_w3_numeric_benchmark_band_ownership_complete": True,
        "stage_w4_real_engine_benchmark_failure_ownership_complete": True,
        "stage_w5_real_engine_benchmark_master_gate_complete": True,
        "stage_w6_real_engine_benchmark_completion_audit_complete": True,

        "real_engine_benchmarking_framework_status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
        "real_engine_benchmark_source_owner_status": "PASS_REAL_ENGINE_BENCHMARK_SOURCE_OWNER",
        "real_engine_benchmark_band_owner_status": "PASS_REAL_ENGINE_BENCHMARK_BAND_OWNER",
        "real_engine_benchmark_failure_owner_status": "PASS_REAL_ENGINE_BENCHMARK_FAILURE_OWNERSHIP",
        "real_engine_benchmark_master_gate_status": "PASS_REAL_ENGINE_BENCHMARK_MASTER_GATE",

        "real_engine_benchmarking_framework_text": "Framework text",
        "real_engine_benchmark_source_owner_text": "Source text",
        "real_engine_benchmark_band_owner_text": "Band text",
        "real_engine_benchmark_failure_owner_text": "Failure text",
        "real_engine_benchmark_master_gate_text": "Master gate text",

        "real_engine_benchmarking_framework_blocking_reasons": [],
        "real_engine_benchmark_source_owner_blocking_reasons": [],
        "real_engine_benchmark_band_owner_blocking_reasons": [],
        "real_engine_benchmark_master_gate_blocking_reasons": [],

        "real_engine_benchmarking_framework_warning_reasons": [],
        "real_engine_benchmark_source_owner_warning_reasons": [],
        "real_engine_benchmark_band_owner_warning_reasons": [],
        "real_engine_benchmark_master_gate_warning_reasons": [],

        "real_engine_benchmark_reference_engine": "Merlin_1D",
        "real_engine_benchmark_reference_data": {
            "scale_class": "LARGE_ENGINE",
            "cycle": "GAS_GENERATOR",
        },
        "real_engine_benchmark_comparison": {
            "comparison_quality": "PRELIMINARY_PUBLIC_REFERENCE",
        },
        "real_engine_benchmark_source_owner_snapshot": {
            "source_count": 2,
            "public_data_used": True,
        },
        "real_engine_benchmark_band_owner_rows": [
            {
                "metric": "thrust",
                "predicted": 845000,
                "reference": 850000,
                "status": "IN_BAND",
            }
        ],
        "real_engine_benchmark_master_gate_owner_summary": [
            {
                "label": "W.1 benchmarking framework",
                "complete": True,
                "status": "PASS_REAL_ENGINE_BENCHMARKING_FRAMEWORK",
            }
        ],
        "real_engine_benchmark_completion_audit_checks": [
            {
                "name": "Stage V scalability dependency",
                "passed": True,
                "reason": "",
            }
        ],
    }

    audit = verify_foundation_save_load_roundtrip(results)

    assert audit["foundation_save_load_verification_status"] == (
        "PASS_FOUNDATION_SAVE_LOAD_VERIFICATION"
    )
    assert audit["foundation_save_load_verified"] is True
    assert audit["foundation_save_load_missing_keys"] == []
    assert audit["foundation_save_load_changed_values"] == []