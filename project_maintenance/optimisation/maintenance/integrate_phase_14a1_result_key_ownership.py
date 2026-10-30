from pathlib import Path

TARGETS = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/output_ownership_audit.py"),
]

PREFIXES = [
    "phase_13k_",
    "phase_13l_",
    "phase_14a_",
    "phase_14b_",
    "phase_14c_",
    "phase_14d_",
    "phase_14e_",
    "phase_14f_",

    "selection_",
    "selected_for_parent_pool",
    "survives_generation",

    "regen_optimisation_selection_",
    "regen_optimisation_parent_pool",
    "regen_optimisation_parent_pool_",
    "regen_optimisation_foundation_",

    "optimisation_foundation_",

    "regen_runtime_mutation_",
    "regen_runtime_candidate_",
]

for path in TARGETS:
    if not path.exists():
        print(f"SKIP missing {path}")
        continue

    text = path.read_text()

    marker = "KNOWN_DEVELOPMENT_KEYS = {"

    if marker in text:
        insert = "\n".join(f'    "{prefix}",' for prefix in PREFIXES)

        if '"phase_14a_",' not in text:
            text = text.replace(
                marker,
                marker + "\n" + insert + "\n"
            )

    prefix_marker = "EXPECTED_PREFIX_VISIBILITY = {"

    if prefix_marker in text:
        insert = "\n".join(
            f'    "{prefix}": "DIAGNOSTIC_ONLY",'
            for prefix in PREFIXES
        )

        if '"phase_14a_": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace(
                prefix_marker,
                prefix_marker + "\n" + insert + "\n"
            )

    if "def _is_known_development_key(key):" in text:
        hook = "    key_l = str(key).lower()\n"

        patch = '''
    phase_13_to_14_prefixes = (
        "phase_13k_",
        "phase_13l_",
        "phase_14a_",
        "phase_14b_",
        "phase_14c_",
        "phase_14d_",
        "phase_14e_",
        "phase_14f_",
        "selection_",
        "regen_optimisation_selection_",
        "regen_optimisation_parent_pool",
        "regen_optimisation_foundation_",
        "optimisation_foundation_",
        "regen_runtime_mutation_",
        "regen_runtime_candidate_",
    )

    if key_l.startswith(phase_13_to_14_prefixes):
        return True

    if key_l in {
        "selected_for_parent_pool",
        "survives_generation",
        "selection_rank",
        "selection_score",
    }:
        return True

'''

        if "phase_13_to_14_prefixes" not in text:
            text = text.replace(hook, hook + patch)

    path.write_text(text)
    print(f"PATCHED {path}")

print("Phase 14A.1 result key ownership integration complete.")
