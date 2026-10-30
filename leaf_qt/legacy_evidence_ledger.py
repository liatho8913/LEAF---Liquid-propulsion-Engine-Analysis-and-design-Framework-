from __future__ import annotations

from pathlib import Path
import shutil
from typing import Any

from core.architecture.io import ensure_artifact_parent, write_json_artifact, write_text_artifact


OUT_JSON = Path("artifacts/legacy_evidence_ledger.json")
OUT_TXT = Path("artifacts/legacy_evidence_ledger.txt")
EVIDENCE_ROOT = Path("project_evidence")


EXCLUDED_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    "project_evidence",
    "build",
    "dist",
}


def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDED_DIRS)


def classify_evidence_file(path: Path) -> str:
    name = path.name.lower()
    rel = path.as_posix().lower()

    if path.name == "promethean_forge.py":
        return "legacy_systems"

    if "handover" in name:
        return "handovers"

    if "certificate" in name or "closeout" in name:
        return "certificates"

    if "gate" in name:
        return "gates"

    if "plan" in name or "roadmap" in name:
        return "plans"

    if "phase_" in name or "phase_" in rel or "integrate_phase_" in name:
        return "phase_artifacts"

    if rel.startswith("artifacts/"):
        return "generated_artifacts"

    return "review"


def iter_direct_evidence_files(root: Path) -> list[Path]:
    files: list[Path] = []

    search_roots = [
        root,
        root / "artifacts",
        root / "project_maintenance",
    ]

    for search_root in search_roots:
        if not search_root.exists():
            continue

        for path in search_root.rglob("*"):
            if not path.is_file():
                continue

            rel = path.relative_to(root)

            if _is_excluded(rel):
                continue

            name = path.name.lower()
            rel_text = rel.as_posix().lower()

            if (
                path.name == "promethean_forge.py"
                or "handover" in name
                or "certificate" in name
                or "closeout" in name
                or "gate" in name
                or "roadmap" in name
                or "plan" in name
                or "phase_" in name
                or "integrate_phase_" in name
                or rel_text.startswith("artifacts/")
            ):
                files.append(path)

    return sorted(set(files))


def summarise_repository_snapshot(root: Path, snapshot_root: Path) -> dict[str, Any]:
    if not snapshot_root.exists():
        return {
            "path": snapshot_root.relative_to(root).as_posix(),
            "exists": False,
            "file_count": 0,
            "python_file_count": 0,
            "size_bytes": 0,
        }

    file_count = 0
    python_file_count = 0
    size_bytes = 0

    for path in snapshot_root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path.relative_to(root)):
            continue

        file_count += 1
        size_bytes += path.stat().st_size
        if path.suffix == ".py":
            python_file_count += 1

    return {
        "path": snapshot_root.relative_to(root).as_posix(),
        "exists": True,
        "file_count": file_count,
        "python_file_count": python_file_count,
        "size_bytes": size_bytes,
        "storage_policy": "Represented as one repository snapshot evidence object, not copied file-by-file.",
    }


def evidence_destination(root: Path, source: Path, category: str) -> Path:
    rel = source.relative_to(root)
    return root / EVIDENCE_ROOT / category / rel


def build_legacy_evidence_ledger(root: str | Path = ".", copy_files: bool = False) -> dict[str, Any]:
    root_path = Path(root).resolve()

    direct_files = iter_direct_evidence_files(root_path)
    entries: list[dict[str, Any]] = []

    for source in direct_files:
        category = classify_evidence_file(source.relative_to(root_path))
        destination = evidence_destination(root_path, source, category)

        copied = False
        if copy_files:
            ensure_artifact_parent(destination)
            if not destination.exists():
                shutil.copy2(source, destination)
                copied = True

        entries.append(
            {
                "type": "file_evidence",
                "source": source.relative_to(root_path).as_posix(),
                "category": category,
                "evidence_destination": destination.relative_to(root_path).as_posix(),
                "copied": copied,
                "size_bytes": source.stat().st_size,
                "suffix": source.suffix,
                "report_use": "Report evidence for LEAF development history.",
            }
        )

    snapshot_roots = [
        root_path / "_external_repository_quarantine",
    ]

    snapshots = [
        summarise_repository_snapshot(root_path, snapshot)
        for snapshot in snapshot_roots
    ]

    category_counts: dict[str, int] = {}
    for entry in entries:
        category_counts[entry["category"]] = category_counts.get(entry["category"], 0) + 1

    for snapshot in snapshots:
        if snapshot["exists"]:
            category_counts["repository_snapshots"] = category_counts.get("repository_snapshots", 0) + 1

    return {
        "schema": "LEAF_LEGACY_EVIDENCE_LEDGER_V2",
        "passed": True,
        "summary": {
            "file_evidence_entries": len(entries),
            "repository_snapshot_entries": sum(1 for item in snapshots if item["exists"]),
            "copied_files": sum(1 for entry in entries if entry["copied"]),
            "copy_files": copy_files,
            "category_counts": dict(sorted(category_counts.items())),
        },
        "evidence_root": EVIDENCE_ROOT.as_posix(),
        "entries": entries,
        "repository_snapshots": snapshots,
        "policy": {
            "evidence_unit": "engineering_milestone_or_repository_snapshot",
            "do_not_copy_virtualenv": True,
            "do_not_copy_quarantine_file_by_file": True,
            "do_not_delete_history": True,
            "do_not_keep_legacy_as_live_runtime": True,
            "storage_rule": "Store report evidence under project_evidence/; keep runtime source under leaf_qt/.",
        },
        "next_feature": "Legacy Evidence Ledger Gate",
    }


def build_text_report(ledger: dict[str, Any]) -> str:
    lines = [
        "LEAF LEGACY EVIDENCE LEDGER",
        "===========================",
        f"schema={ledger['schema']}",
        f"passed={ledger['passed']}",
        f"file_evidence_entries={ledger['summary']['file_evidence_entries']}",
        f"repository_snapshot_entries={ledger['summary']['repository_snapshot_entries']}",
        f"copied_files={ledger['summary']['copied_files']}",
        f"copy_files={ledger['summary']['copy_files']}",
        f"evidence_root={ledger['evidence_root']}",
        "",
        "CATEGORY COUNTS",
        "---------------",
    ]

    for key, value in ledger["summary"]["category_counts"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "REPOSITORY SNAPSHOTS", "--------------------"])
    for snapshot in ledger["repository_snapshots"]:
        lines.append(
            f"{snapshot['path']} | exists={snapshot['exists']} | "
            f"files={snapshot['file_count']} | py={snapshot['python_file_count']}"
        )

    lines.extend(["", "FILE EVIDENCE ENTRIES", "---------------------"])
    for entry in ledger["entries"][:250]:
        lines.append(
            f"{entry['category']} | {entry['source']} -> {entry['evidence_destination']}"
        )

    lines.extend(["", f"next_feature={ledger['next_feature']}"])
    return "\n".join(lines)


def write_legacy_evidence_ledger(root: str | Path = ".", copy_files: bool = False) -> dict[str, Any]:
    ledger = build_legacy_evidence_ledger(root=root, copy_files=copy_files)
    write_json_artifact(ledger, OUT_JSON)
    write_text_artifact(build_text_report(ledger), OUT_TXT)
    return ledger


if __name__ == "__main__":
    result = write_legacy_evidence_ledger(".", copy_files=False)
    print(build_text_report(result))
    print("")
    print(f"json={OUT_JSON}")
    print(f"txt={OUT_TXT}")
    print("PASS_LEGACY_EVIDENCE_LEDGER_DRY_RUN")
