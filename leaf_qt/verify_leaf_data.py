from leaf_data import (
    LABEL_TO_VAR,
    SYMBOLS,
    UNITS,
    UNIT_GROUPS,
    UNIT_PREFERENCES,
    SECTIONS,
    HIDDEN_INPUT_VARS,
)


def main():
    all_label_vars = set(LABEL_TO_VAR.values())

    section_labels = []
    for section_name, labels in SECTIONS.items():
        section_labels.extend(labels)

    section_vars = {
        LABEL_TO_VAR.get(label, label)
        for label in section_labels
    }

    missing_from_outputs = sorted(all_label_vars - section_vars)
    output_vars_not_in_label_map = sorted(section_vars - all_label_vars)

    missing_units = sorted(
        var for var in all_label_vars
        if var not in UNITS
    )

    missing_symbols = sorted(
        var for var in section_vars
        if var not in SYMBOLS
    )

    hidden_not_in_label_map = sorted(
        var for var in HIDDEN_INPUT_VARS
        if var not in all_label_vars
    )

    visible_inputs = sorted(all_label_vars - HIDDEN_INPUT_VARS)

    print("\n--- LEAF DATA VERIFICATION ---")
    print(f"LABEL_TO_VAR entries:      {len(LABEL_TO_VAR)}")
    print(f"Unique internal variables: {len(all_label_vars)}")
    print(f"Output section labels:     {len(section_labels)}")
    print(f"Output section variables:  {len(section_vars)}")
    print(f"Hidden input vars:         {len(HIDDEN_INPUT_VARS)}")
    print(f"Visible input vars:        {len(visible_inputs)}")

    print("\n--- POTENTIAL ISSUES ---")

    if missing_from_outputs:
        print("\nVariables in LABEL_TO_VAR but not shown in output sections:")
        for var in missing_from_outputs:
            print(f"  - {var}")
    else:
        print("\nNo LABEL_TO_VAR variables missing from output sections.")

    if output_vars_not_in_label_map:
        print("\nOutput variables not found in LABEL_TO_VAR:")
        for var in output_vars_not_in_label_map:
            print(f"  - {var}")
    else:
        print("\nNo output variables missing from LABEL_TO_VAR.")

    if missing_units:
        print("\nVariables missing units:")
        for var in missing_units:
            print(f"  - {var}")
    else:
        print("\nNo variables missing units.")

    if missing_symbols:
        print("\nOutput variables missing symbols:")
        for var in missing_symbols:
            print(f"  - {var}")
    else:
        print("\nNo output variables missing symbols.")

    if hidden_not_in_label_map:
        print("\nHidden input vars not found in LABEL_TO_VAR:")
        for var in hidden_not_in_label_map:
            print(f"  - {var}")
    else:
        print("\nNo hidden inputs missing from LABEL_TO_VAR.")

    print("\n--- END VERIFICATION ---\n")


if __name__ == "__main__":
    main()