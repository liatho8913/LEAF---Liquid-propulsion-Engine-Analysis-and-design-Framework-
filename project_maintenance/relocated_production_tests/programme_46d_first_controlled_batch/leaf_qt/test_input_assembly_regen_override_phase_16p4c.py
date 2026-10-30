from pathlib import Path


def main() -> int:
    text = Path("leaf_qt/input_assembly_controller.py").read_text()

    required = [
        "set_regen_geometry_override_phase_16p4",
        "clear_regen_geometry_override_phase_16p4",
        "_apply_regen_geometry_override_phase_16p4",
        "phase_16p4_regen_geometry_override_applied",
        "phase_16p4_regen_geometry_override_keys",
        "coolant_channel_width",
        "hot_gas_wall_thickness",
    ]

    missing = [item for item in required if item not in text]

    if missing:
        print("FAIL_INPUT_ASSEMBLY_REGEN_OVERRIDE_PHASE_16P4C")
        for item in missing:
            print("-", item)
        raise SystemExit(1)

    print("PASS_INPUT_ASSEMBLY_REGEN_OVERRIDE_PHASE_16P4C")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
