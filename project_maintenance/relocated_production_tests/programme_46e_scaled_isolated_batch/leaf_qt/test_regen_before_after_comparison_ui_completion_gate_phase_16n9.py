from pathlib import Path


def main() -> int:
    path = Path("leaf_qt/regen_cross_section_viewer.py")
    text = path.read_text()

    required_fragments = [
        "attach_before_after_comparison_phase_16n9",
        "def refresh_before_after_comparison_phase_16n9",
        "phase_16n9_before_after_comparison_status",
        "phase_16n9_before_after_comparison_available",
        "self.refresh_before_after_comparison_phase_16n9()",
        "def accept_automatic_geometry",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    if missing:
        print("FAIL_REGEN_BEFORE_AFTER_COMPARISON_UI_COMPLETION_GATE_PHASE_16N9")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_BEFORE_AFTER_COMPARISON_UI_COMPLETION_GATE_PHASE_16N9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
