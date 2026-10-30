from regen_viewer_manufacturability_overlay_phase_16q5 import (
    build_manufacturability_overlay,
    attach_manufacturability_overlay,
)


def main() -> int:
    good = {
        "coolant_channel_width": 0.0012,
        "coolant_channel_height": 0.0025,
        "effective_rib_width": 0.00075,
        "cooling_coverage": 0.754,
    }

    overlay = build_manufacturability_overlay({}, good)

    assert overlay["passed"] is True
    assert overlay["label"] == "MANUFACTURABILITY: PASS"
    assert overlay["status"] == "PASS_REGEN_VIEWER_MANUFACTURABILITY_OVERLAY_PHASE_16Q5"

    results = {}
    attach_manufacturability_overlay(results, good)

    assert results["phase_16q5_manufacturability_overlay_pass"] is True
    assert results["phase_16q5_manufacturability_overlay_label"] == "MANUFACTURABILITY: PASS"

    bad = {
        "coolant_channel_width": 0.00062,
        "coolant_channel_height": 0.0048,
        "effective_rib_width": 0.00043,
        "cooling_coverage": 0.588,
    }

    bad_overlay = build_manufacturability_overlay({}, bad)

    assert bad_overlay["passed"] is False
    assert bad_overlay["label"] == "MANUFACTURABILITY: FAIL"
    assert len(bad_overlay["details"]) >= 1

    print("PASS_REGEN_VIEWER_MANUFACTURABILITY_OVERLAY_PHASE_16Q5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
