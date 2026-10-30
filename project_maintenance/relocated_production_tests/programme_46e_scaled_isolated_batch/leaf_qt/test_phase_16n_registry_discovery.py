from pathlib import Path

def main():

    text = Path(
        "leaf_qt/variable_registry.py"
    ).read_text()

    phase16_keys = [
        "phase_16n6_accept_recommendation_status",
        "phase_16n6_recommendation_accepted",
        "phase_16n7_apply_geometry_status",
        "phase_16n7_geometry_applied",
        "phase_16n8_solver_regeneration_request_status",
        "phase_16n8_solver_regeneration_requested",
        "phase_16n9_before_after_comparison_status",
        "phase_16n9_before_after_comparison_available",
        "regen_ui_applied_geometry",
        "regen_current_geometry",
    ]

    missing = [
        key for key in phase16_keys
        if key not in text
    ]

    if missing:
        print("FAIL_PHASE_16N_REGISTRY_DISCOVERY")
        print("Missing:")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_PHASE_16N_REGISTRY_DISCOVERY")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
