from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_semantic_classification_engine import (
    SCHEMA,
    build_semantic_classification,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8e"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEMANTIC_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "repository_semantic_classification_engine.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(SEMANTIC_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"semantic_classification_engine_compile_failure={exc!r}")

    result = build_semantic_classification(ROOT)
    summary = result["summary"]

    if result["schema"] != SCHEMA:
        failures.append("semantic_schema_invalid")

    if result["database_schema"] != "LEAF_REPOSITORY_KNOWLEDGE_DATABASE_V1":
        failures.append("database_schema_invalid")

    if result["metadata_schema"] != "LEAF_REPOSITORY_METADATA_V1":
        failures.append("metadata_schema_invalid")

    if summary["file_count"] <= 0:
        failures.append("no_files_semantically_classified")

    if summary["semantic_enriched_files"] <= 0:
        failures.append("no_files_semantically_enriched")

    if summary["signal_count"] < 5:
        failures.append("not_enough_semantic_signals")

    semantic_path = OUT_DIR / "repository_semantic_classification_v1.json"
    gate_json = OUT_DIR / "repository_semantic_classification_gate_phase_17c8e.json"
    gate_txt = OUT_DIR / "repository_semantic_classification_gate_phase_17c8e.txt"

    semantic_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate = {
        "phase": "17C.8E",
        "feature": "SEMANTIC_CLASSIFICATION_ENGINE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": result["schema"],
        "database_schema": result["database_schema"],
        "metadata_schema": result["metadata_schema"],
        "summary": summary,
        "failures": failures,
        "semantic_json": semantic_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8E_COMPLETE_SEMANTIC_CLASSIFICATION_ENGINE_ESTABLISHED"
            if not failures
            else "PHASE_17C8E_BLOCKED"
        ),
        "next_phase": "17C.8F_REPOSITORY_INTELLIGENCE_API",
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8E SEMANTIC CLASSIFICATION ENGINE",
            "===================================================",
            f"passed={gate['passed']}",
            f"schema={gate['schema']}",
            f"database_schema={gate['database_schema']}",
            f"metadata_schema={gate['metadata_schema']}",
            f"file_count={summary['file_count']}",
            f"semantic_enriched_files={summary['semantic_enriched_files']}",
            f"changed_subsystem_count={summary['changed_subsystem_count']}",
            f"changed_role_count={summary['changed_role_count']}",
            f"signal_count={summary['signal_count']}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"semantic_json={semantic_path.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8E_SEMANTIC_CLASSIFICATION_ENGINE" if gate["passed"] else "FAIL_PHASE_17C8E_SEMANTIC_CLASSIFICATION_ENGINE")
    print(f"schema={gate['schema']}")
    print(f"file_count={summary['file_count']}")
    print(f"semantic_enriched_files={summary['semantic_enriched_files']}")
    print(f"changed_subsystem_count={summary['changed_subsystem_count']}")
    print(f"changed_role_count={summary['changed_role_count']}")
    print(f"signal_count={summary['signal_count']}")
    print(f"semantic_json={semantic_path.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
