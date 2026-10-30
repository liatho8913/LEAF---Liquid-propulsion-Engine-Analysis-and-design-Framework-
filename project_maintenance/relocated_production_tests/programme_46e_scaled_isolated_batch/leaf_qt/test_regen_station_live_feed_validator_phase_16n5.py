from regen_station_live_feed_validator_phase_16n5 import (
    RegenStationLiveFeedValidatorPhase16N5,
)


def main() -> int:
    validator = RegenStationLiveFeedValidatorPhase16N5()

    result = validator.validate(
        {
            "regen_station_rows": [
                {"x": 0.0, "radius": 0.01, "mach": 1.0},
                {"x": 0.1, "radius": 0.02, "mach": 2.0},
            ],
            "regen_geometry_commit_staged_geometry": {
                "number_of_coolant_channels": 80,
                "coolant_channel_width": 0.0015,
            },
            "regen_automatic_geometry_decision": "ACCEPT_AUTOMATIC_GEOMETRY",
        }
    )

    assert result.status == "PASS_STATION_LIVE_FEED_VALIDATION_PHASE_16N5"
    assert result.station_payload_present is True
    assert result.station_count == 2
    assert result.automatic_geometry_present is True
    assert result.recommendation_present is True

    missing = validator.validate({})
    assert missing.status == "FAIL_STATION_LIVE_FEED_VALIDATION_PHASE_16N5"
    assert missing.notes

    print("PASS_REGEN_STATION_LIVE_FEED_VALIDATOR_PHASE_16N5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
