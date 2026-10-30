from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/main_window.py").read_text()

    required = [
        "set_regen_geometry_override_phase_16p4",
        "phase_16p4_input_override_geometry",
        "phase_16p4_input_override_applied",
        "self.calculate()",
        "PASS_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_MAIN_WINDOW_REGEN_INPUT_OVERRIDE_PHASE_16P4C")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_MAIN_WINDOW_REGEN_INPUT_OVERRIDE_PHASE_16P4C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
