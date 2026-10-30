from variable_registry import (
    get_scalar_output_keys,
    get_validation_output_keys,
    get_diagnostic_output_keys,
    get_recommendation_output_keys,
    get_axial_report_keys,
    get_output_visibility,
)

from report_ownership import (
    get_main_output_results,
    get_validation_results,
    get_diagnostic_results,
    get_recommendation_results,
    get_axial_report_results,
    build_report_viewer_bundle,
)

from station_report_builder import (
    get_station_rows,
    build_station_view_rows,
)


def run_foundation_regression_tests(results):
    results = results if isinstance(results, dict) else {}

    tests = []

    def add_test(name, passed, detail=""):
        tests.append({
            "name": name,
            "passed": bool(passed),
            "detail": detail,
        })

    scalar_keys = set(get_scalar_output_keys())
    validation_keys = set(get_validation_output_keys())
    diagnostic_keys = set(get_diagnostic_output_keys())
    recommendation_keys = set(get_recommendation_output_keys())
    axial_keys = set(get_axial_report_keys())

    # ---------------------------------------------------------
    # Visibility overlap tests
    # ---------------------------------------------------------

    add_test(
        "Scalar keys do not overlap validation keys",
        scalar_keys.isdisjoint(validation_keys),
    )

    add_test(
        "Scalar keys do not overlap diagnostic keys",
        scalar_keys.isdisjoint(diagnostic_keys),
    )

    add_test(
        "Scalar keys do not overlap recommendation keys",
        scalar_keys.isdisjoint(recommendation_keys),
    )

    add_test(
        "Scalar keys do not overlap axial/report-only keys",
        scalar_keys.isdisjoint(axial_keys),
    )

    # ---------------------------------------------------------
    # Main output pollution tests
    # ---------------------------------------------------------

    main_results = get_main_output_results(results)

    polluted_keys = [
        key for key in main_results
        if get_output_visibility(key) != "SCALAR_OUTPUT"
    ]

    add_test(
        "Main output results contain only scalar outputs",
        not polluted_keys,
        f"Polluted keys: {polluted_keys}",
    )

    # ---------------------------------------------------------
    # Report category extraction tests
    # ---------------------------------------------------------

    add_test(
        "Validation report extraction runs",
        isinstance(get_validation_results(results), dict),
    )

    add_test(
        "Diagnostics report extraction runs",
        isinstance(get_diagnostic_results(results), dict),
    )

    add_test(
        "Recommendation report extraction runs",
        isinstance(get_recommendation_results(results), dict),
    )

    add_test(
        "Axial report extraction runs",
        isinstance(get_axial_report_results(results), dict),
    )

    # ---------------------------------------------------------
    # Narrative / proof / root-cause / recommendation tests
    # ---------------------------------------------------------

    add_test(
        "Design history narrative key exists after calculation",
        "design_history_narrative_text" in results,
    )

    add_test(
        "Optimisation proof key exists after calculation",
        "regen_optimisation_proof_text" in results,
    )

    add_test(
        "Failure root cause key exists after calculation",
        "failure_root_cause_text" in results,
    )

    add_test(
        "Recommendation explanation key exists after calculation",
        "recommendation_explanation_text" in results,
    )

    add_test(
        "Before/after comparison key exists after calculation",
        "before_after_comparison_text" in results,
    )

    add_test(
        "Report dashboard key exists after calculation",
        "report_dashboard_text" in results,
    )

    # ---------------------------------------------------------
    # Report viewer bundle tests
    # ---------------------------------------------------------

    reports = build_report_viewer_bundle(results)

    required_reports = [
        "Dashboard",
        "Main Output Report",
        "Validation Report",
        "Diagnostics Report",
        "Recommendation Report",
        "Axial Thermal Report",
        "Development Evidence Report",
    ]

    missing_reports = [
        name for name in required_reports
        if name not in reports
    ]

    add_test(
        "Report viewer bundle contains all required reports",
        not missing_reports,
        f"Missing reports: {missing_reports}",
    )

    # ---------------------------------------------------------
    # Station table tests
    # ---------------------------------------------------------

    station_rows = get_station_rows(results)

    add_test(
        "Station rows are list-compatible",
        isinstance(station_rows, list),
    )

    for view_name in ["Thermal", "Validation", "Diagnostics", "Full"]:
        rows, columns = build_station_view_rows(results, view_name)

        add_test(
            f"Station view builds: {view_name}",
            isinstance(rows, list) and isinstance(columns, list),
            f"Rows: {len(rows)}, Columns: {len(columns)}",
        )

    passed_count = sum(1 for test in tests if test["passed"])
    failed_count = len(tests) - passed_count

    status = "PASS" if failed_count == 0 else "FAIL"

    return {
        "foundation_regression_status": status,
        "foundation_regression_passed_count": passed_count,
        "foundation_regression_failed_count": failed_count,
        "foundation_regression_tests": tests,
        "foundation_regression_text": build_regression_report_text(
            status,
            passed_count,
            failed_count,
            tests,
        ),
    }


def build_regression_report_text(status, passed_count, failed_count, tests):
    lines = []
    lines.append("LEAF FOUNDATION REGRESSION TEST REPORT")
    lines.append("======================================")
    lines.append("")
    lines.append(f"Status: {status}")
    lines.append(f"Passed: {passed_count}")
    lines.append(f"Failed: {failed_count}")
    lines.append("")

    for test in tests:
        result = "PASS" if test.get("passed") else "FAIL"
        lines.append(f"[{result}] {test.get('name')}")

        detail = test.get("detail")

        if detail:
            lines.append(f"  {detail}")

        lines.append("")

    return "\n".join(lines)


def attach_foundation_regression_tests(results):
    if results is None:
        return results

    regression = run_foundation_regression_tests(results)

    for key, value in regression.items():
        results[key] = value

    return results