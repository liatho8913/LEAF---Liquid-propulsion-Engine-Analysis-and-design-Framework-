from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from core.architecture.io import write_json_artifact, write_text_artifact, Mapping

import sys
ROOT = Path(__file__).resolve().parents[3]
LEAF_QT = ROOT / "leaf_qt"
for candidate in (str(ROOT), str(LEAF_QT)):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)


from core.contracts.base_contracts import validate_contract_metadata
from core.solver_adapters.engine_solver_adapter import make_engine_solver_read_only_adapter


OUT_JSON = Path("artifacts/engine_solver_adapter_smoke_harness.json")
OUT_TXT = Path("artifacts/engine_solver_adapter_smoke_harness.txt")


def _minimal_smoke_inputs() -> dict[str, Any]:
    return {
        "smoke_test_mode": True,
        "Pc": 6.895e6,
        "mixture_ratio": 1.875,
        "mass_flow_kg_s": 1.15,
        "throat_area_m2": 3.01e-4,
        "expansion_ratio": 9.12,
    }


def _summarise_result(result: Mapping[str, Any]) -> dict[str, Any]:
    keys = sorted(str(key) for key in result.keys())

    likely_numeric_outputs = [
        key for key, value in result.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]

    return {
        "result_type": type(result).__name__,
        "key_count": len(keys),
        "keys_preview": keys[:50],
        "numeric_output_count": len(likely_numeric_outputs),
        "numeric_outputs_preview": sorted(str(key) for key in likely_numeric_outputs)[:50],
    }


def run_engine_solver_adapter_smoke_harness(
    inputs: Mapping[str, Any] | None = None,
    execute_solver: bool = False,
) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []

    try:
        engine_solver = importlib.import_module("engine_solver")
        solve_engine = getattr(engine_solver, "solve_engine")
        findings.append(
            {
                "status": "PASS",
                "code": "SOLVE_ENGINE_IMPORTED",
                "message": "Imported solve_engine from engine_solver.",
            }
        )
    except Exception as exc:
        return {
            "schema": "LEAF_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS_V1",
            "summary": {
                "passed": False,
                "executed_solver": False,
                "finding_count": 1,
                "failure_count": 1,
            },
            "findings": [
                {
                    "status": "FAIL",
                    "code": "SOLVE_ENGINE_IMPORT_FAILED",
                    "message": str(exc),
                    "exception_type": exc.__class__.__name__,
                }
            ],
            "adapter_metadata": None,
            "adapter_evidence": {},
            "result_summary": None,
            "note": "Import failed before adapter smoke execution.",
        }

    adapter = make_engine_solver_read_only_adapter(solve_engine)
    metadata_result = validate_contract_metadata(adapter)

    findings.append(
        {
            "status": "PASS" if metadata_result.passed else "FAIL",
            "code": "ADAPTER_CONTRACT_METADATA_VALIDATED",
            "message": metadata_result.message,
            "evidence": dict(metadata_result.evidence),
        }
    )

    result_summary = None
    executed_solver = False

    if execute_solver:
        try:
            payload = dict(inputs or _minimal_smoke_inputs())
            result = adapter.solve(payload)
            result_summary = _summarise_result(result)
            executed_solver = True
            findings.append(
                {
                    "status": "PASS",
                    "code": "ADAPTER_SOLVE_EXECUTED",
                    "message": "Adapter executed solve_engine through SolverContract.",
                    "evidence": result_summary,
                }
            )
        except Exception as exc:
            findings.append(
                {
                    "status": "FAIL",
                    "code": "ADAPTER_SOLVE_EXECUTION_FAILED",
                    "message": str(exc),
                    "exception_type": exc.__class__.__name__,
                }
            )
    else:
        findings.append(
            {
                "status": "PASS",
                "code": "DRY_SMOKE_IMPORT_ONLY",
                "message": "Adapter import and metadata path verified. Solver execution intentionally skipped.",
            }
        )

    failure_count = sum(1 for item in findings if item["status"] == "FAIL")

    return {
        "schema": "LEAF_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS_V1",
        "summary": {
            "passed": failure_count == 0,
            "executed_solver": executed_solver,
            "finding_count": len(findings),
            "failure_count": failure_count,
        },
        "findings": findings,
        "adapter_metadata": dict(adapter.contract_metadata()),
        "adapter_evidence": dict(adapter.evidence),
        "result_summary": result_summary,
        "note": (
            "This harness does not modify engine_solver.py. "
            "Default mode imports and validates the adapter without executing solve_engine. "
            "Use execute_solver=True only for controlled smoke execution."
        ),
    }


def build_text_report(result: dict[str, Any]) -> str:
    summary = result["summary"]

    lines = [
        "LEAF ENGINE SOLVER ADAPTER SMOKE HARNESS",
        "========================================",
        f"schema={result['schema']}",
        f"passed={summary['passed']}",
        f"executed_solver={summary['executed_solver']}",
        f"finding_count={summary['finding_count']}",
        f"failure_count={summary['failure_count']}",
        "",
        "FINDINGS",
        "--------",
    ]

    for item in result["findings"]:
        lines.append(f"{item['status']} | {item['code']} | {item['message']}")

    if result.get("result_summary"):
        lines.extend(["", "RESULT SUMMARY", "--------------"])
        for key, value in result["result_summary"].items():
            lines.append(f"{key}={value}")

    return "\n".join(lines)


def write_engine_solver_adapter_smoke_harness(execute_solver: bool = False) -> dict[str, Any]:
    result = run_engine_solver_adapter_smoke_harness(execute_solver=execute_solver)

    write_json_artifact(result, OUT_JSON)
    write_text_artifact(build_text_report(result), OUT_TXT)

    return result


if __name__ == "__main__":
    result = write_engine_solver_adapter_smoke_harness(execute_solver=False)
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")

    if result["summary"]["passed"]:
        print("PASS_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS")
    else:
        print("FAIL_ENGINE_SOLVER_ADAPTER_SMOKE_HARNESS")
        raise SystemExit(1)
