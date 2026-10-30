from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from core.architecture.io import write_json_artifact, write_text_artifact


ENGINE_SOLVER_PATH = Path("leaf_qt/engine_solver.py")
OUT_JSON = Path("artifacts/engine_solver_callable_discovery_audit.json")
OUT_TXT = Path("artifacts/engine_solver_callable_discovery_audit.txt")


SOLVER_KEYWORDS = {
    "solve",
    "solver",
    "engine",
    "performance",
    "thrust",
    "isp",
    "cea",
    "regen",
    "cooling",
    "flow",
    "nozzle",
    "chamber",
}


LOW_VALUE_KEYWORDS = {
    "plot",
    "draw",
    "debug",
    "print",
    "format",
    "export",
    "test",
    "demo",
    "main",
}


def _node_line_count(node: ast.AST) -> int:
    start = getattr(node, "lineno", 0) or 0
    end = getattr(node, "end_lineno", start) or start
    return max(end - start + 1, 0)


def _function_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [arg.arg for arg in node.args.args]


def _score_callable(name: str, args: list[str], line_count: int, parent_class: str | None) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    lowered = name.lower()

    for keyword in SOLVER_KEYWORDS:
        if keyword in lowered:
            score += 20
            reasons.append(f"SOLVER_KEYWORD:{keyword}")

    for keyword in LOW_VALUE_KEYWORDS:
        if keyword in lowered:
            score -= 25
            reasons.append(f"LOW_VALUE_KEYWORD:{keyword}")

    if parent_class:
        score += 10
        reasons.append(f"METHOD_OF_CLASS:{parent_class}")

        parent_lowered = parent_class.lower()
        if "solver" in parent_lowered or "engine" in parent_lowered:
            score += 20
            reasons.append("PARENT_CLASS_SOLVER_LIKE")

    if "self" in args:
        score += 5
        reasons.append("INSTANCE_METHOD")

    if any(arg in {"inputs", "input_data", "params", "parameters", "config", "state"} for arg in args):
        score += 20
        reasons.append("STRUCTURED_INPUT_ARGUMENT")

    if line_count >= 200:
        score += 20
        reasons.append("LARGE_CALLABLE")
    elif line_count >= 50:
        score += 10
        reasons.append("MEDIUM_CALLABLE")

    return max(score, 0), reasons


def discover_callables_from_source(source: str, filename: str = "engine_solver.py") -> dict[str, Any]:
    tree = ast.parse(source, filename=filename)

    candidates: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_methods = [
                child for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]

            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "line_count": _node_line_count(node),
                    "methods": [method.name for method in class_methods],
                    "method_count": len(class_methods),
                }
            )

            for method in class_methods:
                args = _function_args(method)
                line_count = _node_line_count(method)
                score, reasons = _score_callable(method.name, args, line_count, node.name)

                if score <= 0:
                    continue

                candidates.append(
                    {
                        "kind": "method",
                        "name": method.name,
                        "qualified_name": f"{node.name}.{method.name}",
                        "parent_class": node.name,
                        "line": method.lineno,
                        "line_count": line_count,
                        "args": args,
                        "score": score,
                        "reasons": reasons,
                    }
                )

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = _function_args(node)
            line_count = _node_line_count(node)
            score, reasons = _score_callable(node.name, args, line_count, None)

            if score <= 0:
                continue

            candidates.append(
                {
                    "kind": "function",
                    "name": node.name,
                    "qualified_name": node.name,
                    "parent_class": None,
                    "line": node.lineno,
                    "line_count": line_count,
                    "args": args,
                    "score": score,
                    "reasons": reasons,
                }
            )

    candidates.sort(
        key=lambda item: (
            item["score"],
            item["line_count"],
            item["qualified_name"],
        ),
        reverse=True,
    )

    return {
        "classes": classes,
        "candidates": candidates,
    }


def build_engine_solver_callable_discovery_audit(
    path: str | Path = ENGINE_SOLVER_PATH,
) -> dict[str, Any]:
    solver_path = Path(path)

    if not solver_path.exists():
        raise FileNotFoundError(f"Missing engine solver file: {solver_path}")

    source = solver_path.read_text(encoding="utf-8", errors="replace")
    discovery = discover_callables_from_source(source, solver_path.as_posix())

    candidates = discovery["candidates"]

    return {
        "schema": "LEAF_ENGINE_SOLVER_CALLABLE_DISCOVERY_AUDIT_V1",
        "target": solver_path.as_posix(),
        "summary": {
            "classes": len(discovery["classes"]),
            "candidates": len(candidates),
            "top_candidate": candidates[0]["qualified_name"] if candidates else None,
            "top_score": candidates[0]["score"] if candidates else 0,
        },
        "classes": discovery["classes"],
        "top_candidates": candidates[:50],
        "candidates": candidates,
        "safe_to_bind_adapter": False,
        "note": (
            "This audit is discovery-only. It uses AST parsing and does not import, "
            "execute, or modify engine_solver.py."
        ),
    }


def build_text_report(audit: dict[str, Any]) -> str:
    summary = audit["summary"]

    lines = [
        "LEAF ENGINE SOLVER CALLABLE DISCOVERY AUDIT",
        "===========================================",
        f"schema={audit['schema']}",
        f"target={audit['target']}",
        f"safe_to_bind_adapter={audit['safe_to_bind_adapter']}",
        f"classes={summary['classes']}",
        f"candidates={summary['candidates']}",
        f"top_candidate={summary['top_candidate']}",
        f"top_score={summary['top_score']}",
        "",
        "TOP 25 CANDIDATES",
        "-----------------",
    ]

    if not audit["top_candidates"]:
        lines.append("No callable candidates found.")
    else:
        for item in audit["top_candidates"][:25]:
            lines.append(
                f"{item['score']:>3} | "
                f"{item['kind']:<8} | "
                f"{item['line_count']:>5} lines | "
                f"line {item['line']:<5} | "
                f"{item['qualified_name']} | "
                f"args={item['args']}"
            )

    return "\n".join(lines)


def write_engine_solver_callable_discovery_audit() -> dict[str, Any]:
    audit = build_engine_solver_callable_discovery_audit()

    write_json_artifact(audit, OUT_JSON)
    write_text_artifact(build_text_report(audit), OUT_TXT)

    return audit


if __name__ == "__main__":
    result = write_engine_solver_callable_discovery_audit()
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")
    print("PASS_ENGINE_SOLVER_CALLABLE_DISCOVERY_AUDIT")
