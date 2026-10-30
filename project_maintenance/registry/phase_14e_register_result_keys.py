from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

PREFIXES = [
    "phase_14e_",
    "regen_runtime_convergence_",
    "regen_runtime_improvement_",
    "regen_runtime_stagnation_",
    "regen_runtime_stop_condition_",
    "runtime_current_best_",
    "runtime_previous_best_",
    "runtime_generation_improvement",
    "runtime_improvement_",
    "runtime_stagnated_",
    "runtime_stagnation_",
    "runtime_convergence_",
    "runtime_max_generation_",
    "runtime_stop_",
    "runtime_baseline_best_",
    "runtime_previous_stagnation_",
    "runtime_max_generations",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    if "KNOWN_DEVELOPMENT_KEYS = {" in text:
        additions = "\n".join(f'    "{p}",' for p in PREFIXES)
        if '"regen_runtime_convergence_",' not in text:
            text = text.replace(
                "KNOWN_DEVELOPMENT_KEYS = {",
                "KNOWN_DEVELOPMENT_KEYS = {\n" + additions
            )

    if "EXPECTED_PREFIX_VISIBILITY = {" in text:
        additions = "\n".join(f'    "{p}": "DIAGNOSTIC_ONLY",' for p in PREFIXES)
        if '"regen_runtime_convergence_": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace(
                "EXPECTED_PREFIX_VISIBILITY = {",
                "EXPECTED_PREFIX_VISIBILITY = {\n" + additions
            )

    path.write_text(text)
    print(f"PATCHED {path}")

print("PHASE_14E_RESULT_KEYS_REGISTERED")
