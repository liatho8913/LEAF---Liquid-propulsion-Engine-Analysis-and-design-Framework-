from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "fallback_solver_regeneration_request_phase_16p9",
        "PASS_SOLVER_REGENERATION_REQUEST_RECORDED_PHASE_16P9",
        "phase_16p9_solver_regeneration_fallback_used",
        "request_owner = fallback_solver_regeneration_request_phase_16p9",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_SOLVER_REQUEST_FALLBACK_PHASE_16P9")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_SOLVER_REQUEST_FALLBACK_PHASE_16P9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
