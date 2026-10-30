from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_maintenance.repository_architecture.repository_architecture_synchronisation_engine import (
    SCHEMA,
    synchronise_repository_architecture,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9h"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_synchronisation_engine.py"
POST_MOVE_VALIDATION = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9f" / "post_movement_architecture_validation_phase_17c9f.json"


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"synchronisation_engine_compile_failure={exc!r}")

    if not POST_MOVE_VALIDATION.exists():
        failures.append("phase_17c9f_validation_missing")
    else:
        previous = json.loads(POST_MOVE_VALIDATION.read_text(encoding="utf-8"))
        if not previous.get("passed"):
            failures.append("phase_17c9f_not_passed")

    sync = synchronise_repository_architecture(
        ROOT,
        "_leaf_artifacts/repository_architecture/phase_17c9h/synchronised",
    )
    summary = sync["summary"]

    if sync["schema"] != SCHEMA:
        failures.append("sync_schema_invalid")

    if summary["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    if summary["artefact_count"] < 7:
        failures.append("missing_synchronised_artefacts")

    for name, rel in sync["artefacts"].items():
        if not (ROOT / rel).exists():
            failures.append(f"synchronised_artefact_missing={name}:{rel}")

    result = {
        "phase": "17C.9H",
        "feature": "REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "sync": sync,
        "failures": failures,
        "completion_notice": (
            "PHASE_17C9H_COMPLETE_REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE_ESTABLISHED"
            if not failures
            else "PHASE_17C9H_BLOCKED"
        ),
        "next_phase": "17C.9I_INCREMENTAL_REPOSITORY_INTELLIGENCE_UPDATES",
    }

    gate_json = OUT_DIR / "repository_architecture_synchronisation_gate_phase_17c9h.json"
    gate_txt = OUT_DIR / "repository_architecture_synchronisation_gate_phase_17c9h.txt"

    gate_json.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_txt.write_text(
        "\n".join([
            "LEAF PHASE 17C.9H REPOSITORY ARCHITECTURE SYNCHRONISATION ENGINE",
            "==================================================================",
            f"passed={result['passed']}",
            f"supported_files={summary['supported_files']}",
            f"python_files={summary['python_files']}",
            f"file_nodes={summary['file_nodes']}",
            f"owner_nodes={summary['owner_nodes']}",
            f"subsystem_nodes={summary['subsystem_nodes']}",
            f"resolved_dependency_edges={summary['resolved_dependency_edges']}",
            f"architecture_errors={summary['architecture_errors']}",
            f"architecture_warnings={summary['architecture_warnings']}",
            f"semantic_enriched_files={summary['semantic_enriched_files']}",
            f"artefact_count={summary['artefact_count']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={gate_json.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9H_REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE" if result["passed"] else "FAIL_PHASE_17C9H_REPOSITORY_ARCHITECTURE_SYNCHRONISATION_ENGINE")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"file_nodes={summary['file_nodes']}")
    print(f"owner_nodes={summary['owner_nodes']}")
    print(f"subsystem_nodes={summary['subsystem_nodes']}")
    print(f"resolved_dependency_edges={summary['resolved_dependency_edges']}")
    print(f"architecture_errors={summary['architecture_errors']}")
    print(f"artefact_count={summary['artefact_count']}")
    print(f"report={gate_txt.relative_to(ROOT)}")
    print(f"json={gate_json.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
