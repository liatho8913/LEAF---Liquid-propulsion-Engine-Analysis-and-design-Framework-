from regen_calculator_data_authority_audit_phase_16t1 import (
    PASS_STATUS,
    WARN_STATUS,
    FAIL_STATUS,
    SOURCE_FALLBACK,
    SOURCE_PLACEHOLDER,
    SOURCE_SOLVER,
    build_regen_calculator_data_authority_audit,
    build_regen_calculator_data_authority_report,
    attach_regen_calculator_data_authority_audit,
)


def authoritative_results():
    return {
        "regen_station_rows": [
            {
                "station_x": 0.0,
                "source": "regen_solver",
                "mach": 0.25,
                "static_pressure": 6.8e6,
                "static_temperature": 3350.0,
                "adiabatic_wall_temperature": 3520.0,
                "heat_flux": 5.1e6,
                "hot_gas_side_wall_temperature": 920.0,
                "coolant_side_wall_temperature": 640.0,
                "coolant_inlet_temperature": 100.0,
                "coolant_outlet_temperature": 180.0,
                "coolant_velocity": 18.0,
                "coolant_reynolds_number": 17500.0,
                "coolant_pressure_drop": 2.4e5,
                "gas_radius": 0.010,
                "coolant_channel_width": 0.0012,
                "coolant_channel_height": 0.0025,
                "rib_width": 0.0005,
                "number_of_coolant_channels": 40,
                "cooling_coverage": 0.876,
                "channel_fit_ratio": 1.14,
            }
        ],
        "manufacturability_status": "PASS_MANUFACTURABILITY",
        "manufacturability_status_source": "solver",
        "engineering_realism_score": 87.7,
        "engineering_realism_score_source": "solver",
    }


def main() -> int:
    good = authoritative_results()
    audit = build_regen_calculator_data_authority_audit(good)

    assert audit["status"] == PASS_STATUS
    assert audit["passed"] is True
    assert audit["blockers"] == []
    assert audit["classified_counts"][SOURCE_SOLVER] > 0
    assert audit["authoritative_required_count"] == audit["required_output_count"]

    report = build_regen_calculator_data_authority_report(good)
    assert "REGEN CALCULATOR DATA AUTHORITY AUDIT" in report
    assert "mach [-]" in report
    assert PASS_STATUS in report

    attach_regen_calculator_data_authority_audit(good)
    assert good["phase_16t1_regen_calculator_data_authority_pass"] is True
    assert good["phase_16t1_regen_calculator_data_authority_status"] == PASS_STATUS

    fallback = authoritative_results()
    fallback["regen_station_rows"][0]["heat_flux_source"] = "fallback"
    fallback_audit = build_regen_calculator_data_authority_audit(fallback)

    assert fallback_audit["status"] == WARN_STATUS
    assert fallback_audit["passed"] is True
    assert fallback_audit["classified_counts"][SOURCE_FALLBACK] == 1
    assert any("heat_flux" in warning for warning in fallback_audit["warnings"])

    placeholder = authoritative_results()
    placeholder["regen_station_rows"][0]["coolant_velocity"] = "PLACEHOLDER"
    placeholder_audit = build_regen_calculator_data_authority_audit(placeholder)

    assert placeholder_audit["status"] == FAIL_STATUS
    assert placeholder_audit["passed"] is False
    assert placeholder_audit["classified_counts"][SOURCE_PLACEHOLDER] == 1
    assert any("coolant_velocity" in blocker for blocker in placeholder_audit["blockers"])

    missing = authoritative_results()
    del missing["regen_station_rows"][0]["static_pressure"]
    missing_audit = build_regen_calculator_data_authority_audit(missing)

    assert missing_audit["status"] == FAIL_STATUS
    assert missing_audit["passed"] is False
    assert any("static_pressure" in blocker for blocker in missing_audit["blockers"])

    print(PASS_STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
