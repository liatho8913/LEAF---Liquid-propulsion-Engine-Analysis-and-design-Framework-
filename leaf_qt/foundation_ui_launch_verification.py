from leaf_qt.status_presentation import status_severity
from leaf_qt.variable_registry import is_scalar_output
def verify_foundation_ui_launch(results, report_bundle_callback=None):
    tests = []

    def add(name, passed, detail=""):
        tests.append({
            "name": name,
            "passed": bool(passed),
            "detail": detail,
        })

    if not isinstance(results, dict):
        return _build_result("FAIL_FOUNDATION_UI_LAUNCH_VERIFICATION", tests, [
            "Results object is not a dictionary."
        ])

    required_report_names = [
        "Dashboard",
        "Validation Report",
        "Diagnostics Report",
        "Foundation Attachment Audit",
        "Foundation Result Key Audit",
        "Foundation Verification Harness",
        "Foundation Save/Load Verification",
        "Stage U Regen Completion Audit",
        "Stage V.5 Regen Scalability Completion Audit",
        "Stage W.6 Real Engine Benchmark Completion Audit",
    ]

    if report_bundle_callback is None:
        add("Report bundle callback exists", False, "No report bundle callback supplied.")
    else:
        try:
            reports = report_bundle_callback(results)
            add("Report viewer bundle can be built", isinstance(reports, dict), type(reports).__name__)

            missing = [name for name in required_report_names if name not in reports]
            add("Required foundation reports are exposed", not missing, f"missing={missing}")

            empty = [name for name in required_report_names if not str(reports.get(name, "")).strip()]
            add("Required foundation reports are non-empty", not empty, f"empty={empty}")

        except Exception as exc:
            add("Report viewer bundle can be built", False, f"{type(exc).__name__}: {exc}")

    required_ui_state_keys = [
        "foundation_attachment_pipeline_status",
        "foundation_result_key_audit_status",
        "regen_completion_audit_status",
        "regen_scalability_completion_audit_status",
        "real_engine_benchmark_completion_audit_status",
    ]

    missing_state = [key for key in required_ui_state_keys if key not in results]
    add("Required UI state keys exist", not missing_state, f"missing={missing_state}")

    long_scalar_pollution = []
    allowed_long_text_suffixes = (
        "_text",
        "_report",
        "_audit_text",
        "_reason",
        "_message",
        "_summary",
        "_note",
    )

    for key, value in results.items():
        if not is_scalar_output(key):
            continue

        if isinstance(value, str) and len(value) > 120:
            if not (
                    key.endswith(allowed_long_text_suffixes)
                    or "text" in key
            ):
                long_scalar_pollution.append(key)

    add("No obvious long report text is exposed as scalar state", not long_scalar_pollution, f"keys={long_scalar_pollution}")

    failed = [test for test in tests if not test["passed"]]

    if failed:
        status = "FAIL_FOUNDATION_UI_LAUNCH_VERIFICATION"
    else:
        status = "PASS_FOUNDATION_UI_LAUNCH_VERIFICATION"

    return _build_result(status, tests, [])


def _build_result(status, tests, blocking):
    passed_count = sum(1 for test in tests if test["passed"])
    failed_count = len(tests) - passed_count

    return {
        "foundation_ui_launch_verification_status": status,
        "foundation_ui_launch_verified": failed_count == 0 and status_severity(status) == "PASS",
        "foundation_ui_launch_passed_count": passed_count,
        "foundation_ui_launch_failed_count": failed_count,
        "foundation_ui_launch_tests": tests,
        "foundation_ui_launch_blocking_reasons": blocking,
        "foundation_ui_launch_verification_text": build_foundation_ui_launch_report(
            status,
            tests,
            blocking,
        ),
    }


def build_foundation_ui_launch_report(status, tests, blocking):
    lines = [
        "LEAF FOUNDATION UI LAUNCH / REPORT VIEWER VERIFICATION",
        "======================================================",
        "",
        f"Status: {status}",
        "",
        "Tests:",
    ]

    for test in tests:
        marker = "PASS" if test["passed"] else "FAIL"
        lines.append(f"- [{marker}] {test['name']}")
        if test.get("detail"):
            lines.append(f"  {test['detail']}")

    lines.append("")
    lines.append("Blocking Reasons:")
    lines.extend([f"- {item}" for item in blocking] or ["- None."])

    lines.append("")
    lines.append("Rule:")
    lines.append("- Report viewer data must build without crashing.")
    lines.append("- Required foundation reports must be exposed.")
    lines.append("- UI-facing state must not lose validation, audit, scalability, or benchmark evidence.")
    lines.append("- This verifies report/dashboard readiness, not live Tkinter rendering.")

    return "\n".join(lines)