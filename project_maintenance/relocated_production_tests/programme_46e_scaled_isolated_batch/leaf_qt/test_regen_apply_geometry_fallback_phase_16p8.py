from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "fallback_apply_geometry_result_phase_16p8",
        "PASS_APPLY_GEOMETRY_RECORDED_PHASE_16P8",
        "phase_16p8_apply_geometry_fallback_used",
        "regen_ui_applied_geometry",
        "regen_current_geometry",
        "apply_owner = fallback_apply_geometry_result_phase_16p8",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_APPLY_GEOMETRY_FALLBACK_PHASE_16P8")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_APPLY_GEOMETRY_FALLBACK_PHASE_16P8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
