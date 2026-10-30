from pathlib import Path


def main() -> int:
    path = Path("leaf_qt/station_table_window.py")
    text = path.read_text()

    required_fragments = [
        "RegenStationLiveFeedValidatorPhase16N5",
        "def refresh_station_live_feed_validation_phase_16n5",
        "self.refresh_station_live_feed_validation_phase_16n5()",
        "phase_16n5_station_live_feed_status",
        "phase_16n5_station_payload_present",
        "phase_16n5_station_count",
        "phase_16n5_station_automatic_geometry_present",
        "phase_16n5_station_recommendation_present",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    if missing:
        print("FAIL_REGEN_STATION_LIVE_FEED_COMPLETION_GATE_PHASE_16N5")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_STATION_LIVE_FEED_COMPLETION_GATE_PHASE_16N5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
