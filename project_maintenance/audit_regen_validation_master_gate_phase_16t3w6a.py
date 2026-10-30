from pathlib import Path
import ast

SOURCE = Path("leaf_qt/regen_validation_master_gate.py")

REQUIRED_PUBLIC_API = {
    "attach_regen_validation_master_gate",
    "build_regen_validation_master_gate",
    "build_regen_validation_master_gate_report",
}

REQUIRED_TOKENS = {
    "structured_findings",
    "global_status",
    "global_status_payload",
    "regen_validation_master_gate_status",
    "regen_validation_master_gate_global_status",
    "regen_validation_master_gate_global_status_payload",
}

EXPECTED_PHASE_TOKENS = {
    "phase_16t3w6_status_adapter_complete",
    "phase_16t3w6_regen_validation_master_gate_status_adapter_complete",
    "regen_validation_master_gate_status_adapter_complete",
    "regen_validation_master_gate_adapter_report",
}


def main():
    if not SOURCE.exists():
        raise SystemExit("FAIL_PHASE_16T3W6A_REGEN_VALIDATION_MASTER_GATE_MISSING")

    text = SOURCE.read_text(errors="replace")
    tree = ast.parse(text)

    public_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    missing_api = sorted(REQUIRED_PUBLIC_API - public_functions)
    missing_required_tokens = sorted(token for token in REQUIRED_TOKENS if token not in text)
    missing_phase_tokens = sorted(token for token in EXPECTED_PHASE_TOKENS if token not in text)

    print("LEAF PHASE 16T.3W.6A")
    print("REGEN VALIDATION MASTER GATE STATUS ADAPTER AUDIT")
    print("=================================================")
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
    print()

    if missing_api:
        print("AUDIT_RESULT: BLOCKED_PUBLIC_API_MISSING")
        raise SystemExit("FAIL_PHASE_16T3W6A_REGEN_VALIDATION_MASTER_GATE_AUDIT")

    if missing_required_tokens:
        print("AUDIT_RESULT: BLOCKED_EXISTING_STRUCTURED_ADAPTER_INCOMPLETE")
        raise SystemExit("FAIL_PHASE_16T3W6A_REGEN_VALIDATION_MASTER_GATE_AUDIT")

    if missing_phase_tokens:
        print("AUDIT_RESULT: ADAPTER_PRESENT_BUT_PHASE_16T3W6_CONTRACT_INCOMPLETE")
        print("NEXT_ACTION: APPLY_SMALL_COMPLETION_ALIAS_PATCH")
    else:
        print("AUDIT_RESULT: PHASE_16T3W6_ALREADY_COMPLETE")

    print("PASS_PHASE_16T3W6A_REGEN_VALIDATION_MASTER_GATE_STATUS_ADAPTER_AUDIT")


if __name__ == "__main__":
    main()
