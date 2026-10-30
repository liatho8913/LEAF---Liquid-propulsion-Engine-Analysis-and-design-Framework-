from pathlib import Path
import ast

SOURCE = Path("project_maintenance/engine_solver_status_adapter.py")

REQUIRED_PUBLIC_API = {
    "solve_engine",
    "iterative_solver",
    "legacy_iterative_solver",
    "build_engine_solver_status_adapter_report",
    "attach_engine_solver_status_adapter",
}

REQUIRED_TOKENS = {
    "structured_findings",
    "global_status",
    "global_status_payload",
    "adapter_report",
    "build_engine_solver_status_adapter_report",
    "attach_engine_solver_status_adapter",
}

EXPECTED_PHASE_TOKENS = {
    "phase_16t3w2_status_adapter_complete",
    "engine_solver_status_adapter_complete",
    "engine_solver_global_status_payload",
    "engine_solver_adapter_report",
}


def main():
    if not SOURCE.exists():
        raise SystemExit("FAIL_PHASE_16T3W2A_ENGINE_SOLVER_MISSING")

    text = SOURCE.read_text(errors="replace")
    tree = ast.parse(text)

    public_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    missing_api = sorted(REQUIRED_PUBLIC_API - public_functions)
    missing_required_tokens = sorted(
        token for token in REQUIRED_TOKENS if token not in text
    )
    missing_phase_tokens = sorted(
        token for token in EXPECTED_PHASE_TOKENS if token not in text
    )

    duplicate_public_names = []
    seen = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            if node.name in seen:
                duplicate_public_names.append(node.name)
            seen.add(node.name)

    print("LEAF PHASE 16T.3W.2A")
    print("ENGINE SOLVER STATUS ADAPTER ARCHITECTURE AUDIT")
    print("================================================")
    print()
    print(f"source_exists: {SOURCE.exists()}")
    print(f"line_count: {len(text.splitlines())}")
    print(f"public_function_count: {len(public_functions)}")
    print(f"legacy_PASS_count: {text.count('PASS')}")
    print(f"legacy_WARN_count: {text.count('WARN')}")
    print(f"legacy_FAIL_count: {text.count('FAIL')}")
    print()
    print("required_public_api_missing:", missing_api)
    print("required_status_tokens_missing:", missing_required_tokens)
    print("expected_phase_tokens_missing:", missing_phase_tokens)
    print("duplicate_public_function_names:", duplicate_public_names)
    print()

    adapter_present = not missing_required_tokens
    phase_complete = not missing_phase_tokens
    api_preserved = not missing_api

    if api_preserved and adapter_present and not phase_complete:
        print("AUDIT_RESULT: ADAPTER_PRESENT_BUT_PHASE_16T3W2_CONTRACT_INCOMPLETE")
        print("NEXT_ACTION: APPLY_SMALL_COMPLETION_ALIAS_PATCH")
        print("PASS_PHASE_16T3W2A_ENGINE_SOLVER_STATUS_ADAPTER_AUDIT")
        return

    if api_preserved and adapter_present and phase_complete:
        print("AUDIT_RESULT: PHASE_16T3W2_ALREADY_COMPLETE")
        print("PASS_PHASE_16T3W2A_ENGINE_SOLVER_STATUS_ADAPTER_AUDIT")
        return

    print("AUDIT_RESULT: BLOCKED")
    raise SystemExit("FAIL_PHASE_16T3W2A_ENGINE_SOLVER_STATUS_ADAPTER_AUDIT")


if __name__ == "__main__":
    main()
