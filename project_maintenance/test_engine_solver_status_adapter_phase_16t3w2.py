from pathlib import Path
import ast
import importlib.util
import sys

SOURCE = Path("project_maintenance/engine_solver_status_adapter.py")


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "engine_solver_phase_16t3w2",
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
        "solve_engine",
        "iterative_solver",
        "legacy_iterative_solver",
        "build_engine_solver_status_adapter_report",
        "attach_engine_solver_status_adapter",
    }

    missing = sorted(required - public_functions)
    assert not missing, f"Missing public API: {missing}"


def test_engine_solver_adapter_adds_phase_completion_without_changing_legacy_payload():
    module = _load_module()

    payload = {
        "thrust": 3332.0,
        "specific_impulse": 320.0,
        "regen_validation_status": "PASS",
        "thermal_margin": 10.0,
        "legacy_field": "preserve_me",
    }

    before = dict(payload)
    adapted = module.attach_engine_solver_status_adapter(dict(payload))

    for key, value in before.items():
        assert adapted.get(key) == value, f"Legacy payload changed: {key}"

    assert adapted["engine_solver_status_adapter_complete"] is True
    assert adapted["phase_16t3w2_status_adapter_complete"] is True
    assert adapted["phase_16t3w2_engine_solver_status_adapter_complete"] is True

    assert "structured_findings" in adapted
    assert "global_status" in adapted
    assert "global_status_payload" in adapted
    assert "adapter_report" in adapted

    assert "engine_solver_structured_findings" in adapted
    assert "engine_solver_global_status" in adapted
    assert "engine_solver_global_status_payload" in adapted
    assert "engine_solver_adapter_report" in adapted


def test_file_audit_phase_tokens_present():
    text = SOURCE.read_text(errors="replace")

    required_tokens = [
        "phase_16t3w2_status_adapter_complete",
        "phase_16t3w2_engine_solver_status_adapter_complete",
        "engine_solver_status_adapter_complete",
        "structured_findings",
        "global_status_payload",
        "adapter_report",
    ]

    missing = [token for token in required_tokens if token not in text]
    assert not missing, f"Missing phase tokens: {missing}"

    forbidden_tokens = [
        "class EngineSolverStatusAdapter",
        "def solve_engine_v2",
        "def iterative_solver_v2",
    ]

    present = [token for token in forbidden_tokens if token in text]
    assert not present, f"Unexpected redesign tokens: {present}"


if __name__ == "__main__":
    test_public_api_preserved()
    test_engine_solver_adapter_adds_phase_completion_without_changing_legacy_payload()
    test_file_audit_phase_tokens_present()
    print("PASS_PHASE_16T3W2_ENGINE_SOLVER_STATUS_ADAPTER")
