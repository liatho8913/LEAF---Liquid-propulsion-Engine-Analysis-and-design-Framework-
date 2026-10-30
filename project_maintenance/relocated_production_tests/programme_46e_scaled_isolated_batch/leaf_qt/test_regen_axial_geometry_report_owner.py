from regen_axial_geometry_report_owner import (
    generate_regen_axial_geometry_report,
    flatten_regen_axial_report_owner_result,
)


def run_test():
    axial_geometry_result = {
        "axial_geometry_solver_status": "PASS_REGEN_AXIAL_GEOMETRY_SOLVER",
        "axial_geometry_solver_pass": True,
        "station_count": 2,
        "station_pass_count": 2,
        "station_fail_count": 0,
        "station_results": [
            {
                "station_id": "chamber",
                "station_name": "Combustion Chamber",
                "axial_position": 0.05,
                "local_radius": 0.03,
                "station_solver_status": "PASS_REGEN_GEOMETRY_SOLVER",
                "station_solver_pass": True,
                "best_candidate": {
                    "channel_count": 40,
                    "channel_width": 0.001,
                    "channel_height": 0.002,
                    "rib_width": 0.0005,
                    "hydraulic_diameter": 0.001333,
                    "coolant_velocity": 25.0,
                    "reynolds_number": 10000.0,
                },
            },
            {
                "station_id": "throat",
                "station_name": "Throat",
                "axial_position": 0.15,
                "local_radius": 0.01,
                "station_solver_status": "PASS_REGEN_GEOMETRY_SOLVER",
                "station_solver_pass": True,
                "best_candidate": {
                    "channel_count": 24,
                    "channel_width": 0.0008,
                    "channel_height": 0.0016,
                    "rib_width": 0.00045,
                    "hydraulic_diameter": 0.00105,
                    "coolant_velocity": 35.0,
                    "reynolds_number": 12000.0,
                },
            },
        ],
    }

    axial_constraint_result = {
        "regen_axial_constraint_owner_status": "PASS_REGEN_AXIAL_GEOMETRY_CONSTRAINT_OWNER",
        "regen_axial_constraint_owner_pass": True,
        "station_constraint_fail_count": 0,
        "errors": [],
        "warnings": [],
        "station_constraint_results": [
            {
                "station_id": "chamber",
                "station_name": "Combustion Chamber",
                "station_constraint_status": "PASS_REGEN_AXIAL_STATION_CONSTRAINTS",
                "station_constraint_pass": True,
                "errors": [],
                "warnings": [],
            },
            {
                "station_id": "throat",
                "station_name": "Throat",
                "station_constraint_status": "PASS_REGEN_AXIAL_STATION_CONSTRAINTS",
                "station_constraint_pass": True,
                "errors": [],
                "warnings": ["Coolant Reynolds number close to lower acceptable bound."],
            },
        ],
    }

    report = generate_regen_axial_geometry_report(
        axial_geometry_result=axial_geometry_result,
        axial_constraint_result=axial_constraint_result,
    )

    assert report["regen_axial_report_owner_status"] == "PASS_REGEN_AXIAL_GEOMETRY_REPORT_OWNER"
    assert report["regen_axial_report_owner_pass"] is True
    assert report["station_report_count"] == 2
    assert "LEAF REGEN AXIAL GEOMETRY REPORT" in report["report_text"]
    assert "Combustion Chamber" in report["report_text"]
    assert "Throat" in report["report_text"]

    flat = flatten_regen_axial_report_owner_result(report)

    assert flat["recommended_regen_axial_report_owner_status"] == "PASS_REGEN_AXIAL_GEOMETRY_REPORT_OWNER"
    assert flat["recommended_regen_axial_report_owner_pass"] == 1.0
    assert "recommended_regen_axial_report_text" in flat

    print("PASS_REGEN_AXIAL_GEOMETRY_REPORT_OWNER")


if __name__ == "__main__":
    run_test()