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
    synchronise_repository_architecture,
)

OUT_DIR = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9i"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SYNC_ENGINE = ROOT / "project_maintenance" / "repository_architecture" / "repository_architecture_synchronisation_engine.py"
PREVIOUS_METADATA = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c9h" / "synchronised" / "repository_metadata_v1.json"

SCHEMA = "LEAF_INCREMENTAL_REPOSITORY_INTELLIGENCE_UPDATES_V1"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_digest_map(metadata: dict) -> dict[str, str]:
    return {
        item["path"]: item["content_sha256"]
        for item in metadata.get("files", [])
    }


def detect_changes(previous: dict, current: dict) -> dict:
    previous_map = file_digest_map(previous)
    current_map = file_digest_map(current)

    previous_paths = set(previous_map)
    current_paths = set(current_map)

    added = sorted(current_paths - previous_paths)
    removed = sorted(previous_paths - current_paths)

    changed = sorted(
        path for path in previous_paths & current_paths
        if previous_map[path] != current_map[path]
    )

    unchanged = sorted(
        path for path in previous_paths & current_paths
        if previous_map[path] == current_map[path]
    )

    return {
        "added_files": added,
        "removed_files": removed,
        "changed_files": changed,
        "unchanged_files": unchanged,
        "summary": {
            "previous_file_count": len(previous_paths),
            "current_file_count": len(current_paths),
            "added_count": len(added),
            "removed_count": len(removed),
            "changed_count": len(changed),
            "unchanged_count": len(unchanged),
            "incremental_candidate_count": len(added) + len(removed) + len(changed),
        },
    }


def main() -> None:
    failures: list[str] = []

    try:
        py_compile.compile(str(SYNC_ENGINE), doraise=True)
    except Exception as exc:
        failures.append(f"sync_engine_compile_failure={exc!r}")

    if not PREVIOUS_METADATA.exists():
        failures.append("previous_phase_17c9h_metadata_missing")

    previous_metadata = load_json(PREVIOUS_METADATA) if PREVIOUS_METADATA.exists() else {}

    sync = synchronise_repository_architecture(
        ROOT,
        "_leaf_artifacts/repository_architecture/phase_17c9i/current_synchronised",
    )

    current_metadata_path = ROOT / sync["artefacts"]["metadata"]
    current_metadata = load_json(current_metadata_path)

    changes = detect_changes(previous_metadata, current_metadata)

    if sync["summary"]["architecture_errors"] != 0:
        failures.append("architecture_errors_present")

    if sync["summary"]["supported_files"] <= 0:
        failures.append("no_supported_files")

    result = {
        "phase": "17C.9I",
        "feature": "INCREMENTAL_REPOSITORY_INTELLIGENCE_UPDATES",
        "schema": SCHEMA,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "passed": not failures,
        "sync_schema": sync["schema"],
        "sync_summary": sync["summary"],
        "change_summary": changes["summary"],
        "added_files": changes["added_files"],
        "removed_files": changes["removed_files"],
        "changed_files": changes["changed_files"],
        "failures": failures,
        "completion_notice": (
            "PHASE_17C9I_COMPLETE_INCREMENTAL_REPOSITORY_INTELLIGENCE_UPDATES_ESTABLISHED"
            if not failures
            else "PHASE_17C9I_BLOCKED"
        ),
        "next_phase": "17C.9J_CONTINUOUS_REPOSITORY_INTEGRITY_GATE",
    }

    json_path = OUT_DIR / "incremental_repository_intelligence_updates_phase_17c9i.json"
    txt_path = OUT_DIR / "incremental_repository_intelligence_updates_phase_17c9i.txt"

    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.9I INCREMENTAL REPOSITORY INTELLIGENCE UPDATES",
            "================================================================",
            f"passed={result['passed']}",
            f"previous_file_count={changes['summary']['previous_file_count']}",
            f"current_file_count={changes['summary']['current_file_count']}",
            f"added_count={changes['summary']['added_count']}",
            f"removed_count={changes['summary']['removed_count']}",
            f"changed_count={changes['summary']['changed_count']}",
            f"unchanged_count={changes['summary']['unchanged_count']}",
            f"incremental_candidate_count={changes['summary']['incremental_candidate_count']}",
            f"architecture_errors={sync['summary']['architecture_errors']}",
            f"architecture_warnings={sync['summary']['architecture_warnings']}",
            f"completion_notice={result['completion_notice']}",
            f"next_phase={result['next_phase']}",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    print("PASS_PHASE_17C9I_INCREMENTAL_REPOSITORY_INTELLIGENCE_UPDATES" if result["passed"] else "FAIL_PHASE_17C9I_INCREMENTAL_REPOSITORY_INTELLIGENCE_UPDATES")
    print(f"previous_file_count={changes['summary']['previous_file_count']}")
    print(f"current_file_count={changes['summary']['current_file_count']}")
    print(f"added_count={changes['summary']['added_count']}")
    print(f"removed_count={changes['summary']['removed_count']}")
    print(f"changed_count={changes['summary']['changed_count']}")
    print(f"unchanged_count={changes['summary']['unchanged_count']}")
    print(f"incremental_candidate_count={changes['summary']['incremental_candidate_count']}")
    print(f"architecture_errors={sync['summary']['architecture_errors']}")
    print(f"report={txt_path.relative_to(ROOT)}")
    print(f"json={json_path.relative_to(ROOT)}")
    print(f"next_phase={result['next_phase']}")

    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
