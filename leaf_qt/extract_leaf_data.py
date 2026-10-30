from pathlib import Path

from core.architecture.io import write_text_artifact


ROOT = Path(__file__).resolve().parent.parent
OLD_GUI = ROOT / "promethean_forge.py"
OUT_FILE = Path(__file__).resolve().parent / "leaf_data.py"


ASSIGNMENTS = {
    "self.label_to_var": "LABEL_TO_VAR",
    "self.symbols": "SYMBOLS",
    "self.units": "UNITS",
    "self.unit_groups": "UNIT_GROUPS",
    "self.unit_preferences": "UNIT_PREFERENCES",
    "self.sections": "SECTIONS",
}


def extract_balanced_dict(source_text, assignment_text):
    start = source_text.find(assignment_text)

    if start == -1:
        raise ValueError(f"Could not find {assignment_text}")

    equals_index = source_text.find("=", start)
    brace_start = source_text.find("{", equals_index)

    if brace_start == -1:
        raise ValueError(f"Could not find opening brace for {assignment_text}")

    depth = 0
    in_string = False
    string_char = ""
    escape = False

    for index in range(brace_start, len(source_text)):
        char = source_text[index]

        if escape:
            escape = False
            continue

        if char == "\\":
            escape = True
            continue

        if in_string:
            if char == string_char:
                in_string = False
            continue

        if char in ("'", '"'):
            in_string = True
            string_char = char
            continue

        if char == "{":
            depth += 1

        elif char == "}":
            depth -= 1

            if depth == 0:
                return source_text[brace_start:index + 1]

    raise ValueError(f"Could not find closing brace for {assignment_text}")


def extract_hidden_inputs(source_text):
    marker = "hidden_input_vars ="

    try:
        hidden_dict = extract_balanced_dict(source_text, marker)
        return hidden_dict
    except Exception:
        return """{
    "specific_heat_cp",
    "cea_molecular_weight",
    "cea_density",
    "cea_cp_frozen",
    "cea_cv_equilibrium",
    "cea_cv_frozen",
    "cea_selected_cp",
    "cea_selected_prandtl",
    "cea_selected_gamma",
    "cea_selected_molecular_weight",
    "cea_selected_viscosity",
    "cea_selected_conductivity",
    "cea_chamber_temperature",
    "specific_heat_cv",
    "thermo_r_error",
    "thermo_r_error_percent",
    "combustion_efficiency",
    "mixture_quality_factor",
    "soot_risk_factor",
    "thermal_risk_factor",
    "ideal_engine_thrust",
    "ideal_engine_specific_impulse",
    "ideal_volumetric_thrust",
    "corrected_thrust",
    "corrected_specific_impulse",
    "fuel_density",
    "oxidizer_density",
    "total_propellant_volume_flow_rate",
    "volumetric_corrected_thrust",
    "material_density",
    "material_max_wall_temperature",
    "single_channel_flow_area",
    "total_coolant_flow_area",
    "coolant_wetted_perimeter",
    "coolant_hydraulic_diameter",
    "channel_pitch",
    "regen_cross_section_outer_radius",
}"""


def main():
    source_text = OLD_GUI.read_text(encoding="utf-8")

    output = []
    output.append('"""')
    output.append("Auto-generated LEAF data definitions.")
    output.append("")
    output.append("Generated from promethean_forge.py.")
    output.append("Do not manually shrink these dictionaries.")
    output.append('"""')
    output.append("")

    for old_name, new_name in ASSIGNMENTS.items():
        dictionary_text = extract_balanced_dict(source_text, old_name)

        output.append(f"{new_name} = {dictionary_text}")
        output.append("")
        output.append("")

    hidden_inputs = extract_hidden_inputs(source_text)

    output.append(f"HIDDEN_INPUT_VARS = {hidden_inputs}")
    output.append("")

    write_text_artifact("\n".join(output), OUT_FILE)

    print(f"Generated: {OUT_FILE}")
    print("Extracted full dictionaries:")
    for new_name in ASSIGNMENTS.values():
        print(f" - {new_name}")
    print(" - HIDDEN_INPUT_VARS")


if __name__ == "__main__":
    main()