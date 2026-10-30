from regen_result_replacement_verification_phase_16p5a import (
    verify_result_replacement,
)


def main():

    before = {
        "coolant_channel_width": 0.0015,
        "number_of_coolant_channels": 80,
    }

    after = {
        "coolant_channel_width": 0.0020,
        "number_of_coolant_channels": 80,
    }

    result = verify_result_replacement(before, after)

    assert result.verified is True
    assert result.changed_count == 1
    assert "coolant_channel_width" in result.changed_keys

    print(
        "PASS_REGEN_RESULT_REPLACEMENT_VERIFICATION_PHASE_16P5A"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
