from pathlib import Path
import tempfile

from project_maintenance.production_historical_artifacts.leaf_qt.engine_solver_callable_discovery_audit import (
    build_engine_solver_callable_discovery_audit,
    discover_callables_from_source,
    build_text_report,
)


def test_discovery_finds_solver_like_method():
    source = '''
class EngineSolver:
    def __init__(self):
        pass

    def solve_engine(self, inputs):
        thrust = inputs["mdot"] * inputs["ve"]
        return {"thrust": thrust}

def format_output(value):
    return str(value)
'''

    result = discover_callables_from_source(source)

    candidates = result["candidates"]
    names = [item["qualified_name"] for item in candidates]

    assert "EngineSolver.solve_engine" in names
    assert "format_output" not in names
    assert candidates[0]["qualified_name"] == "EngineSolver.solve_engine"


def test_discovery_audit_reads_file_without_importing():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "engine_solver.py"
        path.write_text(
            '''
class EngineSolver:
    def solve(self, inputs):
        return {"ok": True}
''',
            encoding="utf-8",
        )

        audit = build_engine_solver_callable_discovery_audit(path)

        assert audit["schema"] == "LEAF_ENGINE_SOLVER_CALLABLE_DISCOVERY_AUDIT_V1"
        assert audit["summary"]["classes"] == 1
        assert audit["summary"]["candidates"] >= 1
        assert audit["safe_to_bind_adapter"] is False


def test_discovery_report_contains_candidate():
    audit = {
        "schema": "LEAF_ENGINE_SOLVER_CALLABLE_DISCOVERY_AUDIT_V1",
        "target": "leaf_qt/engine_solver.py",
        "safe_to_bind_adapter": False,
        "summary": {
            "classes": 1,
            "candidates": 1,
            "top_candidate": "EngineSolver.solve",
            "top_score": 50,
        },
        "top_candidates": [
            {
                "score": 50,
                "kind": "method",
                "line_count": 5,
                "line": 10,
                "qualified_name": "EngineSolver.solve",
                "args": ["self", "inputs"],
            }
        ],
    }

    report = build_text_report(audit)

    assert "LEAF ENGINE SOLVER CALLABLE DISCOVERY AUDIT" in report
    assert "EngineSolver.solve" in report


if __name__ == "__main__":
    test_discovery_finds_solver_like_method()
    test_discovery_audit_reads_file_without_importing()
    test_discovery_report_contains_candidate()
    print("PASS_ENGINE_SOLVER_CALLABLE_DISCOVERY_AUDIT_TEST")
