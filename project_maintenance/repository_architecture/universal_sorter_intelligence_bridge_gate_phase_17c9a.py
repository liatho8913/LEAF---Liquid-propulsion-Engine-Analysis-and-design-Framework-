from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.universal_sorter_intelligence_bridge import (
    SCHEMA,
    build_sorter_intelligence_bridge,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BRIDGE_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "universal_sorter_intelligence_bridge.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(BRIDGE_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"bridge_compile_failure={exc!r}")

    result = build_sorter_intelligence_bridge(ROOT)
    summary = result["summary"]

    if result["schema"] != SCHEMA:
        failures.append("bridge_schema_invalid")

    if result["api_schema"] != "LEAF_REPOSITORY_INTELLIGENCE_API_V1":
        failures.append("api_schema_invalid")

    if summary["files_considered"] <= 0:
        failures.append("no_files_considered")

    if summary["sorter_ready_files"] <= 0:
        failures.append("no_sorter_ready_files")

    if summary["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    if summary["semantic_enriched_files"] <= 0:
        failures.append("semantic_enrichment_missing")

    bridge_json = OUT_DIR / "universal_sorter_intelligence_bridge_v1.json"
    gate_json = OUT_DIR / "universal_sorter_intelligence_bridge_gate_phase_17c9a.json"
    gate_txt = OUT_DIR / "universal_sorter_intelligence_bridge_gate_phase_17c9a.txt"

    bridge_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate = {
        "phase": "17C.9A",
        "feature": "UNIVERSAL_SORTER_INTEGRATION_WITH_REPOSITORY_INTELLIGENCE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": result["schema"],
        "api_schema": result["api_schema"],
        "summary": summary,
        "failures": failures,
        "bridge_json": bridge_json.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C9A_COMPLETE_UNIVERSAL_SORTER_INTELLIGENCE_BRIDGE_ESTABLISHED"
            if not failures
            else "PHASE_17C9A_BLOCKED"
        ),
        "next_phase": "17C.9B_INTELLIGENCE_GUIDED_SORTER_PLANNING_GATE",
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.9A UNIVERSAL SORTER INTELLIGENCE BRIDGE",
            "=======================================================",
            f"passed={gate['passed']}",
            f"schema={gate['schema']}",
            f"api_schema={gate['api_schema']}",
            f"files_considered={summary['files_considered']}",
            f"sorter_ready_files={summary['sorter_ready_files']}",
            f"already_aligned_files={summary['already_aligned_files']}",
            f"candidate_move_count={summary['candidate_move_count']}",
            f"architecture_errors={summary['architecture_errors']}",
            f"semantic_enriched_files={summary['semantic_enriched_files']}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"bridge_json={bridge_json.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9A_UNIVERSAL_SORTER_INTELLIGENCE_BRIDGE" if gate["passed"] else "FAIL_PHASE_17C9A_UNIVERSAL_SORTER_INTELLIGENCE_BRIDGE")
    print(f"files_considered={summary['files_considered']}")
    print(f"sorter_ready_files={summary['sorter_ready_files']}")
    print(f"already_aligned_files={summary['already_aligned_files']}")
    print(f"candidate_move_count={summary['candidate_move_count']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"bridge_json={bridge_json.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
