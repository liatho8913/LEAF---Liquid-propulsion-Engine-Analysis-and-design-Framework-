from pathlib import Path
import ast
import importlib.util
import sys

SOURCE = Path("leaf_qt/regen_completion_gate_validation_owner.py")


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "regen_completion_gate_validation_owner_phase_16t3w4",
        SOURCE,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_public_api_preserved():
    tree = ast.parse(SOURCE.read_text(errors="replace"))
    public_functions = {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    }

    assert public_functions == {"attach_regen_completion_gate_validation_owner"}


def test_status_adapter_preserves_legacy_failure_payload():
    module = _load_module()

    payload = {}
    adapted = module.attach_regen_completion_gate_validation_owner(dict(payload))

    assert adapted["regen_completion_gate_validation_owner_status"] == module.FAIL_STATUS
    assert adapted["regen_completion_gate_validation_passed"] is False

    assert adapted["phase_16t3w4_status_adapter_complete"] is True
    assert adapted[
        "phase_16t3w4_regen_completion_gate_validation_owner_status_adapter_complete"
    ] is True
    assert adapted[
        "regen_completion_gate_validation_owner_status_adapter_complete"
    ] is True

    assert isinstance(
        adapted["regen_completion_gate_validation_owner_structured_findings"],
        list,
    )
    assert adapted["regen_completion_gate_validation_owner_global_status"] == "FAIL"
    assert isinstance(
        adapted["regen_completion_gate_validation_owner_global_status_payload"],
        dict,
    )
    assert "REGEN COMPLETION GATE VALIDATION OWNER STATUS ADAPTER" in adapted[
        "regen_completion_gate_validation_owner_adapter_report"
    ]

    assert adapted["structured_findings"] == adapted[
        "regen_completion_gate_validation_owner_structured_findings"
    ]
    assert adapted["global_status"] == adapted[
        "regen_completion_gate_validation_owner_global_status"
    ]
    assert adapted["global_status_payload"] == adapted[
        "regen_completion_gate_validation_owner_global_status_payload"
    ]
    assert adapted["adapter_report"] == adapted[
        "regen_completion_gate_validation_owner_adapter_report"
    ]


def test_file_audit_phase_tokens_present():
    text = SOURCE.read_text(errors="replace")

    required = [
        "phase_16t3w4_status_adapter_complete",
        "regen_completion_gate_validation_owner_structured_findings",
        "regen_completion_gate_validation_owner_global_status_payload",
        "regen_completion_gate_validation_owner_adapter_report",
        "regen_completion_gate_validation_owner_legacy_status",
    ]

    missing = [token for token in required if token not in text]
    assert not missing, f"Missing tokens: {missing}"

    forbidden = [
        "attach_regen_completion_gate_validation_owner_v2",
        "class RegenCompletionGateValidationOwner",
    ]

    present = [token for token in forbidden if token in text]
    assert not present, f"Unexpected redesign tokens: {present}"


if __name__ == "__main__":
    test_public_api_preserved()
    test_status_adapter_preserves_legacy_failure_payload()
    test_file_audit_phase_tokens_present()
    print("PASS_PHASE_16T3W4_REGEN_COMPLETION_GATE_VALIDATION_OWNER_STATUS_ADAPTER")
