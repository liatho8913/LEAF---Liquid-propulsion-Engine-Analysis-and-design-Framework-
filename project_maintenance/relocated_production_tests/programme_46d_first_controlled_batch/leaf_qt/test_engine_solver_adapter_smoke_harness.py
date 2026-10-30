from project_maintenance.production_historical_artifacts.leaf_qt.engine_solver_adapter_smoke_harness import (
    _summarise_result,
    run_engine_solver_adapter_smoke_harness,
    build_text_report,
)


def test_result_summary_counts_keys_and_numeric_outputs():
    summary = _summarise_result(
        {
            "thrust_n": 1000.0,
            "status": "PASS",
            "isp_s": 300,
            "flag": True,
        }
    )

    assert summary["key_count"] == 4
    assert summary["numeric_output_count"] == 2
    assert "thrust_n" in summary["numeric_outputs_preview"]
    assert "isp_s" in summary["numeric_outputs_preview"]


def test_smoke_harness_import_only_mode():
    result = run_engine_solver_adapter_smoke_harness(execute_solver=False)

    assert result["schema"] == "LEAF_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS_V1"
    assert result["summary"]["executed_solver"] is False
    assert result["adapter_metadata"]["mode"] == "READ_ONLY_ADAPTER"


def test_smoke_harness_report_contains_status():
    result = {
        "schema": "LEAF_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS_V1",
        "summary": {
            "passed": True,
            "executed_solver": False,
            "finding_count": 1,
            "failure_count": 0,
        },
        "findings": [
            {
                "status": "PASS",
                "code": "DRY_SMOKE_IMPORT_ONLY",
                "message": "ok",
            }
        ],
        "result_summary": None,
    }

    report = build_text_report(result)

    assert "LEAF ENGINE SOLVER ADAPTER SMOKE HARNESS" in report
    assert "passed=True" in report


if __name__ == "__main__":
    test_result_summary_counts_keys_and_numeric_outputs()
    test_smoke_harness_import_only_mode()
    test_smoke_harness_report_contains_status()
    print("PASS_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS_TEST")
