from dataclasses import dataclass


@dataclass
class ResultReplacementVerification:
    status: str
    changed_keys: list
    unchanged_keys: list
    changed_count: int
    verified: bool


TRACKED_KEYS = [
    "coolant_channel_width",
    "coolant_channel_height",
    "number_of_coolant_channels",
    "hot_gas_wall_thickness",
    "outer_wall_thickness",
    "regen_pressure_drop",
    "coolant_velocity",
    "coolant_temperature_rise",
]


def verify_result_replacement(before_results, after_results):

    changed = []
    unchanged = []

    before_results = before_results or {}
    after_results = after_results or {}

    for key in TRACKED_KEYS:

        before_value = before_results.get(key)
        after_value = after_results.get(key)

        if before_value != after_value:
            changed.append(key)
        else:
            unchanged.append(key)

    verified = len(changed) > 0

    return ResultReplacementVerification(
        status=(
            "PASS_REGEN_RESULT_REPLACEMENT_VERIFIED_PHASE_16P5A"
            if verified
            else
            "FAIL_REGEN_RESULT_REPLACEMENT_VERIFIED_PHASE_16P5A"
        ),
        changed_keys=changed,
        unchanged_keys=unchanged,
        changed_count=len(changed),
        verified=verified,
    )
