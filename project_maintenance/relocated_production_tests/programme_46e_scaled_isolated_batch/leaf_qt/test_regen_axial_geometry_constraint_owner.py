from regen_axial_geometry_constraint_owner import (
    validate_regen_axial_geometry_constraints,
    flatten_regen_axial_constraint_owner_result,
)


def _make_candidate(
    channel_count=40,
    channel_width=0.001,
    channel_height=0.002,
    rib_width=0.0005,
    hydraulic_diameter=0.001333,
    coolant_velocity=25.0,
    reynolds_number=10000.0,
    estimated_pressure_drop=100000.0,
    circumferential_coverage=0.65,
):
    return {
        "channel_count": channel_count,
        "channel_width": channel_width,
        "channel_height": channel_height,
        "rib_width": rib_width,
        "hydraulic_diameter": hydraulic_diameter,
        "coolant_velocity": coolant_velocity,
        "reynolds_number": reynolds_number,
        "estimated_pressure_drop": estimated_pressure_drop,
        "circumferential_coverage": circumferential_coverage,
    }


def run_test():
    axial_result = {
        "axial_geometry_solver_status": "PASS_REGEN_AXIAL_GEOMETRY_SOLVER",
        "axial_geometry_solver_pass": True,
        "axial_station_profile": {
            "axial_station_profile_status": "PASS_REGEN_AXIAL_STATION_PROFILE",
            "axial_station_profile_pass": True,
        },
        "station_results": [
            {
                "station_id": "injector_end",
                "station_name": "Injector End",
                "axial_position": 0.00,
                "local_radius": 0.03,
                "best_candidate": _make_candidate(),
            },
            {
                "station_id": "throat",
                "station_name": "Throat",
                "axial_position": 0.15,
                "local_radius": 0.01,
                "best_candidate": _make_candidate(
                    channel_count=24,
                    channel_width=0.0008,
                    channel_height=0.0016,
                    rib_width=0.00045,
                ),
            },
            {
                "station_id": "exit_nozzle",
                "station_name": "Exit Nozzle",
                "axial_position": 0.30,
                "local_radius": 0.04,
                "best_candidate": _make_candidate(
                    channel_count=48,
                    channel_width=0.0011,
                    channel_height=0.0022,
                    rib_width=0.0005,
                ),
            },
        ],
    }

    result = validate_regen_axial_geometry_constraints(axial_result)

    assert result["regen_axial_constraint_owner_status"] == "PASS_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER"
    assert result["regen_axial_constraint_owner_pass"] is True
    assert result["station_constraint_fail_count"] == 0

    flat = flatten_regen_axial_constraint_owner_result(result)

    assert flat["recommended_regen_axial_constraint_owner_status"] == "PASS_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER"
    assert flat["recommended_regen_axial_constraint_owner_pass"] == 1.0
    assert "recommended_regen_axial_constraint_station_1_status" in flat

    failing_axial_result = {
        "axial_geometry_solver_status": "PASS_REGEN_AXIAL_GEOMETRY_SOLVER",
        "axial_geometry_solver_pass": True,
        "axial_station_profile": {
            "axial_station_profile_status": "PASS_REGEN_AXIAL_STATION_PROFILE",
            "axial_station_profile_pass": True,
        },
        "station_results": [
            {
                "station_id": "bad_station",
                "station_name": "Bad Station",
                "axial_position": 0.0,
                "local_radius": 0.005,
                "best_candidate": _make_candidate(
                    channel_count=500,
                    channel_width=0.002,
                    rib_width=0.002,
                ),
            }
        ],
    }

    failing_result = validate_regen_axial_geometry_constraints(failing_axial_result)

    assert failing_result["regen_axial_constraint_owner_status"] == "FAIL_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER"
    assert failing_result["regen_axial_constraint_owner_pass"] is False
    assert failing_result["station_constraint_fail_count"] == 1

    print("PASS_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER")


if __name__ == "__main__":
    run_test()