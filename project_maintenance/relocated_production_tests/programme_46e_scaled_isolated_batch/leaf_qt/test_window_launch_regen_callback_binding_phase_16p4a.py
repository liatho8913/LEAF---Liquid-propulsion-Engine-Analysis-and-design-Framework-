from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/window_launch_controller.py").read_text()

    required = [
        "regen_solver_regeneration_callback=None",
        "self.regen_solver_regeneration_callback = regen_solver_regeneration_callback",
        "regeneration_callback=self.regen_solver_regeneration_callback",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_WINDOW_LAUNCH_REGEN_CALLBACK_BINDING_PHASE_16P4A")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_WINDOW_LAUNCH_REGEN_CALLBACK_BINDING_PHASE_16P4A")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
