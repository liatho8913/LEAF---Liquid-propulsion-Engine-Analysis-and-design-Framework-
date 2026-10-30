from report_ownership import build_report_viewer_bundle


def test_stage_w_reports_are_exposed_in_report_bundle():
    results = {
        "real_engine_benchmarking_framework_text": "W1 report",
        "real_engine_benchmark_source_owner_text": "W2 report",
        "real_engine_benchmark_band_owner_text": "W3 report",
        "real_engine_benchmark_failure_owner_text": "W4 report",
        "real_engine_benchmark_master_gate_text": "W5 report",
        "real_engine_benchmark_completion_audit_text": "W6 report",
    }

    reports = build_report_viewer_bundle(results)

    assert reports["Stage W.1 Real Engine Benchmarking Framework"] == "W1 report"
    assert reports["Stage W.2 Public Benchmark Source Ownership"] == "W2 report"
    assert reports["Stage W.3 Numeric Benchmark Band Ownership"] == "W3 report"
    assert reports["Stage W.4 Real Engine Benchmark Failure Ownership"] == "W4 report"
    assert reports["Stage W.5 Real Engine Benchmark Master Gate"] == "W5 report"
    assert reports["Stage W.6 Real Engine Benchmark Completion Audit"] == "W6 report"


def test_stage_w_reports_have_fallback_text():
    reports = build_report_viewer_bundle({})

    assert "Stage W.1 Real Engine Benchmarking Framework" in reports
    assert "Stage W.2 Public Benchmark Source Ownership" in reports
    assert "Stage W.3 Numeric Benchmark Band Ownership" in reports
    assert "Stage W.4 Real Engine Benchmark Failure Ownership" in reports
    assert "Stage W.5 Real Engine Benchmark Master Gate" in reports
    assert "Stage W.6 Real Engine Benchmark Completion Audit" in reports