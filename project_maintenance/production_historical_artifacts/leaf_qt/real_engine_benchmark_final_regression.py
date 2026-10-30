"""
LEAF Real Engine Benchmark Final Regression
===========================================

Stage W.7 final regression and handover signoff.

This module does not create benchmark logic.
It verifies that Stage W architecture is complete enough to hand over.
"""


REQUIRED_STAGE_W_KEYS = [
    "stage_w1_real_engine_benchmarking_framework_complete",
    "stage_w2_public_benchmark_source_ownership_complete",
    "stage_w3_numeric_benchmark_band_ownership_complete",
    "stage_w4_real_engine_benchmark_failure_ownership_complete",
    "stage_w5_real_engine_benchmark_master_gate_complete",
    "stage_w6_real_engine_benchmark_completion_audit_complete",
    "stage_w_real_engine_benchmarking_complete",
]

REQUIRED_STAGE_W_REPORTS = [
    "real_engine_benchmarking_framework_text",
    "real_engine_benchmark_source_owner_text",
    "real_engine_benchmark_band_owner_text",
    "real_engine_benchmark_failure_owner_text",
    "real_engine_benchmark_master_gate_text",
    "real_engine_benchmark_completion_audit_text",
]


def attach_real_engine_benchmark_final_regression(results):
    if not isinstance(results, dict):
        return results

    audit = evaluate_real_engine_benchmark_final_regression(results)
    results.update(audit)
    return results


def evaluate_real_engine_benchmark_final_regression(results):
    results = results if isinstance(results, dict) else {}

    blocking_reasons = []
    evidence = []

    for key in REQUIRED_STAGE_W_KEYS:
        if not bool(results.get(key, False)):
            blocking_reasons.append(f"Required Stage W completion key is false or missing: {key}")
        else:
            evidence.append(f"Completion key present: {key}")

    for key in REQUIRED_STAGE_W_REPORTS:
        if not results.get(key):
            blocking_reasons.append(f"Required Stage W report is missing: {key}")
        else:
            evidence.append(f"Report present: {key}")

    completion_status = results.get("real_engine_benchmark_completion_audit_status")
    if completion_status != "PASS_REAL_ENGINE_BENCHMARK_COMPLETION_AUDIT":
        blocking_reasons.append(
            f"Stage W completion audit is not passing: {completion_status}"
        )

    if blocking_reasons:
        status = "FAIL_REAL_ENGINE_BENCHMARK_FINAL_REGRESSION"
        complete = False
    else:
        status = "PASS_REAL_ENGINE_BENCHMARK_FINAL_REGRESSION"
        complete = True

    text = build_final_regression_text(
        status=status,
        complete=complete,
        blocking_reasons=blocking_reasons,
        evidence=evidence,
        results=results,
    )

    return {
        "real_engine_benchmark_final_regression_status": status,
        "real_engine_benchmark_final_regression_complete": complete,
        "real_engine_benchmark_final_regression_blocking_reasons": blocking_reasons,
        "real_engine_benchmark_final_regression_evidence": evidence,
        "real_engine_benchmark_final_regression_text": text,
        "stage_w7_real_engine_benchmark_final_regression_complete": complete,
    }


def build_final_regression_text(status, complete, blocking_reasons, evidence, results):
    lines = [
        "LEAF STAGE W.7 REAL ENGINE BENCHMARK FINAL REGRESSION",
        "=====================================================",
        "",
        f"Status: {status}",
        f"Stage W final regression complete: {complete}",
        "",
        "Owned By:",
        "- real_engine_benchmark_final_regression.py",
        "",
        "Purpose:",
        "- Confirms Stage W benchmark architecture is ready for handover.",
        "- Confirms W.1-W.6 completion evidence exists.",
        "- Confirms reports exist for review.",
        "- Does not add benchmark physics.",
        "",
        "Stage W Summary:",
        f"- Reference engine: {results.get('real_engine_benchmark_reference_engine', 'N/A')}",
        f"- Completion audit: {results.get('real_engine_benchmark_completion_audit_status', 'UNKNOWN')}",
        f"- Stage W complete: {results.get('stage_w_real_engine_benchmarking_complete', False)}",
        "",
        "Blocking Reasons:",
    ]

    lines.extend([f"- {item}" for item in blocking_reasons] or ["- None."])

    lines.append("")
    lines.append("Evidence:")
    lines.extend([f"- {item}" for item in evidence] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Final regression can pass only after W.1-W.6 are complete.")
    lines.append("- Missing reports block handover.")
    lines.append("- This is architectural signoff, not physical validation.")

    return "\n".join(lines)