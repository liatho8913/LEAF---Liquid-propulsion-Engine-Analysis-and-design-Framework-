from pathlib import Path

FILES = [
    Path("leaf_qt/foundation_result_key_audit.py"),
    Path("leaf_qt/variable_registry.py"),
]

PREFIXES = [
    "phase_14b_",
    "regen_runtime_candidate_evaluation_",
    "regen_runtime_candidate_solver_",
    "regen_runtime_candidate_acceptance_",
    "regen_runtime_candidate_generation_",
    "regen_runtime_candidate_live_",
]

for path in FILES:
    if not path.exists():
        print(f"SKIP {path}")
        continue

    text = path.read_text()

    if "KNOWN_DEVELOPMENT_KEYS = {" in text:
        additions = "\n".join(f'    "{p}",' for p in PREFIXES)
        if '"regen_runtime_candidate_evaluation_",' not in text:
            text = text.replace("KNOWN_DEVELOPMENT_KEYS = {", "KNOWN_DEVELOPMENT_KEYS = {\n" + additions)

    if "EXPECTED_PREFIX_VISIBILITY = {" in text:
        additions = "\n".join(f'    "{p}": "DIAGNOSTIC_ONLY",' for p in PREFIXES)
        if '"regen_runtime_candidate_evaluation_": "DIAGNOSTIC_ONLY",' not in text:
            text = text.replace("EXPECTED_PREFIX_VISIBILITY = {", "EXPECTED_PREFIX_VISIBILITY = {\n" + additions)

    path.write_text(text)
    print(f"PATCHED {path}")

print("PHASE_14B_RESULT_KEYS_REGISTERED")
