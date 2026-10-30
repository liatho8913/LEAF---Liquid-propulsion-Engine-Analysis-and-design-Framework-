from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "run_automatic_geometry_workflow_phase_16p1",
        "Generate Automatic Geometry",
        "self.accept_automatic_button.setVisible(False)",
        "self.reject_automatic_button.setVisible(False)",
        "PASS_AUTOMATIC_GEOMETRY_WORKFLOW_PHASE_16P1",
        "BLOCKED_NO_AUTOMATIC_GEOMETRY_AVAILABLE_PHASE_16P1",
        "button.setEnabled(True)",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_PRODUCTION_UI_CLEANUP_PHASE_16P1")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_PRODUCTION_UI_CLEANUP_PHASE_16P1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
