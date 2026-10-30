from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/regen_cross_section_viewer.py").read_text()

    required = [
        "refresh_from_regenerated_results_phase_16p5b",
        "verify_result_replacement",
        "PASS_VIEWER_AUTO_REFRESH_PHASE_16P5B",
        "phase_16p5b_result_replacement_verified",
        "phase_16p5b_viewer_auto_refreshed",
        "before_refresh_phase_16p5b",
        "self.refresh_from_regenerated_results_phase_16p5b",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_REGEN_VIEWER_AUTO_REFRESH_PHASE_16P5B")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_REGEN_VIEWER_AUTO_REFRESH_PHASE_16P5B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
