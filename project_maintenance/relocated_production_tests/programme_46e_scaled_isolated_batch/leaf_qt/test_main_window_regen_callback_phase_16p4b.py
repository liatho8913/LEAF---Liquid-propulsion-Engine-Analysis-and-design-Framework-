from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/main_window.py").read_text()

    required = [
        "regenerate_solver_from_regen_viewer_phase_16p4",
        "regen_solver_regeneration_callback=self.regenerate_solver_from_regen_viewer_phase_16p4",
        "phase_16p4_main_window_regeneration_callback_called",
        "PASS_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4",
        "FAIL_MAIN_WINDOW_REGENERATION_CALLBACK_PHASE_16P4",
        "self.calculate()",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_MAIN_WINDOW_REGEN_CALLBACK_PHASE_16P4B")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_MAIN_WINDOW_REGEN_CALLBACK_PHASE_16P4B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
