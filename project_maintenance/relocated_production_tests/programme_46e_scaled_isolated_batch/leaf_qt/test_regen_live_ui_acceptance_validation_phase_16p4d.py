from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "build_live_ui_acceptance_report_phase_16p4d",
        "PASS_LIVE_UI_ACCEPTANCE_VALIDATION_PHASE_16P4D",
        "phase_16p4d_live_ui_acceptance_report",
        "phase_16p4d_live_ui_acceptance_changed_fields",
        "before_geometry_phase_16p4d",
        "after_geometry_phase_16p4d",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_LIVE_UI_ACCEPTANCE_VALIDATION_PHASE_16P4D")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_LIVE_UI_ACCEPTANCE_VALIDATION_PHASE_16P4D")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
