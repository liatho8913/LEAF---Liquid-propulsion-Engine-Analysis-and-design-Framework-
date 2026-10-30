from pathlib import Path

registry_files = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

KEYS = [
    "phase_14_runtime_optimisation_allowed",
    "regen_evolution_engine_execution_allowed",
    "regen_generation_advance_execution_allowed",
]

for path in registry_files:

    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    #
    # Add to KNOWN_DEVELOPMENT_KEYS
    #

    if "KNOWN_DEVELOPMENT_KEYS" in text:

        marker = "KNOWN_DEVELOPMENT_KEYS = {"

        additions = "\n".join(
            f'    "{k}",'
            for k in KEYS
        )

        for k in KEYS:
            if f'"{k}"' in text:
                break
        else:
            text = text.replace(
                marker,
                marker + "\n" + additions + "\n"
            )

    #
    # Add visibility mapping
    #

    if "EXPECTED_PREFIX_VISIBILITY" in text:

        marker = "EXPECTED_PREFIX_VISIBILITY = {"

        additions = "\n".join(
            f'    "{k}": "DIAGNOSTIC_ONLY",'
            for k in KEYS
        )

        missing = [
            k for k in KEYS
            if f'"{k}": "DIAGNOSTIC_ONLY"' not in text
        ]

        if missing:
            text = text.replace(
                marker,
                marker + "\n" + additions + "\n"
            )

    path.write_text(text)

    print(f"PATCHED {path}")

print()
print("PHASE_14A2_REMAINING_KEYS_REGISTERED")
