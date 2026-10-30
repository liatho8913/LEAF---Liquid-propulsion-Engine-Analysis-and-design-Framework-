from __future__ import annotations

import json
import py_compile
from datetime import datetime, timezone
from pathlib import Path

from repository_architecture.universal_repository_sorter_engine import (
    classify_repository,
    compile_active_python,
    select_safe_moves,
)


ROOT = Path(__file__).resolve().parents[1]

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c6v"
OUT_TXT = OUT_DIR / "sorter_engine_consolidation_phase_17c6v.txt"
OUT_JSON = OUT_DIR / "sorter_engine_consolidation_phase_17c6v.json"

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "universal_repository_sorter_engine.py"


def build_consolidation() -> dict:
    classifications = classify_repository(ROOT)
    selected_moves, deferred, rejected = select_safe_moves(ROOT, classifications)

    compile_failures = compile_active_python(ROOT)

    engine_compile_failures = []
    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        engine_compile_failures.append({"path": str(ENGINE.relative_to(ROOT)), "error": repr(exc)})

    hard_blockers = len(compile_failures) + len(engine_compile_failures)

    passed = (
        ENGINE.exists()
        and len(classifications) > 0
        and len(selected_moves) > 0
        and hard_blockers == 0
    )

    return {
        "phase": "17C.6V",
        "name": "Sorter Engine Consolidation",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "engine": str(ENGINE.relative_to(ROOT)),
        "policy": {
            "moves_files": False,
            "deletes_files": False,
            "rewrites_imports": False,
            "consolidation_only": True,
            "creates_reusable_sorter_engine": True,
            "reduces_phase_script_duplication": True,
            "supports_name_signal_sorting": True,
            "supports_purpose_driven_sorting": True,
            "authorises_next_phase": "17C.6W_SORTER_ENGINE_ADOPTION_GATE",
        },
        "counts": {
            "classified_files": len(classifications),
            "selected_moves_from_engine": len(selected_moves),
            "deferred_moves_from_engine": len(deferred),
            "rejected_moves_from_engine": len(rejected),
            "compile_failures": len(compile_failures),
            "engine_compile_failures": len(engine_compile_failures),
            "hard_blockers": hard_blockers,
        },
        "selected_moves_sample": selected_moves[:50],
        "deferred_sample": deferred[:50],
        "rejected_sample": rejected[:50],
        "compile_failures": compile_failures,
        "engine_compile_failures": engine_compile_failures,
        "sorting_algorithm_meaning": [
            "Filename sorting is supported, but it is only one signal.",
            "The engine combines path, filename, imports, content hints, subsystem rules, role rules, and layer rules.",
            "Movement candidates are rejected if confidence is low, destination exists, role is generic, or boundary is unsafe.",
            "Future phase scripts should import this engine instead of reimplementing sorter helpers.",
        ],
        "next_phase": "17C.6W_SORTER_ENGINE_ADOPTION_GATE",
        "passed": passed,
    }


def write_report(result: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    lines = [
        "LEAF PHASE 17C.6V",
        "SORTER ENGINE CONSOLIDATION",
        "=" * 38,
        "",
        f"engine={result['engine']}",
        "",
        "POLICY",
        "------",
    ]

    for key, value in result["policy"].items():
        lines.append(f"{key}={value}")

    lines += ["", "COUNTS", "------"]

    for key, value in result["counts"].items():
        lines.append(f"{key}={value}")

    lines += ["", "SORTING ALGORITHM MEANING", "-------------------------"]

    for item in result["sorting_algorithm_meaning"]:
        lines.append(f"- {item}")

    lines += ["", "SELECTED MOVE SAMPLE", "--------------------"]

    for move in result["selected_moves_sample"]:
        lines.append(
            f"{move['move_id']} :: {move['from']} -> {move['to']} "
            f"[layer={move['layer']}, subsystem={move['subsystem']}, role={move['role']}, confidence={move['confidence']}]"
        )

    lines += [
        "",
        "RESULT",
        "------",
        "PASS_PHASE_17C6V_SORTER_ENGINE_CONSOLIDATION" if result["passed"] else "FAIL_PHASE_17C6V_SORTER_ENGINE_CONSOLIDATION",
        "",
        f"report={OUT_TXT.relative_to(ROOT)}",
        f"json={OUT_JSON.relative_to(ROOT)}",
        "",
        f"next_phase={result['next_phase']}",
    ]

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    result = build_consolidation()
    write_report(result)

    print("PASS_PHASE_17C6V_SORTER_ENGINE_CONSOLIDATION" if result["passed"] else "FAIL_PHASE_17C6V_SORTER_ENGINE_CONSOLIDATION")
    print(f"engine={result['engine']}")
    print(f"classified_files={result['counts']['classified_files']}")
    print(f"selected_moves_from_engine={result['counts']['selected_moves_from_engine']}")
    print(f"deferred_moves_from_engine={result['counts']['deferred_moves_from_engine']}")
    print(f"rejected_moves_from_engine={result['counts']['rejected_moves_from_engine']}")
    print(f"compile_failures={result['counts']['compile_failures']}")
    print(f"engine_compile_failures={result['counts']['engine_compile_failures']}")
    print(f"hard_blockers={result['counts']['hard_blockers']}")
    print(f"report={OUT_TXT.relative_to(ROOT)}")
    print(f"json={OUT_JSON.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
