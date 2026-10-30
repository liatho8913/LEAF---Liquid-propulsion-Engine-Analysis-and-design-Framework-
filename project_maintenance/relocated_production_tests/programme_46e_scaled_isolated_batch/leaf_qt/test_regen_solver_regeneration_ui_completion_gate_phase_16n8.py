from pathlib import Path


def main() -> int:
    path = Path("leaf_qt/regen_cross_section_viewer.py")
    text = path.read_text()

    required_fragments = [
        "attach_solver_regeneration_request_phase_16n8",
        "def request_solver_regeneration_phase_16n8",
        "phase_16n8_solver_regeneration_request_status",
        "phase_16n8_solver_regeneration_requested",
        "self.request_solver_regeneration_phase_16n8()",
        "def accept_automatic_geometry",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in text]

    if missing:
        print("FAIL_REGEN_SOLVER_REGENERATION_UI_COMPLETION_GATE_PHASE_16N8")
        print("Missing fragments:")
        for fragment in missing:
            print("-", fragment)
        raise SystemExit(1)

    print("PASS_REGEN_SOLVER_REGENERATION_UI_COMPLETION_GATE_PHASE_16N8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
