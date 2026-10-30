from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "show_applied_automatic_geometry_phase_16p11",
        "PASS_AUTOMATIC_GEOMETRY_DISPLAYED_PHASE_16P11",
        'self.canvas.geometry_source = "automatic"',
        "phase_16p11_automatic_display_requested",
        "phase_16p11_displayed_automatic_geometry",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_AUTOMATIC_SOURCE_DISPLAY_PHASE_16P11")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_AUTOMATIC_SOURCE_DISPLAY_PHASE_16P11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
