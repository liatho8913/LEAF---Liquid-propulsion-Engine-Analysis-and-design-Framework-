from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "regeneration_callback=None",
        "self.regeneration_callback = regeneration_callback",
        "run_live_solver_regeneration_phase_16p3",
        "PASS_LIVE_SOLVER_REGENERATION_PHASE_16P3",
        "WARN_LIVE_SOLVER_REGENERATION_CALLBACK_MISSING_PHASE_16P3",
        "FAIL_LIVE_SOLVER_REGENERATION_CALLBACK_ERROR_PHASE_16P3",
        "live_regenerated = self.run_live_solver_regeneration_phase_16p3()",
        "phase_16p1_automatic_geometry_workflow_live_solver_regenerated",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_LIVE_SOLVER_REGENERATION_HOOK_PHASE_16P3")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_LIVE_SOLVER_REGENERATION_HOOK_PHASE_16P3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
