from pathlib import Path


def main() -> int:
    path = Path("leaf_qt/regen_cross_section_viewer.py")
    text = path.read_text()

    required_fragments = [
        "RegenCrossSectionLiveFeedValidatorPhase16N4",
        "def refresh_cross_section_live_feed_validation_phase_16n4",
        "self.refresh_cross_section_live_feed_validation_phase_16n4()",
        "phase_16n4_cross_section_live_feed_status",
        "phase_16n4_cross_section_manual_geometry_present",
        "phase_16n4_cross_section_automatic_geometry_present",
        "phase_16n4_cross_section_recommendation_present",
        "phase_16n4_cross_section_button_state_present",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    if missing:
        print("FAIL_REGEN_CROSS_SECTION_LIVE_FEED_COMPLETION_GATE_PHASE_16N4")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_CROSS_SECTION_LIVE_FEED_COMPLETION_GATE_PHASE_16N4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
