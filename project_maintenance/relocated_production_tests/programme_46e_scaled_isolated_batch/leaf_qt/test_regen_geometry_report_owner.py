from regen_geometry_solver import solve_regen_geometry
from regen_geometry_report_owner import build_regen_geometry_report


def run_test():
    solver_result = solve_regen_geometry(
        channel_mid_radius=0.012,
        coolant_mass_flow_rate=0.25,
        coolant_density=420.0,
        coolant_dynamic_viscosity=0.00018,
        target_reynolds_number=10000.0,
        minimum_rib_width=0.0005,
        minimum_channel_width=0.0005,
        maximum_channel_height=0.003,
        channel_aspect_ratio=3.0,
        minimum_channel_count=8,
        maximum_channel_count=220,
        maximum_coolant_velocity=80.0,
        minimum_hydraulic_diameter=0.00035,
        pressure_drop_limit=2.0e6,
        nozzle_length=0.15,
        minimum_cooling_coverage=0.25,
    )

    report = build_regen_geometry_report(solver_result)

    assert report["regen_geometry_report_status"] == "PASS_REGEN_GEOMETRY_REPORT_OWNER"
    assert "REGEN GEOMETRY SOLVER REPORT" in report["regen_geometry_report_text"]
    assert "CANDIDATE SEARCH SUMMARY" in report["regen_geometry_report_text"]
    assert "SELECTED GEOMETRY" in report["regen_geometry_report_text"]
    assert "CONSTRAINT OWNER SUMMARY" in report["regen_geometry_report_text"]
    assert "ITERATION HISTORY SUMMARY" in report["regen_geometry_report_text"]
    assert "FINAL DECISION" in report["regen_geometry_report_text"]

    mapped = solver_result["mapped_results"]
    assert "recommended_regen_geometry_report_status" in mapped
    assert "recommended_regen_geometry_report_text" in mapped

    print("PASS_REGEN_GEOMETRY_REPORT_OWNER")


if __name__ == "__main__":
    run_test()