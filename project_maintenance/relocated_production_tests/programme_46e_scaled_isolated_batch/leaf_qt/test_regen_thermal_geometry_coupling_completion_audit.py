from project_maintenance.production_historical_artifacts.leaf_qt.regen_thermal_geometry_coupling_completion_audit import (
    run_regen_thermal_geometry_coupling_completion_audit,
)


def run_test():
    result = (
        run_regen_thermal_geometry_coupling_completion_audit()
    )

    assert (
        result[
            "regen_thermal_geometry_coupling_completion_audit_status"
        ]
        ==
        "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_COMPLETION_AUDIT"
    )

    assert result[
        "regen_thermal_geometry_coupling_completion_audit_pass"
    ]

    assert result[
        "phase_5_thermal_geometry_coupling_complete"
    ]

    print(
        "PASS_REGEN_THERMAL_GEOMETRY_COUPLING_COMPLETION_AUDIT"
    )


if __name__ == "__main__":
    run_test()