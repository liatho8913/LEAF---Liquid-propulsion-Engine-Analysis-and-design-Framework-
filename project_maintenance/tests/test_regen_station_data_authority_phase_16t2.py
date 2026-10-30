from regen_station_data_authority_phase_16t2 import (
    PASS_STATUS,
    WARN_STATUS,
    FAIL_STATUS,
    AUTH_SOLVER,
    AUTH_FALLBACK,
    AUTH_PLACEHOLDER,
    build_regen_station_data_authority_audit,
    build_regen_station_data_authority_report,
    attach_regen_station_data_authority_audit,
)


def authoritative_station_row():
    return {
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
    }


def main() -> int:
    good = {
        "regen_station_rows": [
            authoritative_station_row(),
            authoritative_station_row(),
        ]
    }

    good_audit = build_regen_station_data_authority_audit(good)

    assert good_audit["status"] == PASS_STATUS
    assert good_audit["passed"] is True
    assert good_audit["station_row_count"] == 2
    assert good_audit["classified_counts"][AUTH_SOLVER] == 2
    assert good_audit["blockers"] == []

    report = build_regen_station_data_authority_report(good)
    assert "REGEN STATION DATA AUTHORITY AUDIT" in report
    assert PASS_STATUS in report
    assert "row 0" in report

    attach_regen_station_data_authority_audit(good)
    assert good["phase_16t2_regen_station_data_authority_pass"] is True
    assert good["phase_16t2_regen_station_data_authority_status"] == PASS_STATUS

    fallback = {
        "regen_station_rows": [
            {
                **authoritative_station_row(),
                "source": "viewer_derived_fallback",
            }
        ]
    }

    fallback_audit = build_regen_station_data_authority_audit(fallback)

    assert fallback_audit["status"] == FAIL_STATUS
    assert fallback_audit["passed"] is False
    assert fallback_audit["classified_counts"][AUTH_FALLBACK] == 1
    assert any("No solver-authoritative" in blocker for blocker in fallback_audit["blockers"])

    mixed = {
        "regen_station_rows": [
            {
                **authoritative_station_row(),
                "source": "regen_solver",
                "coolant_velocity": None,
            }
        ]
    }

    mixed_audit = build_regen_station_data_authority_audit(mixed)

    assert mixed_audit["status"] == WARN_STATUS
    assert mixed_audit["passed"] is True
    assert any("coolant_velocity" in warning for warning in mixed_audit["warnings"])

    placeholder = {
        "regen_station_rows": [
            {
                **authoritative_station_row(),
                "source": "placeholder_station_data",
            }
        ]
    }

    placeholder_audit = build_regen_station_data_authority_audit(placeholder)

    assert placeholder_audit["status"] == FAIL_STATUS
    assert placeholder_audit["passed"] is False
    assert placeholder_audit["classified_counts"][AUTH_PLACEHOLDER] == 1

    missing = {}
    missing_audit = build_regen_station_data_authority_audit(missing)

    assert missing_audit["status"] == FAIL_STATUS
    assert missing_audit["passed"] is False
    assert "No regen station rows were found." in missing_audit["blockers"]

    print(PASS_STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
