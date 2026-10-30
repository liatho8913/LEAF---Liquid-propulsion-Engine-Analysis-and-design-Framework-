from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "force_enable_automatic_geometry_button_phase_16p7c",
        "button.setEnabled(True)",
        "button.setDisabled(False)",
        "PASS_FORCE_ENABLED_AUTOMATIC_GEOMETRY_PHASE_16P7C",
        "self.force_enable_automatic_geometry_button_phase_16p7c()",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_FORCE_ENABLE_AUTOMATIC_BUTTON_PHASE_16P7C")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_FORCE_ENABLE_AUTOMATIC_BUTTON_PHASE_16P7C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
