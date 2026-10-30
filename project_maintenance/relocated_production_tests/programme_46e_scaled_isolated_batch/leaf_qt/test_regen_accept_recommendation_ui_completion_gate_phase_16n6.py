from pathlib import Path


def main() -> int:
    path = Path("leaf_qt/regen_cross_section_viewer.py")
    text = path.read_text()

    required_fragments = [
        "attach_accept_recommendation_result_phase_16n6",
        "def accept_recommendation_phase_16n6",
        "phase_16n6_accept_recommendation_status",
        "phase_16n6_recommendation_accepted",
        "self.accept_recommendation_phase_16n6()",
        "def accept_automatic_geometry",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    if missing:
        print("FAIL_REGEN_ACCEPT_RECOMMENDATION_UI_COMPLETION_GATE_PHASE_16N6")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_ACCEPT_RECOMMENDATION_UI_COMPLETION_GATE_PHASE_16N6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
