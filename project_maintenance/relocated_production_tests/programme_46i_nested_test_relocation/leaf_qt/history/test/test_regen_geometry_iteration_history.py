from regen_geometry_iteration_history import (
    RegenGeometryIterationHistory,
    flatten_iteration_history_summary,
)


def run_test():
    history = RegenGeometryIterationHistory(max_records=5)

    passing_candidate = {
        "channel_count": 40,
        "channel_width": 0.001,
        "channel_height": 0.0015,
        "effective_rib_width": 0.0006,
        "fit_ratio": 1.1,
        "coolant_velocity": 25.0,
        "reynolds_number": 12000.0,
        "estimated_pressure_drop": 100000.0,
        "circumferential_coverage": 0.5,
        "score": 8.5,
    }

    failing_candidate = dict(passing_candidate)
    failing_candidate["effective_rib_width"] = 0.0002

    history.record_candidate(
        failing_candidate,
        {
            "constraint_status": "FAIL",
            "geometry_constraints_pass": False,
            "failures": ["EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM"],
            "warnings": [],
        },
    )

    history.record_candidate(
        passing_candidate,
        {
            "constraint_status": "PASS",
            "geometry_constraints_pass": True,
            "failures": [],
            "warnings": ["LOW_RIB_WIDTH_MARGIN"],
        },
    )

    summary = history.build_summary(selected_candidate=passing_candidate)
    flat = flatten_iteration_history_summary(summary)

    assert summary["iteration_history_status"] == "PASS"
    assert summary["total_candidates_seen"] == 2.0
    assert summary["total_passed_constraints"] == 1.0
    assert summary["total_failed_constraints"] == 1.0
    assert "EFFECTIVE_RIB_WIDTH_BELOW_MINIMUM" in flat["recommended_geometry_most_common_failures"]
    assert "LOW_RIB_WIDTH_MARGIN" in flat["recommended_geometry_most_common_warnings"]

    print("PASS_REGEN_GEOMETRY_ITERATION_HISTORY")


if __name__ == "__main__":
    run_test()