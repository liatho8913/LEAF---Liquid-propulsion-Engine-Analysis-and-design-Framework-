from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    start = text.find("automatic_data = (")
    block = text[start:start + 700]

    required_order = [
        "regen_ui_applied_geometry",
        "regen_current_geometry",
        "regen_viewer_accepted_geometry",
        "regen_geometry_commit_staged_geometry",
    ]

    missing = [item for item in required_order if item not in block]

    if missing:
        print("FAIL_REGEN_RENDERER_USES_APPLIED_GEOMETRY_PHASE_16P12")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    if block.find("regen_ui_applied_geometry") > block.find("regen_geometry_commit_staged_geometry"):
        print("FAIL_REGEN_RENDERER_USES_APPLIED_GEOMETRY_PHASE_16P12")
        print("- applied geometry is not preferred before staged geometry")
        raise SystemExit(1)

    print("PASS_REGEN_RENDERER_USES_APPLIED_GEOMETRY_PHASE_16P12")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
