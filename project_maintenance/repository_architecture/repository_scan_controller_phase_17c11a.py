from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

SCHEMA = "LEAF_REPOSITORY_SCAN_CONTROLLER_PHASE_17C11A_V1"

EXCLUDED_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".idea", ".vscode", "build", "dist",

    # LEAF generated / archived / external artefacts.
    "_leaf_artifacts",
    "_leaf_archive",
    "_external_repository_quarantine",
    "_leaf_repository_cleanup_candidates",
    "project_evidence",
    "artifacts",
}

OUT = ROOT / "_leaf_artifacts" / "repository_architecture" / "phase_17c11a"
OUT.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class RepositoryFileRecord:
    path: str
    suffix: str
    size_bytes: int
    modified_ns: int
    sha256: str
    is_python: bool
    top_level_owner: str


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def should_scan(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return not any(part in EXCLUDED_PARTS for part in rel.parts)


def owner_for(path: Path) -> str:
    rel = path.relative_to(ROOT)
    if not rel.parts:
        return "UNKNOWN"
    return rel.parts[0]


def build_repository_snapshot() -> dict[str, Any]:
    records: list[RepositoryFileRecord] = []

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if not should_scan(path):
            continue

        stat = path.stat()
        records.append(
            RepositoryFileRecord(
                path=path.relative_to(ROOT).as_posix(),
                suffix=path.suffix.lower(),
                size_bytes=stat.st_size,
                modified_ns=stat.st_mtime_ns,
                sha256=file_sha256(path),
                is_python=path.suffix.lower() == ".py",
                top_level_owner=owner_for(path),
            )
        )

    owner_counts: dict[str, int] = {}
    suffix_counts: dict[str, int] = {}

    for record in records:
        owner_counts[record.top_level_owner] = owner_counts.get(record.top_level_owner, 0) + 1
        suffix_counts[record.suffix or "<none>"] = suffix_counts.get(record.suffix or "<none>", 0) + 1

    snapshot = {
        "schema": SCHEMA,
        "phase": "17C.11A",
        "feature": "REPOSITORY_SCAN_CONTROLLER_FOUNDATION",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "mode": "SINGLE_REPOSITORY_SNAPSHOT_FOR_SHARED_CONSUMERS",
        "summary": {
            "total_files": len(records),
            "python_files": sum(1 for r in records if r.is_python),
            "top_level_owner_count": len(owner_counts),
            "suffix_count": len(suffix_counts),
            "single_scan_complete": True,
            "shared_snapshot_available": True,
        },
        "owner_counts": dict(sorted(owner_counts.items())),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "files": [asdict(r) for r in records],
        "reuse_policy": {
            "purpose": "All future repository intelligence consumers should read this snapshot instead of independently rescanning the repository.",
            "consumers": [
                "metadata",
                "knowledge_database",
                "dependency_graph",
                "semantic_classification",
                "architecture_validation",
                "visualisation",
                "sorter",
                "duplicate_detection",
                "unused_file_proof",
                "future_ai_repository_tools",
            ],
        },
    }

    return snapshot


def write_snapshot_report() -> dict[str, Any]:
    snapshot = build_repository_snapshot()

    json_path = OUT / "repository_scan_controller_snapshot_phase_17c11a.json"
    txt_path = OUT / "repository_scan_controller_phase_17c11a.txt"

    json_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    s = snapshot["summary"]
    txt_path.write_text(
        "\n".join([
            "LEAF PHASE 17C.11A REPOSITORY SCAN CONTROLLER FOUNDATION",
            "==========================================================",
            f"schema={snapshot['schema']}",
            f"mode={snapshot['mode']}",
            f"total_files={s['total_files']}",
            f"python_files={s['python_files']}",
            f"top_level_owner_count={s['top_level_owner_count']}",
            f"suffix_count={s['suffix_count']}",
            f"single_scan_complete={s['single_scan_complete']}",
            f"shared_snapshot_available={s['shared_snapshot_available']}",
            "completion_notice=PHASE_17C11A_COMPLETE_REPOSITORY_SCAN_CONTROLLER_FOUNDATION_ESTABLISHED",
            "next_phase=17C.11B_SHARED_SNAPSHOT_CONSUMER_ADAPTER",
            f"json={json_path.relative_to(ROOT)}",
        ]),
        encoding="utf-8",
    )

    snapshot["artefacts"] = {
        "report": txt_path.relative_to(ROOT).as_posix(),
        "json": json_path.relative_to(ROOT).as_posix(),
    }

    return snapshot


if __name__ == "__main__":
    payload = write_snapshot_report()
    s = payload["summary"]

    print("PASS_REPOSITORY_SCAN_CONTROLLER_PHASE_17C11A")
    print(f"total_files={s['total_files']}")
    print(f"python_files={s['python_files']}")
    print(f"top_level_owner_count={s['top_level_owner_count']}")
    print(f"suffix_count={s['suffix_count']}")
    print(f"single_scan_complete={s['single_scan_complete']}")
    print(f"shared_snapshot_available={s['shared_snapshot_available']}")
    print(f"report={payload['artefacts']['report']}")
    print(f"json={payload['artefacts']['json']}")
    print("next_phase=17C.11B_SHARED_SNAPSHOT_CONSUMER_ADAPTER")
