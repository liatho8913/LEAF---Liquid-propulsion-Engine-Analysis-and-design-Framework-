from regen_cross_section_live_feed_validator_phase_16n4 import (
    RegenCrossSectionLiveFeedValidatorPhase16N4,
)


def main() -> int:
    validator = RegenCrossSectionLiveFeedValidatorPhase16N4()

    result = validator.validate(
        {
            "regen_current_geometry": {
                "number_of_coolant_channels": 80,
                "coolant_channel_width": 0.0015,
            },
            "regen_geometry_commit_staged_geometry": {
                "number_of_coolant_channels": 96,
                "coolant_channel_width": 0.0012,
            },
            "regen_automatic_geometry_decision": "ACCEPT_AUTOMATIC_GEOMETRY",
            "phase_16n2_automatic_geometry_button_state": (
                "PASS_AUTOMATIC_GEOMETRY_BUTTON_ENABLED_PHASE_16N2"
            ),
        }
    )

    assert result.status == "PASS_CROSS_SECTION_LIVE_FEED_VALIDATION_PHASE_16N4"
    assert result.manual_geometry_present is True
    assert result.automatic_geometry_present is True
    assert result.recommendation_present is True

    missing = validator.validate({})
    assert missing.status == "FAIL_CROSS_SECTION_LIVE_FEED_VALIDATION_PHASE_16N4"
    assert missing.notes

    print("PASS_REGEN_CROSS_SECTION_LIVE_FEED_VALIDATOR_PHASE_16N4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
