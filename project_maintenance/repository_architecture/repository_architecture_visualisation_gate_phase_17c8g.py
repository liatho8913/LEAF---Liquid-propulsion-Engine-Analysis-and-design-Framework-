from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_architecture_visualisation import (
    SCHEMA,
    build_architecture_visualisation,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8g"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIS_MODULE = ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_visualisation.py"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(VIS_MODULE), doraise=True)
    except Exception as exc:
        failures.append(f"architecture_visualisation_compile_failure={exc!r}")

    result = build_architecture_visualisation(ROOT)
    summary = result["summary"]

    if result["schema"] != SCHEMA:
        failures.append("visualisation_schema_invalid")

    if result["api_schema"] != "LEAF_REPOSITORY_INTELLIGENCE_API_V1":
        failures.append("api_schema_invalid")

    if summary["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    if not result["top_subsystems"]:
        failures.append("no_subsystems_visualised")

    if not result["top_owners"]:
        failures.append("no_owners_visualised")

    if "flowchart TD" not in result["mermaid"]:
        failures.append("mermaid_graph_missing")

    if "# LEAF Repository Architecture Map" not in result["markdown"]:
        failures.append("markdown_map_missing")

    json_path = OUT_DIR / "repository_architecture_visualisation_v1.json"
    md_path = OUT_DIR / "repository_architecture_map.md"
    mmd_path = OUT_DIR / "repository_architecture_map.mmd"
    gate_json = OUT_DIR / "repository_architecture_visualisation_gate_phase_17c8g.json"
    gate_txt = OUT_DIR / "repository_architecture_visualisation_gate_phase_17c8g.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    md_path.write_text(result["markdown"], encoding="utf-8")
    mmd_path.write_text(result["mermaid"], encoding="utf-8")

    gate = {
        "phase": "17C.8G",
        "feature": "ARCHITECTURE_VISUALISATION_FOUNDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": result["schema"],
        "api_schema": result["api_schema"],
        "summary": summary,
        "top_subsystem_count": len(result["top_subsystems"]),
        "top_owner_count": len(result["top_owners"]),
        "failures": failures,
        "visualisation_json": json_path.relative_to(ROOT).as_posix(),
        "markdown_map": md_path.relative_to(ROOT).as_posix(),
        "mermaid_map": mmd_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8G_COMPLETE_ARCHITECTURE_VISUALISATION_FOUNDATION_ESTABLISHED"
            if not failures
            else "PHASE_17C8G_BLOCKED"
        ),
        "next_phase": "17C.8H_REPOSITORY_INTELLIGENCE_COMPLETION_GATE",
    }

    gate_json.write_text(json.dumps(gate, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.8G ARCHITECTURE VISUALISATION FOUNDATION",
            "==========================================================",
            f"passed={gate['passed']}",
            f"schema={gate['schema']}",
            f"api_schema={gate['api_schema']}",
            f"supported_files={summary['supported_files']}",
            f"python_files={summary['python_files']}",
            f"subsystems={summary['subsystem_nodes']}",
            f"owners={summary['owner_nodes']}",
            f"architecture_errors={summary['architecture_errors']}",
            f"architecture_warnings={summary['architecture_warnings']}",
            f"top_subsystem_count={gate['top_subsystem_count']}",
            f"top_owner_count={gate['top_owner_count']}",
            f"completion_notice={gate['completion_notice']}",
            f"next_phase={gate['next_phase']}",
            f"visualisation_json={json_path.relative_to(ROOT)}",
            f"markdown_map={md_path.relative_to(ROOT)}",
            f"mermaid_map={mmd_path.relative_to(ROOT)}",
            f"gate_json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8G_ARCHITECTURE_VISUALISATION_FOUNDATION" if gate["passed"] else "FAIL_PHASE_17C8G_ARCHITECTURE_VISUALISATION_FOUNDATION")
    print(f"schema={gate['schema']}")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"subsystems={summary['subsystem_nodes']}")
    print(f"owners={summary['owner_nodes']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"markdown_map={md_path.relative_to(ROOT)}")
    print(f"mermaid_map={mmd_path.relative_to(ROOT)}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={gate['next_phase']}")

    if not gate["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
