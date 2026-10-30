from __future__ import annotations

import json
import py_compile
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from leaf_qt.core.architecture.repository_metadata import (
    build_repository_metadata,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c8a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FOUNDATION = ROOT / "leaf_qt" / "core" / "architecture" / "repository_metadata.py"


def main() -> None:
    failures: list[str] = []

    if not FOUNDATION.exists():
        failures.append("repository_metadata_foundation_missing")
    else:
        try:
            py_compile.compile(str(FOUNDATION), doraise=True)
        except Exception as exc:
            failures.append(f"repository_metadata_foundation_compile_failure={exc!r}")

    metadata = build_repository_metadata(ROOT)
    summary = metadata["summary"]

    if metadata["schema"] != "LEAF_REPOSITORY_METADATA_V1":
        failures.append("metadata_schema_invalid")

    if summary["python_files"] <= 0:
        failures.append("no_python_files_indexed")

    if summary["supported_files"] < summary["python_files"]:
        failures.append("supported_file_count_invalid")

    if "runtime" not in summary["layer_counts"]:
        failures.append("runtime_layer_missing")

    if "development" not in summary["layer_counts"]:
        failures.append("development_layer_missing")

    if summary["ast_parse_failures"] != 0:
        failures.append("ast_parse_failures_present")

    json_metadata_path = OUT_DIR / "repository_metadata_v1.json"
    json_gate_path = OUT_DIR / "repository_metadata_foundation_gate_phase_17c8a.json"
    txt_gate_path = OUT_DIR / "repository_metadata_foundation_gate_phase_17c8a.txt"

    json_metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    result = {
        "phase": "17C.8A",
        "feature": "REPOSITORY_METADATA_FOUNDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "schema": metadata["schema"],
        "summary": summary,
        "failures": failures,
        "metadata_json": json_metadata_path.relative_to(ROOT).as_posix(),
        "completion_notice": (
            "PHASE_17C8A_COMPLETE_REPOSITORY_METADATA_FOUNDATION_ESTABLISHED"
            if not failures
            else "PHASE_17C8A_BLOCKED"
        ),
        "next_phase": "17C.8B_REPOSITORY_KNOWLEDGE_DATABASE",
    }

    json_gate_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_gate_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.8A REPOSITORY METADATA FOUNDATION",
            "=================================================",
            f"passed={result['passed']}",
            f"schema={result['schema']}",
            f"supported_files={summary['supported_files']}",
            f"python_files={summary['python_files']}",
            f"public_api_candidates={summary['public_api_candidates']}",
            f"ast_parse_failures={summary['ast_parse_failures']}",
            f"runtime_files={summary['layer_counts'].get('runtime', 0)}",
            f"development_files={summary['layer_counts'].get('development', 0)}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"metadata_json={json_metadata_path.relative_to(ROOT)}",
            f"gate_json={json_gate_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C8A_REPOSITORY_METADATA_FOUNDATION" if result["passed"] else "FAIL_PHASE_17C8A_REPOSITORY_METADATA_FOUNDATION")
    print(f"schema={result['schema']}")
    print(f"supported_files={summary['supported_files']}")
    print(f"python_files={summary['python_files']}")
    print(f"public_api_candidates={summary['public_api_candidates']}")
    print(f"ast_parse_failures={summary['ast_parse_failures']}")
    print(f"metadata_json={json_metadata_path.relative_to(ROOT)}")
    print(f"report={txt_gate_path.relative_to(ROOT)}")
    print(f"json={json_gate_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
