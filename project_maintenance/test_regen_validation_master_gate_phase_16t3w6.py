from pathlib import Path
import ast
import importlib.util
import sys

sys.path.insert(0, str(Path.cwd()))

SOURCE = Path("leaf_qt/regen_validation_master_gate.py")


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "regen_validation_master_gate_phase_16t3w6",
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

    required = {
        "attach_regen_validation_master_gate",
        "build_regen_validation_master_gate",
        "build_regen_validation_master_gate_report",
    }

    missing = sorted(required - public_functions)
    assert not missing, f"Missing public API: {missing}"


def test_phase_aliases_added_without_losing_legacy_status():
    module = _load_module()

    payload = {
        "regen_validation_status": "PASS_REGEN_VALIDATION_MASTER_GATE",
        "regen_validation_mode_status": "PASS_SOURCED_VALIDATION_MODE",
    }

    adapted = module.attach_regen_validation_master_gate(dict(payload))

    assert "regen_validation_master_gate_status" in adapted
    assert isinstance(adapted["regen_validation_master_gate_status"], str)

    assert adapted["phase_16t3w6_status_adapter_complete"] is True
    assert adapted[
        "phase_16t3w6_regen_validation_master_gate_status_adapter_complete"
    ] is True
    assert adapted["regen_validation_master_gate_status_adapter_complete"] is True

    assert isinstance(adapted["regen_validation_master_gate_adapter_report"], str)
    assert "REGEN VALIDATION MASTER GATE" in adapted[
        "regen_validation_master_gate_adapter_report"
    ]

    assert "structured_findings" in adapted
    assert "global_status" in adapted
    assert "global_status_payload" in adapted
    assert "adapter_report" in adapted

    assert adapted["adapter_report"] == adapted[
        "regen_validation_master_gate_adapter_report"
    ]


def test_file_audit_phase_tokens_present():
    text = SOURCE.read_text(errors="replace")

    required = [
        "phase_16t3w6_status_adapter_complete",
        "phase_16t3w6_regen_validation_master_gate_status_adapter_complete",
        "regen_validation_master_gate_status_adapter_complete",
        "regen_validation_master_gate_adapter_report",
        "structured_findings",
        "global_status_payload",
        "adapter_report",
    ]

    missing = [token for token in required if token not in text]
    assert not missing, f"Missing tokens: {missing}"

    forbidden = [
        "build_regen_validation_master_gate_v2",
        "attach_regen_validation_master_gate_v2",
        "class RegenValidationMasterGate",
    ]

    present = [token for token in forbidden if token in text]
    assert not present, f"Unexpected redesign tokens: {present}"


if __name__ == "__main__":
    test_public_api_preserved()
    test_phase_aliases_added_without_losing_legacy_status()
    test_file_audit_phase_tokens_present()
    print("PASS_PHASE_16T3W6_REGEN_VALIDATION_MASTER_GATE_STATUS_ADAPTER")
