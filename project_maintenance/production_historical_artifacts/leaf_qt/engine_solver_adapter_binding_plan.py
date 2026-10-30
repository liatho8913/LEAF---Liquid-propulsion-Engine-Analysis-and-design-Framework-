from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from core.architecture.io import write_json_artifact, write_text_artifact


ENGINE_SOLVER_PATH = Path("leaf_qt/engine_solver.py")
OUT_JSON = Path("artifacts/engine_solver_adapter_binding_plan.json")
OUT_TXT = Path("artifacts/engine_solver_adapter_binding_plan.txt")


TARGET_CALLABLE = "solve_engine"
TARGET_ARGS = ["inputs"]


def _function_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args]


def find_top_level_function(source: str, function_name: str) -> dict[str, Any] | None:
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
            return {
                "name": node.name,
                "line": node.lineno,
                "end_line": getattr(node, "end_lineno", node.lineno),
                "line_count": max((getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1, 0),
                "args": _function_args(node),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }

    return None


def build_engine_solver_adapter_binding_plan(
    path: str | Path = ENGINE_SOLVER_PATH,
    target_callable: str = TARGET_CALLABLE,
) -> dict[str, Any]:
    solver_path = Path(path)

    if not solver_path.exists():
        raise FileNotFoundError(f"Missing engine solver file: {solver_path}")

    source = solver_path.read_text(encoding="utf-8", errors="replace")
    target = find_top_level_function(source, target_callable)

    findings: list[dict[str, Any]] = []

    if target is None:
        findings.append(
            {
                "status": "FAIL",
                "code": "TARGET_CALLABLE_NOT_FOUND",
                "message": f"{target_callable} was not found as a top-level function.",
            }
        )
    else:
        if target["args"] != TARGET_ARGS:
            findings.append(
                {
                    "status": "FAIL",
                    "code": "TARGET_SIGNATURE_MISMATCH",
                    "message": f"Expected args {TARGET_ARGS}, found {target['args']}.",
                    "evidence": target,
                }
            )
        else:
            findings.append(
                {
                    "status": "PASS",
                    "code": "TARGET_CALLABLE_SIGNATURE_OK",
                    "message": f"{target_callable} has the expected signature.",
                    "evidence": target,
                }
            )

        if target["is_async"]:
            findings.append(
                {
                    "status": "FAIL",
                    "code": "ASYNC_CALLABLE_NOT_SUPPORTED",
                    "message": "Read-only adapter currently expects a synchronous callable.",
                    "evidence": target,
                }
            )

        if target["line_count"] > 1000:
            findings.append(
                {
                    "status": "WARN",
                    "code": "TARGET_CALLABLE_LARGE",
                    "message": "Callable is large and should later be split behind contracts.",
                    "evidence": target,
                }
            )
        else:
            findings.append(
                {
                    "status": "PASS",
                    "code": "TARGET_CALLABLE_SIZE_ACCEPTABLE_FOR_INITIAL_BINDING",
                    "message": "Callable size is acceptable for first read-only adapter binding.",
                    "evidence": target,
                }
            )

    failed = [item for item in findings if item["status"] == "FAIL"]
    warnings = [item for item in findings if item["status"] == "WARN"]

    safe_to_bind = bool(target is not None and not failed)

    return {
        "schema": "LEAF_ENGINE_SOLVER_ADAPTER_BINDING_PLAN_V1",
        "target_file": solver_path.as_posix(),
        "target_callable": target_callable,
        "target": target,
        "summary": {
            "safe_to_bind_adapter": safe_to_bind,
            "finding_count": len(findings),
            "failure_count": len(failed),
            "warning_count": len(warnings),
        },
        "findings": findings,
        "binding_plan": {
            "adapter": "EngineSolverReadOnlyAdapter",
            "contract": "SolverContract",
            "callable": target_callable,
            "import_required": "from engine_solver import solve_engine",
            "execution_mode": "READ_ONLY",
            "legacy_file_modification_required": False,
            "next_step_if_safe": "Create a binding smoke test that imports solve_engine and calls adapter with minimal controlled inputs.",
        },
        "note": (
            "This plan does not import or execute engine_solver.py. "
            "It only confirms whether the adapter binding target is structurally suitable."
        ),
    }


def build_text_report(plan: dict[str, Any]) -> str:
    summary = plan["summary"]

    lines = [
        "LEAF ENGINE SOLVER ADAPTER BINDING PLAN",
        "=======================================",
        f"schema={plan['schema']}",
        f"target_file={plan['target_file']}",
        f"target_callable={plan['target_callable']}",
        f"safe_to_bind_adapter={summary['safe_to_bind_adapter']}",
        f"failure_count={summary['failure_count']}",
        f"warning_count={summary['warning_count']}",
        "",
        "FINDINGS",
        "--------",
    ]

    for item in plan["findings"]:
        lines.append(
            f"{item['status']} | {item['code']} | {item['message']}"
        )

    lines.extend(
        [
            "",
            "BINDING PLAN",
            "------------",
            f"adapter={plan['binding_plan']['adapter']}",
            f"contract={plan['binding_plan']['contract']}",
            f"callable={plan['binding_plan']['callable']}",
            f"legacy_file_modification_required={plan['binding_plan']['legacy_file_modification_required']}",
            f"execution_mode={plan['binding_plan']['execution_mode']}",
        ]
    )

    return "\n".join(lines)


def write_engine_solver_adapter_binding_plan() -> dict[str, Any]:
    plan = build_engine_solver_adapter_binding_plan()

    write_json_artifact(plan, OUT_JSON)
    write_text_artifact(build_text_report(plan), OUT_TXT)

    return plan


if __name__ == "__main__":
    result = write_engine_solver_adapter_binding_plan()
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")

    if result["summary"]["safe_to_bind_adapter"]:
        print("PASS_ENGINE_SOLVER_ADAPTER_BINDING_PLAN")
    else:
        print("FAIL_ENGINE_SOLVER_ADAPTER_BINDING_PLAN")
        raise SystemExit(1)
