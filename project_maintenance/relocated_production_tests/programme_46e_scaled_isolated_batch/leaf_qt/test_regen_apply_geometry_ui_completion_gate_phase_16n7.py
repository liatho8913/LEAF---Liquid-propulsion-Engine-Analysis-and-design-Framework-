from pathlib import Path


def main() -> int:
    path = Path("leaf_qt/regen_cross_section_viewer.py")
    text = path.read_text()

    required_fragments = [
        "attach_apply_geometry_result_phase_16n7",
        "def apply_accepted_geometry_phase_16n7",
        "phase_16n7_apply_geometry_status",
        "phase_16n7_geometry_applied",
        "self.apply_accepted_geometry_phase_16n7()",
        "def accept_automatic_geometry",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    if missing:
        print("FAIL_REGEN_APPLY_GEOMETRY_UI_COMPLETION_GATE_PHASE_16N7")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_APPLY_GEOMETRY_UI_COMPLETION_GATE_PHASE_16N7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
