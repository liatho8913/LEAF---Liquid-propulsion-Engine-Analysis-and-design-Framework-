from pathlib import Path
import tempfile

from project_maintenance.production_historical_artifacts.leaf_qt.engine_solver_adapter_binding_plan import (
    build_engine_solver_adapter_binding_plan,
    build_text_report,
    find_top_level_function,
)


def test_find_top_level_function_detects_solve_engine():
    source = '''
def solve_engine(inputs):
    return {"ok": True}
'''

    found = find_top_level_function(source, "solve_engine")

    assert found is not None
    assert found["name"] == "solve_engine"
    assert found["args"] == ["inputs"]


def test_binding_plan_passes_expected_signature():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "engine_solver.py"
        path.write_text(
            '''
def solve_engine(inputs):
    return {"ok": True}
''',
            encoding="utf-8",
        )

        plan = build_engine_solver_adapter_binding_plan(path)

        assert plan["schema"] == "LEAF_ENGINE_SOLVER_ADAPTER_BINDING_PLAN_V1"
        assert plan["summary"]["safe_to_bind_adapter"] is True
        assert plan["summary"]["failure_count"] == 0


def test_binding_plan_fails_missing_callable():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "engine_solver.py"
        path.write_text(
            '''
def other_function(inputs):
    return {"ok": True}
''',
            encoding="utf-8",
        )

        plan = build_engine_solver_adapter_binding_plan(path)

        assert plan["summary"]["safe_to_bind_adapter"] is False
        assert plan["summary"]["failure_count"] == 1
        assert plan["findings"][0]["code"] == "TARGET_CALLABLE_NOT_FOUND"


def test_binding_plan_fails_signature_mismatch():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "engine_solver.py"
        path.write_text(
            '''
def solve_engine(params, extra):
    return {"ok": True}
''',
            encoding="utf-8",
        )

        plan = build_engine_solver_adapter_binding_plan(path)

        assert plan["summary"]["safe_to_bind_adapter"] is False
        assert any(item["code"] == "TARGET_SIGNATURE_MISMATCH" for item in plan["findings"])


def test_binding_plan_report_contains_plan():
    plan = {
        "schema": "LEAF_ENGINE_SOLVER_ADAPTER_BINDING_PLAN_V1",
        "target_file": "leaf_qt/engine_solver.py",
        "target_callable": "solve_engine",
        "summary": {
            "safe_to_bind_adapter": True,
            "failure_count": 0,
            "warning_count": 0,
        },
        "findings": [
            {
                "status": "PASS",
                "code": "TARGET_CALLABLE_SIGNATURE_OK",
                "message": "solve_engine has the expected signature.",
            }
        ],
        "binding_plan": {
            "adapter": "EngineSolverReadOnlyAdapter",
            "contract": "SolverContract",
            "callable": "solve_engine",
            "legacy_file_modification_required": False,
            "execution_mode": "READ_ONLY",
        },
    }

    report = build_text_report(plan)

    assert "LEAF ENGINE SOLVER ADAPTER BINDING PLAN" in report
    assert "EngineSolverReadOnlyAdapter" in report


if __name__ == "__main__":
    test_find_top_level_function_detects_solve_engine()
    test_binding_plan_passes_expected_signature()
    test_binding_plan_fails_missing_callable()
    test_binding_plan_fails_signature_mismatch()
    test_binding_plan_report_contains_plan()
    print("PASS_ENGINE_SOLVER_ADAPTER_BINDING_PLAN_TEST")
